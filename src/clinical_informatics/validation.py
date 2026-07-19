from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta

import pandas as pd

from .config import (
    COMPLETED_VISIT_STATUSES,
    CRITICAL_LAB_FIELDS,
    CRITICAL_PARTICIPANT_FIELDS,
    CRITICAL_VISIT_FIELDS,
    DATA_CUT_DATE,
    MILESTONE_DELAY_TOLERANCE_DAYS,
    PRIMARY_KEYS,
    PROTOCOL_AGE_MAX_YEARS,
    PROTOCOL_AGE_MIN_YEARS,
    QUERY_AGE_THRESHOLD_DAYS,
    REQUIRED_HBA1C_VISITS,
    UNPERFORMED_VISIT_STATUSES,
    UNRESOLVED_QUERY_STATUSES,
)

CHECK_REGISTRY = {
    "primary_key_uniqueness": "Primary identifiers are unique within every table.",
    "participant_visit_uniqueness": "Each participant has at most one record for each scheduled visit.",
    "participant_site_integrity": "Every participant references an existing site.",
    "visit_participant_integrity": "Every visit references an existing participant.",
    "visit_site_integrity": "Every visit references an existing site.",
    "visit_participant_site_consistency": "Each visit uses the same site as its participant.",
    "lab_visit_integrity": "Every lab references an existing visit.",
    "lab_participant_integrity": "Every lab references an existing participant.",
    "lab_site_integrity": "Every lab references an existing site.",
    "lab_visit_participant_consistency": "Each lab uses the same participant as its visit.",
    "lab_visit_site_consistency": "Each lab uses the same site as its visit.",
    "lab_participant_site_consistency": "Each lab uses the same site as its participant.",
    "ae_participant_integrity": "Every adverse event references an existing participant.",
    "ae_site_integrity": "Every adverse event references an existing site.",
    "ae_participant_site_consistency": "Each adverse event uses the same site as its participant.",
    "query_participant_integrity": "Every query references an existing participant.",
    "query_site_integrity": "Every query references an existing site.",
    "query_participant_site_consistency": "Each query uses the same site as its participant.",
    "deviation_participant_integrity": "Every protocol deviation references an existing participant.",
    "deviation_site_integrity": "Every protocol deviation references an existing site.",
    "deviation_visit_integrity": "A supplied related visit references an existing visit.",
    "deviation_participant_site_consistency": "Each deviation uses the same site as its participant.",
    "deviation_visit_participant_consistency": "Each deviation uses the same participant as its related visit.",
    "deviation_visit_site_consistency": "Each deviation uses the same site as its related visit.",
    "milestone_site_integrity": "Every milestone references an existing site.",
    "screening_after_site_activation": "Screening occurs on or after site activation.",
    "age_eligibility": "Participant age is within the synthetic protocol range.",
    "consent_before_screening": "Consent occurs on or before screening.",
    "randomization_timing": "Randomisation is present when required and does not precede screening.",
    "required_hba1c_availability": "Randomised participants have a screening or baseline HbA1c result.",
    "critical_field_completeness": "Critical identifiers and operational fields are populated.",
    "visit_status_date_consistency": "Visit status and actual-date population are consistent.",
    "visit_window_adherence": "Performed visit dates are inside the protocol visit window.",
    "lab_result_completeness": "Expected lab results are present for performed visits.",
    "lab_result_plausibility": "Populated lab results are inside broad plausible limits.",
    "query_ageing": "Unresolved queries older than the operational threshold are visible.",
    "ae_follow_up": "Serious and ongoing adverse-event follow-up is operationally coherent.",
    "milestone_timeliness": "Site milestones use the documented delay tolerance.",
}

ISSUE_COLUMNS = [
    "check_id",
    "severity",
    "table_name",
    "record_id",
    "site_id",
    "participant_id",
    "message",
]


def _blank_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().isin({"", "nan", "NaT", "None"})


