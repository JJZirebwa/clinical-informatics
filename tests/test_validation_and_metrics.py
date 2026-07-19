from __future__ import annotations

import pandas as pd
import pytest

from clinical_informatics.generate_synthetic_data import generate_all_tables
from clinical_informatics.metrics import build_metric_tables
from clinical_informatics.validation import run_validation_checks


def test_validation_checks_return_issue_and_summary_tables():
    tables = generate_all_tables(seed=21)
    validation = run_validation_checks(tables)

    assert {"issues", "summary"}.issubset(validation)
    assert {"check_id", "severity", "table_name", "record_id", "message"}.issubset(
        validation["issues"].columns
    )
    assert {"check_id", "severity", "issue_count", "status"}.issubset(
        validation["summary"].columns
    )
    assert validation["summary"]["check_id"].nunique() >= 8


def test_metric_tables_cover_dashboard_operational_views():
    tables = generate_all_tables(seed=31)
    validation = run_validation_checks(tables)
    metrics = build_metric_tables(tables, validation)

    assert {
        "overview",
        "site_metrics",
        "visit_adherence",
        "query_metrics",
        "ae_summary",
        "missingness",
        "validation_flags",
    }.issubset(metrics)
    assert {"site_id", "enrolled_n", "open_query_n", "visit_window_miss_rate"}.issubset(
        metrics["site_metrics"].columns
    )
    assert metrics["overview"].loc[0, "participant_n"] == len(tables["participants"])
    assert metrics["query_metrics"]["open_query_n"].sum() >= 0


@pytest.mark.parametrize(
    ("table_name", "field_name", "invalid_value", "check_id"),
    [
        ("participants", "site_id", "S999", "participant_site_integrity"),
        ("visits", "participant_id", "P-9999", "visit_participant_integrity"),
        ("visits", "site_id", "S999", "visit_site_integrity"),
        ("labs", "visit_id", "V-99999", "lab_visit_integrity"),
        ("labs", "participant_id", "P-9999", "lab_participant_integrity"),
        ("labs", "site_id", "S999", "lab_site_integrity"),
        ("adverse_events", "participant_id", "P-9999", "ae_participant_integrity"),
        ("adverse_events", "site_id", "S999", "ae_site_integrity"),
        ("queries", "participant_id", "P-9999", "query_participant_integrity"),
        ("queries", "site_id", "S999", "query_site_integrity"),
        (
            "protocol_deviations",
            "participant_id",
            "P-9999",
            "deviation_participant_integrity",
        ),
        ("protocol_deviations", "site_id", "S999", "deviation_site_integrity"),
        (
            "protocol_deviations",
            "related_visit_id",
            "V-99999",
            "deviation_visit_integrity",
        ),
        ("milestones", "site_id", "S999", "milestone_site_integrity"),
    ],
)
def test_broken_foreign_keys_create_record_level_issues(
    valid_tables, table_name, field_name, invalid_value, check_id
):
    valid_tables[table_name].loc[0, field_name] = invalid_value

    issues = run_validation_checks(valid_tables)["issues"]
    matching = issues[issues["check_id"] == check_id]

    assert len(matching) == 1
    assert matching.iloc[0]["record_id"]
    assert matching.iloc[0]["message"]


@pytest.mark.parametrize(
    ("table_name", "field_name", "mismatched_value", "check_id"),
    [
        ("visits", "site_id", "S002", "visit_participant_site_consistency"),
        ("labs", "participant_id", "P-0002", "lab_visit_participant_consistency"),
        ("labs", "site_id", "S002", "lab_visit_site_consistency"),
        (
            "adverse_events",
            "site_id",
            "S002",
            "ae_participant_site_consistency",
        ),
        ("queries", "site_id", "S002", "query_participant_site_consistency"),
        (
            "protocol_deviations",
            "participant_id",
            "P-0002",
            "deviation_visit_participant_consistency",
        ),
        (
            "protocol_deviations",
            "site_id",
            "S002",
            "deviation_visit_site_consistency",
        ),
    ],
)
def test_child_records_must_match_their_parent_context(
    valid_tables, table_name, field_name, mismatched_value, check_id
):
    valid_tables[table_name].loc[0, field_name] = mismatched_value

    issues = run_validation_checks(valid_tables)["issues"]

    assert check_id in set(issues["check_id"])


