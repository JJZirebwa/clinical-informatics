from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .config import CRITICAL_LAB_FIELDS, CRITICAL_PARTICIPANT_FIELDS, CRITICAL_VISIT_FIELDS


CHECK_REGISTRY = {
    "participant_site_integrity": "Every participant references an existing site.",
    "visit_participant_integrity": "Every visit references an existing participant.",
    "lab_visit_integrity": "Every lab references an existing visit.",
    "duplicate_participants": "Participant identifiers are unique.",
    "duplicate_visits": "Participant and visit name combinations are unique.",
    "randomization_after_screening": "Randomisation occurs after screening for randomized participants.",
    "critical_field_completeness": "Critical fields are populated in participant, visit, and lab tables.",
    "visit_window_adherence": "Actual visit dates are inside the protocol visit window.",
    "lab_plausibility": "Lab values are present and inside broad plausible limits.",
    "query_ageing": "Open or answered queries older than 14 days are visible.",
    "ae_follow_up": "Serious or ongoing AEs have follow-up status visibility.",
    "milestone_timeliness": "Site milestones are not delayed beyond planned dates.",
}


def _blank_mask(series: pd.Series) -> pd.Series:
    return series.isna() | (series.astype(str).str.strip() == "")


def _append_issue(
    issues: list[dict[str, object]],
    check_id: str,
    severity: str,
    table_name: str,
    record_id: str,
    message: str,
    site_id: str = "",
    participant_id: str = "",
) -> None:
    issues.append(
        {
            "check_id": check_id,
            "severity": severity,
            "table_name": table_name,
            "record_id": record_id,
            "site_id": site_id,
            "participant_id": participant_id,
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
        missing = table[_blank_mask(table[field])]
        for row in missing.itertuples(index=False):
            _append_issue(
                issues,
                "critical_field_completeness",
                "High",
                table_name,
                str(getattr(row, record_column)),
                f"Critical field `{field}` is blank.",
                site_id=str(getattr(row, "site_id", "")),
                participant_id=str(getattr(row, "participant_id", "")),
            )


def run_validation_checks(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    issues: list[dict[str, object]] = []
    sites = tables["sites"]
    participants = tables["participants"]
    visits = tables["visits"]
    labs = tables["labs"]
    adverse_events = tables["adverse_events"]
    milestones = tables["milestones"]
    queries = tables["queries"]

    site_ids = set(sites["site_id"])
    participant_ids = set(participants["participant_id"])
    visit_ids = set(visits["visit_id"])

    for row in participants[~participants["site_id"].isin(site_ids)].itertuples(index=False):
        _append_issue(
            issues,
            "participant_site_integrity",
            "Critical",
            "participants",
            row.participant_id,
            "Participant references a site not present in sites.csv.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    for row in visits[~visits["participant_id"].isin(participant_ids)].itertuples(index=False):
        _append_issue(
            issues,
            "visit_participant_integrity",
            "Critical",
            "visits",
            row.visit_id,
            "Visit references a participant not present in participants.csv.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    for row in labs[~labs["visit_id"].isin(visit_ids)].itertuples(index=False):
        _append_issue(
            issues,
            "lab_visit_integrity",
            "Critical",
            "labs",
            row.lab_id,
            "Lab references a visit not present in visits.csv.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    for participant_id in participants[participants.duplicated("participant_id", keep=False)]["participant_id"].unique():
        _append_issue(issues, "duplicate_participants", "Critical", "participants", participant_id, "Duplicate participant_id.")

    duplicate_visit_rows = visits[visits.duplicated(["participant_id", "visit_name"], keep=False)]
    for row in duplicate_visit_rows.itertuples(index=False):
        _append_issue(
            issues,
            "duplicate_visits",
            "High",
            "visits",
            row.visit_id,
            "Duplicate participant visit name combination.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    randomized = participants[participants["randomization_date"].astype(str).str.strip() != ""].copy()
    randomized["screening_dt"] = pd.to_datetime(randomized["screening_date"], errors="coerce")
    randomized["randomization_dt"] = pd.to_datetime(randomized["randomization_date"], errors="coerce")
    for row in randomized[randomized["randomization_dt"] < randomized["screening_dt"]].itertuples(index=False):
        _append_issue(
            issues,
            "randomization_after_screening",
            "Critical",
            "participants",
            row.participant_id,
            "Randomisation date precedes screening date.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    _missing_field_issues(issues, participants, "participants", CRITICAL_PARTICIPANT_FIELDS, "participant_id")
    _missing_field_issues(issues, visits, "visits", CRITICAL_VISIT_FIELDS, "visit_id")
    _missing_field_issues(issues, labs, "labs", CRITICAL_LAB_FIELDS, "lab_id")

    outside_window = visits[pd.to_numeric(visits["days_from_window"], errors="coerce").fillna(0) > 0]
    for row in outside_window.itertuples(index=False):
        _append_issue(
            issues,
            "visit_window_adherence",
            "Medium" if not row.critical_visit else "High",
            "visits",
            row.visit_id,
            f"{row.visit_name} is {row.days_from_window} day(s) outside the protocol visit window.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    lab_problem = labs[labs["abnormal_flag"].isin(["Missing", "Implausible"])]
    for row in lab_problem.itertuples(index=False):
        _append_issue(
            issues,
            "lab_plausibility",
            "High" if row.abnormal_flag == "Implausible" else "Medium",
            "labs",
            row.lab_id,
            f"{row.test_name} result flagged as {row.abnormal_flag.lower()}.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    aged_queries = queries[(queries["status"].isin(["Open", "Answered"])) & (pd.to_numeric(queries["age_days"], errors="coerce") > 14)]
    for row in aged_queries.itertuples(index=False):
        _append_issue(
            issues,
            "query_ageing",
            "High" if row.severity == "High" else "Medium",
            "queries",
            row.query_id,
            f"{row.status} query aged {row.age_days} days.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    ae_follow_up = adverse_events[
        ((adverse_events["seriousness"] == "Serious") | (adverse_events["outcome"] == "Ongoing"))
        & (adverse_events["follow_up_status"] != "Complete")
    ]
    for row in ae_follow_up.itertuples(index=False):
        _append_issue(
            issues,
            "ae_follow_up",
            "High" if row.seriousness == "Serious" else "Medium",
            "adverse_events",
            row.ae_id,
            "AE follow-up remains open for a serious or ongoing event.",
            site_id=row.site_id,
            participant_id=row.participant_id,
        )

    delayed = milestones[milestones["status"] == "Delayed"]
    for row in delayed.itertuples(index=False):
        _append_issue(
            issues,
            "milestone_timeliness",
            "Medium",
            "milestones",
            row.milestone_id,
            f"{row.milestone_type} milestone is delayed.",
            site_id=row.site_id,
        )

    issue_columns = ["check_id", "severity", "table_name", "record_id", "site_id", "participant_id", "message"]
    issues_df = pd.DataFrame(issues, columns=issue_columns)
    summary_rows = []
    for check_id, description in CHECK_REGISTRY.items():
        check_issues = issues_df[issues_df["check_id"] == check_id] if not issues_df.empty else issues_df
        severity = "None" if check_issues.empty else "; ".join(sorted(check_issues["severity"].unique()))
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