def _is_truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _append_issue(
    issues: list[dict[str, object]],
    check_id: str,
    severity: str,
    table_name: str,
    record_id: object,
    message: str,
    site_id: object = "",
    participant_id: object = "",
) -> None:
    issues.append(
        {
            "check_id": check_id,
            "severity": severity,
            "table_name": table_name,
            "record_id": str(record_id),
            "site_id": str(site_id),
            "participant_id": str(participant_id),
            "message": message,
        }
    )


def _missing_field_issues(
    issues: list[dict[str, object]],
    table: pd.DataFrame,
    table_name: str,
    fields: Iterable[str],
    record_column: str,
) -> None:
    for field in fields:
        if field not in table.columns:
            continue
        for row in table[_blank_mask(table[field])].itertuples(index=False):
            _append_issue(
                issues,
                "critical_field_completeness",
                "High",
                table_name,
                getattr(row, record_column),
                f"Critical field `{field}` is blank.",
                site_id=getattr(row, "site_id", ""),
                participant_id=getattr(row, "participant_id", ""),
            )


def _append_foreign_key_issues(
    issues: list[dict[str, object]],
    child: pd.DataFrame,
    child_table: str,
    record_column: str,
    foreign_key_column: str,
    parent_ids: set[object],
    check_id: str,
    parent_table: str,
    *,
    allow_blank: bool = False,
) -> None:
    foreign_key = child[foreign_key_column]
    invalid = ~foreign_key.isin(parent_ids)
    if allow_blank:
        invalid &= ~_blank_mask(foreign_key)
    for row in child[invalid].itertuples(index=False):
        _append_issue(
            issues,
            check_id,
            "Critical",
            child_table,
            getattr(row, record_column),
            f"`{foreign_key_column}` does not reference an existing record in {parent_table}.",
            site_id=getattr(row, "site_id", ""),
            participant_id=getattr(row, "participant_id", ""),
        )


def _lookup(frame: pd.DataFrame, key: str, value_columns: list[str]) -> dict[object, dict[str, object]]:
    unique = frame.drop_duplicates(key, keep="first")
    return unique.set_index(key)[value_columns].to_dict(orient="index")


def _check_primary_keys(
    issues: list[dict[str, object]], tables: dict[str, pd.DataFrame]
) -> None:
    for table_name, primary_key in PRIMARY_KEYS.items():
        frame = tables[table_name]
        duplicated = frame[frame.duplicated(primary_key, keep=False)]
        for value in duplicated[primary_key].drop_duplicates():
            _append_issue(
                issues,
                "primary_key_uniqueness",
                "Critical",
                table_name,
                value,
                f"Duplicate `{primary_key}` value.",
            )