def test_consent_after_screening_is_flagged(valid_tables):
    valid_tables["participants"].loc[0, "consent_date"] = "2026-02-02"

    issues = run_validation_checks(valid_tables)["issues"]

    assert "consent_before_screening" in set(issues["check_id"])


def test_randomisation_before_screening_is_flagged(valid_tables):
    valid_tables["participants"].loc[0, "randomization_date"] = "2026-01-31"

    issues = run_validation_checks(valid_tables)["issues"]

    assert "randomization_timing" in set(issues["check_id"])


@pytest.mark.parametrize("age_years", [34, 76])
def test_out_of_range_age_is_flagged(valid_tables, age_years):
    valid_tables["participants"].loc[0, "age_years"] = age_years

    issues = run_validation_checks(valid_tables)["issues"]

    assert "age_eligibility" in set(issues["check_id"])


def test_missing_required_screening_or_baseline_hba1c_is_flagged(valid_tables):
    valid_tables["labs"] = valid_tables["labs"].loc[
        valid_tables["labs"]["participant_id"] != "P-0001"
    ]

    issues = run_validation_checks(valid_tables)["issues"]

    matching = issues[
        (issues["check_id"] == "required_hba1c_availability")
        & (issues["participant_id"] == "P-0001")
    ]
    assert len(matching) == 1


def test_completed_visit_outside_window_is_flagged(valid_tables):
    valid_tables["visits"].loc[0, "visit_status"] = "Late"
    valid_tables["visits"].loc[0, "actual_date"] = "2026-02-17"
    valid_tables["visits"].loc[0, "signed_delta_days"] = 16
    valid_tables["visits"].loc[0, "days_from_window"] = 2

    issues = run_validation_checks(valid_tables)["issues"]

    matching = issues[issues["check_id"] == "visit_window_adherence"]
    assert list(matching["record_id"]) == ["V-00001"]
    assert list(matching["severity"]) == ["High"]


@pytest.mark.parametrize("visit_status", ["Missed", "Pending"])
def test_unperformed_visit_is_not_treated_as_a_completed_window_breach(
    valid_tables, visit_status
):
    valid_tables["visits"].loc[0, "visit_status"] = visit_status
    valid_tables["visits"].loc[0, "actual_date"] = ""
    valid_tables["visits"].loc[0, "days_from_window"] = 99

    issues = run_validation_checks(valid_tables)["issues"]

    window_issues = issues[issues["check_id"] == "visit_window_adherence"]
    assert "V-00001" not in set(window_issues["record_id"])


def test_visit_window_miss_rate_uses_performed_visits_as_denominator(valid_tables):
    valid_tables["visits"].loc[0, ["visit_status", "days_from_window"]] = [
        "Late",
        2,
    ]
    valid_tables["visits"].loc[1, ["visit_status", "actual_date"]] = [
        "Pending",
        "",
    ]

    validation = run_validation_checks(valid_tables)
    metrics = build_metric_tables(valid_tables, validation)

    assert metrics["overview"].loc[0, "visit_window_miss_rate"] == 1.0


def test_missing_lab_result_is_only_flagged_for_a_completed_visit(valid_tables):
    valid_tables["labs"].loc[0, ["result_value", "abnormal_flag"]] = ["", "Missing"]
    valid_tables["visits"].loc[0, ["actual_date", "visit_status"]] = ["", "Pending"]

    pending_issues = run_validation_checks(valid_tables)["issues"]
    assert "L-00001" not in set(
        pending_issues.loc[
            pending_issues["check_id"] == "lab_result_completeness", "record_id"
        ]
    )

    valid_tables["visits"].loc[0, ["actual_date", "visit_status"]] = [
        "2026-02-01",
        "Completed",
    ]
    completed_issues = run_validation_checks(valid_tables)["issues"]
    assert "L-00001" in set(
        completed_issues.loc[
            completed_issues["check_id"] == "lab_result_completeness", "record_id"
        ]
    )


