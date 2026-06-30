"""Relational-data practice script for the synthetic clinical informatics project.

Run after `python -m clinical_informatics.build_project`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUT = ROOT / "outputs"


def read_table(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", keep_default_na=False)


def main() -> None:
    participants = read_table("participants")
    sites = read_table("sites")
    visits = read_table("visits")
    labs = read_table("labs")
    queries = read_table("queries")
    adverse_events = read_table("adverse_events")

    enrolled = participants[participants["randomization_date"].astype(str).str.strip() != ""]
    enrollment_by_site = (
        enrolled.merge(sites[["site_id", "site_name", "target_enrollment"]], on="site_id", how="left")
        .groupby(["site_id", "site_name", "target_enrollment"], as_index=False)
        .agg(enrolled_n=("participant_id", "nunique"))
    )
    enrollment_by_site["target_rate"] = enrollment_by_site["enrolled_n"] / enrollment_by_site["target_enrollment"]

    visits_with_participant = visits.merge(
        participants[["participant_id", "participant_status", "treatment_arm"]], on="participant_id", how="left"
    )
    visits_with_participant["outside_window"] = pd.to_numeric(
        visits_with_participant["days_from_window"], errors="coerce"
    ).fillna(0) > 0
    visit_adherence = (
        visits_with_participant.groupby(["visit_name", "participant_status"], as_index=False)
        .agg(
            scheduled_n=("visit_id", "count"),
            completed_n=("visit_status", lambda s: int(s.isin(["Completed", "Late", "Early"]).sum())),
            outside_window_n=("outside_window", "sum"),
        )
        .sort_values(["visit_name", "participant_status"])
    )

    lab_missingness = (
        labs.assign(result_missing=labs["result_value"].astype(str).str.strip() == "")
        .groupby(["visit_id", "test_name"], as_index=False)
        .agg(result_missing_n=("result_missing", "sum"), lab_n=("lab_id", "count"))
    )
    lab_missingness["missing_rate"] = lab_missingness["result_missing_n"] / lab_missingness["lab_n"]

    aged_queries = queries[queries["status"].isin(["Open", "Answered"])].copy()
    aged_queries["age_days"] = pd.to_numeric(aged_queries["age_days"], errors="coerce").fillna(0)
    query_ageing = (
        aged_queries.groupby(["site_id", "severity"], as_index=False)
        .agg(open_query_n=("query_id", "count"), median_age_days=("age_days", "median"), max_age_days=("age_days", "max"))
        .sort_values(["site_id", "severity"])
    )

    ae_summary = (
        adverse_events.groupby(["site_id", "seriousness", "severity"], as_index=False)
        .agg(ae_n=("ae_id", "count"), open_follow_up_n=("follow_up_status", lambda s: int((s == "Open").sum())))
        .sort_values(["site_id", "seriousness", "severity"])
    )

    OUT.mkdir(exist_ok=True)
    enrollment_by_site.to_csv(OUT / "relational_practice_enrollment_by_site.csv", index=False)
    visit_adherence.to_csv(OUT / "relational_practice_visit_adherence.csv", index=False)
    lab_missingness.to_csv(OUT / "relational_practice_lab_missingness.csv", index=False)
    query_ageing.to_csv(OUT / "relational_practice_query_ageing.csv", index=False)
    ae_summary.to_csv(OUT / "relational_practice_ae_summary.csv", index=False)

    interpretation = [
        "# Relational Data Practice Interpretation",
        "",
        "This script demonstrates joins and aggregations across synthetic study tables.",
        "",
        "## Checks Demonstrated",
        "",
        "- Site enrollment uses `participants` joined to `sites`.",
        "- Visit adherence uses `visits` joined to participant status.",
        "- Lab missingness groups lab results by visit and test.",
        "- Query ageing groups open and answered queries by site and severity.",
        "- AE summary groups events by site, seriousness, severity, and follow-up status.",
        "",
        "## Why These Checks Matter",
        "",
        "Clinical operations dashboards need traceable data products: a high-level metric should be explainable by record-level tables.",
    ]
    (OUT / "relational_data_practice_interpretation.md").write_text("\n".join(interpretation), encoding="utf-8")
    print("Relational practice outputs written to outputs/.")


if __name__ == "__main__":
    main()