def _check_referential_integrity(
    issues: list[dict[str, object]], tables: dict[str, pd.DataFrame]
) -> None:
    sites = tables["sites"]
    participants = tables["participants"]
    visits = tables["visits"]
    labs = tables["labs"]
    adverse_events = tables["adverse_events"]
    queries = tables["queries"]
    deviations = tables["protocol_deviations"]
    milestones = tables["milestones"]

    site_ids = set(sites["site_id"])
    participant_ids = set(participants["participant_id"])
    visit_ids = set(visits["visit_id"])

    relationships = [
        (
            participants,
            "participants",
            "participant_id",
            "site_id",
            site_ids,
            "participant_site_integrity",
            "sites",
            False,
        ),
        (
            visits,
            "visits",
            "visit_id",
            "participant_id",
            participant_ids,
            "visit_participant_integrity",
            "participants",
            False,
        ),
        (
            visits,
            "visits",
            "visit_id",
            "site_id",
            site_ids,
            "visit_site_integrity",
            "sites",
            False,
        ),
        (
            labs,
            "labs",
            "lab_id",
            "visit_id",
            visit_ids,
            "lab_visit_integrity",
            "visits",
            False,
        ),
        (
            labs,
            "labs",
            "lab_id",
            "participant_id",
            participant_ids,
            "lab_participant_integrity",
            "participants",
            False,
        ),
        (
            labs,
            "labs",
            "lab_id",
            "site_id",
            site_ids,
            "lab_site_integrity",
            "sites",
            False,
        ),
        (
            adverse_events,
            "adverse_events",
            "ae_id",
            "participant_id",
            participant_ids,
            "ae_participant_integrity",
            "participants",
            False,
        ),
        (
            adverse_events,
            "adverse_events",
            "ae_id",
            "site_id",
            site_ids,
            "ae_site_integrity",
            "sites",
            False,
        ),
        (
            queries,
            "queries",
            "query_id",
            "participant_id",
            participant_ids,
            "query_participant_integrity",
            "participants",
            False,
        ),
        (
            queries,
            "queries",
            "query_id",
            "site_id",
            site_ids,
            "query_site_integrity",
            "sites",
            False,
        ),
        (
            deviations,
            "protocol_deviations",
            "deviation_id",
            "participant_id",
            participant_ids,
            "deviation_participant_integrity",
            "participants",
            False,
        ),
        (
            deviations,
            "protocol_deviations",
            "deviation_id",
            "site_id",
            site_ids,
            "deviation_site_integrity",
            "sites",
            False,
        ),
        (
            deviations,
            "protocol_deviations",
            "deviation_id",
            "related_visit_id",
            visit_ids,
            "deviation_visit_integrity",
            "visits",
            True,
        ),
        (
            milestones,
            "milestones",
            "milestone_id",
            "site_id",
            site_ids,
            "milestone_site_integrity",
            "sites",
            False,
        ),
    ]
    for relationship in relationships:
        _append_foreign_key_issues(issues, *relationship[:-1], allow_blank=relationship[-1])

    participant_lookup = _lookup(participants, "participant_id", ["site_id", "screening_date"])
    visit_lookup = _lookup(visits, "visit_id", ["participant_id", "site_id", "visit_status", "critical_visit"])

    for row in visits.itertuples(index=False):
        parent = participant_lookup.get(row.participant_id)
        if parent and row.site_id != parent["site_id"]:
            _append_issue(
                issues,
                "visit_participant_site_consistency",
                "Critical",
                "visits",
                row.visit_id,
                "Visit site does not match the participant site.",
                row.site_id,
                row.participant_id,
            )

    for row in labs.itertuples(index=False):
        visit = visit_lookup.get(row.visit_id)
        participant = participant_lookup.get(row.participant_id)
        if visit and row.participant_id != visit["participant_id"]:
            _append_issue(
                issues,
                "lab_visit_participant_consistency",
                "Critical",
                "labs",
                row.lab_id,
                "Lab participant does not match the related visit participant.",
                row.site_id,
                row.participant_id,
            )
        if visit and row.site_id != visit["site_id"]:
            _append_issue(
                issues,
                "lab_visit_site_consistency",
                "Critical",
                "labs",
                row.lab_id,
                "Lab site does not match the related visit site.",
                row.site_id,
                row.participant_id,
            )
        if participant and row.site_id != participant["site_id"]:
            _append_issue(
                issues,
                "lab_participant_site_consistency",
                "Critical",
                "labs",
                row.lab_id,
                "Lab site does not match the participant site.",
                row.site_id,
                row.participant_id,
            )

    for table_name, frame, record_column, check_id in [
        (
            "adverse_events",
            adverse_events,
            "ae_id",
            "ae_participant_site_consistency",
        ),
        ("queries", queries, "query_id", "query_participant_site_consistency"),
        (
            "protocol_deviations",
            deviations,
            "deviation_id",
            "deviation_participant_site_consistency",
        ),
    ]:
        for row in frame.itertuples(index=False):
            participant = participant_lookup.get(row.participant_id)
            if participant and row.site_id != participant["site_id"]:
                _append_issue(
                    issues,
                    check_id,
                    "Critical",
                    table_name,
                    getattr(row, record_column),
                    f"{table_name.replace('_', ' ').title()} site does not match the participant site.",
                    row.site_id,
                    row.participant_id,
                )

    for row in deviations.itertuples(index=False):
        if not str(row.related_visit_id).strip():
            continue
        visit = visit_lookup.get(row.related_visit_id)
        if not visit:
            continue
        if row.participant_id != visit["participant_id"]:
            _append_issue(
                issues,
                "deviation_visit_participant_consistency",
                "Critical",
                "protocol_deviations",
                row.deviation_id,
                "Deviation participant does not match the related visit participant.",
                row.site_id,
                row.participant_id,
            )
        if row.site_id != visit["site_id"]:
            _append_issue(
                issues,
                "deviation_visit_site_consistency",
                "Critical",
                "protocol_deviations",
                row.deviation_id,
                "Deviation site does not match the related visit site.",
                row.site_id,
                row.participant_id,
            )