def test_only_aged_unresolved_queries_are_flagged(valid_tables):
    queries = valid_tables["queries"].iloc[[0]].copy()
    answered = queries.iloc[0].copy()
    answered[["query_id", "status", "age_days"]] = ["Q-0002", "Answered", 20]
    closed = queries.iloc[0].copy()
    closed[["query_id", "status", "age_days", "closed_date"]] = [
        "Q-0003",
        "Closed",
        200,
        "2026-06-26",
    ]
    valid_tables["queries"] = pd.DataFrame([queries.iloc[0], answered, closed])

    issues = run_validation_checks(valid_tables)["issues"]
    aged_ids = set(
        issues.loc[issues["check_id"] == "query_ageing", "record_id"]
    )

    assert aged_ids == {"Q-0002"}


def test_closed_queries_do_not_change_unresolved_query_age_metrics(valid_tables):
    rows = []
    for query_id, status, age_days in [
        ("Q-0001", "Open", 10),
        ("Q-0002", "Answered", 20),
        ("Q-0003", "Closed", 999),
    ]:
        row = valid_tables["queries"].iloc[0].copy()
        row[["query_id", "status", "age_days"]] = [query_id, status, age_days]
        if status == "Closed":
            row["severity"] = "High"
        rows.append(row)
    valid_tables["queries"] = pd.DataFrame(rows)

    validation = run_validation_checks(valid_tables)
    metrics = build_metric_tables(valid_tables, validation)

    assert metrics["overview"].loc[0, "open_query_n"] == 2
    assert metrics["overview"].loc[0, "median_open_query_age_days"] == 15
    assert metrics["site_metrics"].loc[
        metrics["site_metrics"]["site_id"] == "S001",
        "median_open_query_age_days",
    ].item() == 15
    assert metrics["query_metrics"].loc[
        metrics["query_metrics"]["site_id"] == "S001",
        "median_open_query_age_days",
    ].item() == 15
    assert metrics["query_metrics"].loc[
        metrics["query_metrics"]["site_id"] == "S001",
        "high_severity_open_query_n",
    ].item() == 0


def test_empty_unresolved_query_subset_returns_zero_age(valid_tables):
    valid_tables["queries"]["status"] = "Closed"

    validation = run_validation_checks(valid_tables)
    metrics = build_metric_tables(valid_tables, validation)

    assert metrics["overview"].loc[0, "open_query_n"] == 0
    assert metrics["overview"].loc[0, "median_open_query_age_days"] == 0.0
    assert metrics["query_metrics"].loc[0, "median_open_query_age_days"] == 0.0


def test_serious_or_ongoing_adverse_events_need_coherent_follow_up(valid_tables):
    serious = valid_tables["adverse_events"].iloc[0].copy()
    serious[
        [
            "ae_id",
            "seriousness",
            "outcome",
            "follow_up_required",
            "follow_up_status",
        ]
    ] = ["AE-0002", "Serious", "Resolved", True, "Open"]
    ongoing = valid_tables["adverse_events"].iloc[0].copy()
    ongoing[
        [
            "ae_id",
            "seriousness",
            "outcome",
            "resolution_date",
            "follow_up_required",
            "follow_up_status",
        ]
    ] = ["AE-0003", "Non-serious", "Ongoing", "", True, "Complete"]
    valid_tables["adverse_events"] = pd.DataFrame(
        [valid_tables["adverse_events"].iloc[0], serious, ongoing]
    )

    issues = run_validation_checks(valid_tables)["issues"]
    follow_up_ids = set(
        issues.loc[issues["check_id"] == "ae_follow_up", "record_id"]
    )

    assert follow_up_ids == {"AE-0002", "AE-0003"}


def test_milestone_delay_uses_documented_tolerance(valid_tables):
    valid_tables["milestones"].loc[0, "actual_date"] = "2026-01-09"
    valid_tables["milestones"].loc[0, "status"] = "Met"

    issues = run_validation_checks(valid_tables)["issues"]

    assert "M-0001" in set(
        issues.loc[issues["check_id"] == "milestone_timeliness", "record_id"]
    )
