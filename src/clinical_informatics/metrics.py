from __future__ import annotations

import pandas as pd


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator), 3)


def build_metric_tables(
    tables: dict[str, pd.DataFrame], validation: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    sites = tables["sites"]
    participants = tables["participants"]
    visits = tables["visits"]
    adverse_events = tables["adverse_events"]
    queries = tables["queries"]
    deviations = tables["protocol_deviations"]
    validation_issues = validation["issues"]

    randomized = participants[participants["randomization_date"].astype(str).str.strip() != ""]
    completed_visits = visits[visits["visit_status"].isin(["Completed", "Late", "Early"])]
    window_misses = visits[pd.to_numeric(visits["days_from_window"], errors="coerce").fillna(0) > 0]
    open_queries = queries[queries["status"].isin(["Open", "Answered"])]

    overview = pd.DataFrame(
        [
            {
                "participant_n": int(len(participants)),
                "randomized_n": int(len(randomized)),
                "site_n": int(len(sites)),
                "active_n": int((participants["participant_status"] == "Active").sum()),
                "completed_n": int((participants["participant_status"] == "Completed").sum()),
                "screen_failed_n": int((participants["participant_status"] == "Screen Failed").sum()),
                "visit_completion_rate": _safe_rate(len(completed_visits), len(visits)),
                "visit_window_miss_rate": _safe_rate(len(window_misses), len(visits)),
                "open_query_n": int(len(open_queries)),
                "median_query_age_days": float(pd.to_numeric(open_queries["age_days"], errors="coerce").median())
                if len(open_queries)
                else 0.0,
                "ae_n": int(len(adverse_events)),
                "sae_n": int((adverse_events["seriousness"] == "Serious").sum()),
                "validation_issue_n": int(len(validation_issues)),
                "high_severity_issue_n": int(validation_issues["severity"].isin(["High", "Critical"]).sum())
                if not validation_issues.empty
                else 0,
            }
        ]
    )

    site_rows = []
    for site in sites.itertuples(index=False):
        site_participants = participants[participants["site_id"] == site.site_id]
        site_visits = visits[visits["site_id"] == site.site_id]
        site_queries = queries[queries["site_id"] == site.site_id]
        site_open_queries = site_queries[site_queries["status"].isin(["Open", "Answered"])]
        site_window_misses = site_visits[pd.to_numeric(site_visits["days_from_window"], errors="coerce").fillna(0) > 0]
        site_validation = (
            validation_issues[validation_issues["site_id"] == site.site_id] if not validation_issues.empty else validation_issues
        )
        enrolled = int((site_participants["randomization_date"].astype(str).str.strip() != "").sum())
        site_rows.append(
            {
                "site_id": site.site_id,
                "site_name": site.site_name,
                "region": site.region,
                "target_enrollment": int(site.target_enrollment),
                "screened_n": int(len(site_participants)),
                "enrolled_n": enrolled,
                "enrollment_to_target_rate": _safe_rate(enrolled, int(site.target_enrollment)),
                "completed_n": int((site_participants["participant_status"] == "Completed").sum()),
                "discontinued_n": int((site_participants["participant_status"] == "Discontinued").sum()),
                "open_query_n": int(len(site_open_queries)),
                "median_open_query_age_days": float(pd.to_numeric(site_open_queries["age_days"], errors="coerce").median())
                if len(site_open_queries)
                else 0.0,
                "visit_window_miss_rate": _safe_rate(len(site_window_misses), len(site_visits)),
                "ae_n": int((adverse_events["site_id"] == site.site_id).sum()),
                "deviation_n": int((deviations["site_id"] == site.site_id).sum()),
                "validation_issue_n": int(len(site_validation)),
            }
        )
    site_metrics = pd.DataFrame(site_rows)

    visit_adherence = (
        visits.assign(outside_window=pd.to_numeric(visits["days_from_window"], errors="coerce").fillna(0) > 0)
        .groupby(["site_id", "visit_name"], as_index=False)
        .agg(
            scheduled_n=("visit_id", "count"),
            completed_n=("visit_status", lambda s: int(s.isin(["Completed", "Late", "Early"]).sum())),
            missed_n=("visit_status", lambda s: int((s == "Missed").sum())),
            pending_n=("visit_status", lambda s: int((s == "Pending").sum())),
            outside_window_n=("outside_window", "sum"),
        )
    )
    visit_adherence["completion_rate"] = visit_adherence.apply(
        lambda row: _safe_rate(row["completed_n"], row["scheduled_n"]), axis=1
    )
    visit_adherence["window_miss_rate"] = visit_adherence.apply(
        lambda row: _safe_rate(row["outside_window_n"], row["scheduled_n"]), axis=1
    )

    query_metrics = (
        queries.assign(is_open=queries["status"].isin(["Open", "Answered"]))
        .groupby("site_id", as_index=False)
        .agg(
            query_n=("query_id", "count"),
            open_query_n=("is_open", "sum"),
            median_query_age_days=("age_days", "median"),
            high_severity_n=("severity", lambda s: int((s == "High").sum())),
        )
    )

    ae_summary = (
        adverse_events.groupby(["site_id", "seriousness", "severity"], as_index=False)
        .agg(ae_n=("ae_id", "count"), open_follow_up_n=("follow_up_status", lambda s: int((s == "Open").sum())))
        .sort_values(["site_id", "seriousness", "severity"])
    )

    missingness_rows = []
    for table_name, frame in tables.items():
        for column in frame.columns:
            missing_n = int(frame[column].isna().sum() + (frame[column].astype(str).str.strip() == "").sum())
            missingness_rows.append(
                {
                    "table_name": table_name,
                    "column_name": column,
                    "missing_n": missing_n,
                    "row_n": int(len(frame)),
                    "missing_pct": _safe_rate(missing_n, len(frame)),
                }
            )
    missingness = pd.DataFrame(missingness_rows)

    validation_flags = validation["summary"].copy()
    validation_flags["dashboard_priority"] = validation_flags.apply(
        lambda row: "High" if row["status"] == "Review" and row["severity"] in {"High", "Critical", "Critical; High"} else row["status"],
        axis=1,
    )

    return {
        "overview": overview,
        "site_metrics": site_metrics,
        "visit_adherence": visit_adherence,
        "query_metrics": query_metrics,
        "ae_summary": ae_summary,
        "missingness": missingness,
        "validation_flags": validation_flags,
    }