def _check_protocol_requirements(
    issues: list[dict[str, object]], tables: dict[str, pd.DataFrame]
) -> None:
    sites = tables["sites"]
    participants = tables["participants"]
    visits = tables["visits"]
    labs = tables["labs"]

    site_lookup = _lookup(sites, "site_id", ["activation_date"])
    for row in participants.itertuples(index=False):
        screening = pd.to_datetime(row.screening_date, errors="coerce")
        consent = pd.to_datetime(row.consent_date, errors="coerce")
        randomisation = pd.to_datetime(row.randomization_date, errors="coerce")
        age = pd.to_numeric(pd.Series([row.age_years]), errors="coerce").iloc[0]

        site = site_lookup.get(row.site_id)
        if site:
            activation = pd.to_datetime(site["activation_date"], errors="coerce")
            if pd.notna(screening) and pd.notna(activation) and screening < activation:
                _append_issue(
                    issues,
                    "screening_after_site_activation",
                    "Critical",
                    "participants",
                    row.participant_id,
                    "Screening date precedes site activation.",
                    row.site_id,
                    row.participant_id,
                )

        if pd.notna(age) and not (
            PROTOCOL_AGE_MIN_YEARS <= age <= PROTOCOL_AGE_MAX_YEARS
        ):
            _append_issue(
                issues,
                "age_eligibility",
                "Critical",
                "participants",
                row.participant_id,
                (
                    f"Age {int(age)} is outside the protocol range of "
                    f"{PROTOCOL_AGE_MIN_YEARS} to {PROTOCOL_AGE_MAX_YEARS} years."
                ),
                row.site_id,
                row.participant_id,
            )

        if pd.notna(consent) and pd.notna(screening) and consent > screening:
            _append_issue(
                issues,
                "consent_before_screening",
                "Critical",
                "participants",
                row.participant_id,
                "Consent date is after the screening date.",
                row.site_id,
                row.participant_id,
            )

        is_screen_failure = row.participant_status == "Screen Failed"
        has_randomisation = not _blank_mask(
            pd.Series([row.randomization_date])
        ).iloc[0]
        timing_problem = (
            (not is_screen_failure and not has_randomisation)
            or (is_screen_failure and has_randomisation)
            or (
                has_randomisation
                and pd.notna(screening)
                and pd.notna(randomisation)
                and randomisation < screening
            )
        )
        if timing_problem:
            if not has_randomisation:
                message = "Non-screen-failed participant has no randomisation date."
            elif is_screen_failure:
                message = "Screen-failed participant has a randomisation date."
            else:
                message = "Randomisation date precedes screening date."
            _append_issue(
                issues,
                "randomization_timing",
                "Critical",
                "participants",
                row.participant_id,
                message,
                row.site_id,
                row.participant_id,
            )

    randomised_ids = set(
        participants.loc[
            ~_blank_mask(participants["randomization_date"]), "participant_id"
        ]
    )
    required_visits = visits.loc[
        visits["visit_name"].isin(REQUIRED_HBA1C_VISITS),
        ["visit_id", "participant_id"],
    ]
    hba1c_labs = labs.loc[
        (labs["test_name"] == "HbA1c") & ~_blank_mask(labs["result_value"]),
        ["visit_id"],
    ]
    available_hba1c_ids = set(
        required_visits.merge(hba1c_labs, on="visit_id", how="inner")[
            "participant_id"
        ]
    )
    participant_lookup = _lookup(participants, "participant_id", ["site_id"])
    for participant_id in sorted(randomised_ids - available_hba1c_ids):
        participant = participant_lookup[participant_id]
        _append_issue(
            issues,
            "required_hba1c_availability",
            "High",
            "participants",
            participant_id,
            "No populated HbA1c result is available at screening or baseline.",
            participant["site_id"],
            participant_id,
        )


def _check_operational_semantics(
    issues: list[dict[str, object]], tables: dict[str, pd.DataFrame]
) -> None:
    visits = tables["visits"]
    labs = tables["labs"]
    adverse_events = tables["adverse_events"]
    queries = tables["queries"]
    milestones = tables["milestones"]

    duplicate_visit_rows = visits[
        visits.duplicated(["participant_id", "visit_name"], keep=False)
    ]
    for row in duplicate_visit_rows.itertuples(index=False):
        _append_issue(
            issues,
            "participant_visit_uniqueness",
            "High",
            "visits",
            row.visit_id,
            "Participant has more than one record for this visit name.",
            row.site_id,
            row.participant_id,
        )

    _missing_field_issues(
        issues,
        tables["participants"],
        "participants",
        CRITICAL_PARTICIPANT_FIELDS,
        "participant_id",
    )
    _missing_field_issues(
        issues, visits, "visits", CRITICAL_VISIT_FIELDS, "visit_id"
    )
    _missing_field_issues(issues, labs, "labs", CRITICAL_LAB_FIELDS, "lab_id")

    completed_mask = visits["visit_status"].isin(COMPLETED_VISIT_STATUSES)
    actual_blank = _blank_mask(visits["actual_date"])
    for row in visits[completed_mask & actual_blank].itertuples(index=False):
        _append_issue(
            issues,
            "visit_status_date_consistency",
            "High" if _is_truthy(row.critical_visit) else "Medium",
            "visits",
            row.visit_id,
            "Performed visit status has no actual date.",
            row.site_id,
            row.participant_id,
        )
    for row in visits[
        visits["visit_status"].isin(UNPERFORMED_VISIT_STATUSES) & ~actual_blank
    ].itertuples(index=False):
        _append_issue(
            issues,
            "visit_status_date_consistency",
            "High",
            "visits",
            row.visit_id,
            "Missed or pending visit has an actual date.",
            row.site_id,
            row.participant_id,
        )

    days_outside = pd.to_numeric(visits["days_from_window"], errors="coerce")
    for row in visits[completed_mask & (days_outside > 0)].itertuples(index=False):
        day_count = int(row.days_from_window)
        day_label = "day" if day_count == 1 else "days"
        _append_issue(
            issues,
            "visit_window_adherence",
            "High" if _is_truthy(row.critical_visit) else "Medium",
            "visits",
            row.visit_id,
            f"{row.visit_name} is {day_count} {day_label} outside the protocol visit window.",
            row.site_id,
            row.participant_id,
        )

    visit_lookup = _lookup(
        visits, "visit_id", ["visit_status", "critical_visit"]
    )
    for row in labs.itertuples(index=False):
        visit = visit_lookup.get(row.visit_id)
        if (
            row.abnormal_flag == "Missing"
            and visit
            and visit["visit_status"] in COMPLETED_VISIT_STATUSES
        ):
            _append_issue(
                issues,
                "lab_result_completeness",
                "High" if _is_truthy(visit["critical_visit"]) else "Medium",
                "labs",
                row.lab_id,
                f"{row.test_name} result is missing for a performed visit.",
                row.site_id,
                row.participant_id,
            )
        if row.abnormal_flag == "Implausible":
            _append_issue(
                issues,
                "lab_result_plausibility",
                "High",
                "labs",
                row.lab_id,
                f"{row.test_name} result is outside the broad synthetic plausibility range.",
                row.site_id,
                row.participant_id,
            )

    unresolved = queries["status"].isin(UNRESOLVED_QUERY_STATUSES)
    aged = pd.to_numeric(queries["age_days"], errors="coerce") > QUERY_AGE_THRESHOLD_DAYS
    for row in queries[unresolved & aged].itertuples(index=False):
        _append_issue(
            issues,
            "query_ageing",
            "High" if row.severity == "High" else "Medium",
            "queries",
            row.query_id,
            (
                f"{row.status} query has been unresolved for {int(row.age_days)} days, "
                f"above the {QUERY_AGE_THRESHOLD_DAYS}-day threshold."
            ),
            row.site_id,
            row.participant_id,
        )

    for row in adverse_events.itertuples(index=False):
        serious = row.seriousness == "Serious"
        ongoing = row.outcome == "Ongoing"
        follow_up_required = _is_truthy(row.follow_up_required)
        incomplete_serious = serious and row.follow_up_status != "Complete"
        incoherent_ongoing = ongoing
        if not (incomplete_serious or incoherent_ongoing or ((serious or ongoing) and not follow_up_required)):
            continue
        if ongoing:
            message = "Ongoing adverse event requires active follow-up and cannot be treated as complete."
        else:
            message = "Serious adverse-event follow-up is not complete."
        _append_issue(
            issues,
            "ae_follow_up",
            "High" if serious else "Medium",
            "adverse_events",
            row.ae_id,
            message,
            row.site_id,
            row.participant_id,
        )

    tolerance = timedelta(days=MILESTONE_DELAY_TOLERANCE_DAYS)
    for row in milestones.itertuples(index=False):
        planned = pd.to_datetime(row.planned_date, errors="coerce")
        actual = pd.to_datetime(row.actual_date, errors="coerce")
        delayed_actual = (
            pd.notna(planned) and pd.notna(actual) and actual > planned + tolerance
        )
        overdue_pending = (
            pd.notna(planned)
            and pd.isna(actual)
            and planned + tolerance < DATA_CUT_DATE
        )
        if delayed_actual or overdue_pending:
            delay_text = (
                f"more than {MILESTONE_DELAY_TOLERANCE_DAYS} days after plan"
                if delayed_actual
                else f"still pending beyond the {MILESTONE_DELAY_TOLERANCE_DAYS}-day tolerance"
            )
            _append_issue(
                issues,
                "milestone_timeliness",
                "Medium",
                "milestones",
                row.milestone_id,
                f"{row.milestone_type} milestone is {delay_text}.",
                row.site_id,
            )


def run_validation_checks(
    tables: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    issues: list[dict[str, object]] = []
    _check_primary_keys(issues, tables)
    _check_referential_integrity(issues, tables)
    _check_protocol_requirements(issues, tables)
    _check_operational_semantics(issues, tables)

    issues_df = pd.DataFrame(issues, columns=ISSUE_COLUMNS)
    summary_rows = []
    for check_id, description in CHECK_REGISTRY.items():
        check_issues = issues_df[issues_df["check_id"] == check_id]
        severity = (
            "None"
            if check_issues.empty
            else "; ".join(sorted(check_issues["severity"].unique()))
        )
        summary_rows.append(
            {
                "check_id": check_id,
                "description": description,
                "severity": severity,
                "issue_count": int(len(check_issues)),
                "status": "Pass" if check_issues.empty else "Review",
            }
        )

    return {"issues": issues_df, "summary": pd.DataFrame(summary_rows)}
