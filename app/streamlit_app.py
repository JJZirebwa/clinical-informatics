from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clinical_informatics.metrics import build_metric_tables
from clinical_informatics.validation import run_validation_checks

DATA = ROOT / "data" / "synthetic"
OUTPUTS = ROOT / "outputs"


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False)


def load_data() -> dict[str, pd.DataFrame]:
    expected = {
        "sites": DATA / "sites.csv",
        "participants": DATA / "participants.csv",
        "visits": DATA / "visits.csv",
        "labs": DATA / "labs.csv",
        "adverse_events": DATA / "adverse_events.csv",
        "queries": DATA / "queries.csv",
        "protocol_deviations": DATA / "protocol_deviations.csv",
        "milestones": DATA / "milestones.csv",
        "site_metrics": OUTPUTS / "site_metrics.csv",
        "visit_adherence": OUTPUTS / "visit_adherence.csv",
        "query_metrics": OUTPUTS / "query_metrics.csv",
        "ae_summary": OUTPUTS / "ae_summary.csv",
        "missingness": OUTPUTS / "missingness.csv",
        "validation_flags": OUTPUTS / "validation_flags.csv",
        "validation_issues": OUTPUTS / "validation_issues.csv",
        "overview": OUTPUTS / "overview.csv",
    }
    missing = [str(path.relative_to(ROOT)) for path in expected.values() if not path.exists()]
    if missing:
        st.error("Generated files are missing. Run `python -m clinical_informatics.build_project` first.")
        st.code("\n".join(missing))
        st.stop()
    return {name: load_csv(path) for name, path in expected.items()}


RAW_TABLES = [
    "sites",
    "participants",
    "visits",
    "labs",
    "adverse_events",
    "queries",
    "protocol_deviations",
    "milestones",
]


def _ensure_raw_tables(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {name: data[name].copy() for name in RAW_TABLES}


def apply_filters(data: dict[str, pd.DataFrame], selected_sites: list[str], statuses: list[str], visits: list[str]) -> dict[str, pd.DataFrame]:
    filtered = _ensure_raw_tables(data)
    if selected_sites:
        filtered["sites"] = filtered["sites"][filtered["sites"]["site_id"].isin(selected_sites)]
        for name in ["participants", "visits", "labs", "adverse_events", "queries", "protocol_deviations", "milestones"]:
            if "site_id" in filtered[name].columns:
                filtered[name] = filtered[name][filtered[name]["site_id"].isin(selected_sites)]
    if statuses:
        filtered["participants"] = filtered["participants"][filtered["participants"]["participant_status"].isin(statuses)]
        keep_ids = set(filtered["participants"]["participant_id"])
        for name in ["visits", "labs", "adverse_events", "queries", "protocol_deviations"]:
            if "participant_id" in filtered[name].columns:
                filtered[name] = filtered[name][filtered[name]["participant_id"].isin(keep_ids)]
    if visits:
        filtered["visits"] = filtered["visits"][filtered["visits"]["visit_name"].isin(visits)]
        keep_visit_ids = set(filtered["visits"]["visit_id"])
        filtered["labs"] = filtered["labs"][filtered["labs"]["visit_id"].isin(keep_visit_ids)]
        filtered["protocol_deviations"] = filtered["protocol_deviations"][
            filtered["protocol_deviations"]["related_visit_id"].isin(keep_visit_ids)
            | (filtered["protocol_deviations"]["related_visit_id"].astype(str).str.strip() == "")
        ]
    return filtered


def derive_dashboard_tables(raw_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    validation = run_validation_checks(raw_tables)
    metrics = build_metric_tables(raw_tables, validation)
    return {**raw_tables, **metrics, "validation_issues": validation["issues"], "validation_summary": validation["summary"]}


def metric_cards(data: dict[str, pd.DataFrame]) -> None:
    participants = data["participants"]
    visits = data["visits"]
    queries = data["queries"]
    aes = data["adverse_events"]
    open_queries = queries[queries["status"].isin(["Open", "Answered"])]
    outside_window = pd.to_numeric(visits["days_from_window"], errors="coerce").fillna(0) > 0
    cols = st.columns(5)
    cols[0].metric("Participants", f"{len(participants):,}")
    cols[1].metric("Randomised", f"{(participants['randomization_date'].astype(str).str.strip() != '').sum():,}")
    cols[2].metric("Open queries", f"{len(open_queries):,}")
    cols[3].metric("Window misses", f"{int(outside_window.sum()):,}")
    cols[4].metric("SAEs", f"{int((aes['seriousness'] == 'Serious').sum()):,}")


def main() -> None:
    st.set_page_config(page_title="Clinical Informatics Demo", layout="wide")
    st.title("Clinical Informatics Trial Operations Demo")
    st.caption("Synthetic protocol-to-data mapping, validation checks, operational metrics, and dashboard views.")

    data = load_data()
    site_options = sorted(data["sites"]["site_id"].unique())
    status_options = sorted(data["participants"]["participant_status"].unique())
    visit_options = sorted(data["visits"]["visit_name"].unique())

    with st.sidebar:
        st.header("Filters")
        selected_sites = st.multiselect("Site", site_options, default=site_options)
        statuses = st.multiselect("Participant status", status_options, default=status_options)
        selected_visits = st.multiselect("Visit", visit_options, default=visit_options)
        st.divider()
        st.caption("All records are synthetic. This dashboard is a portfolio demonstration.")

    filtered = derive_dashboard_tables(apply_filters(data, selected_sites, statuses, selected_visits))
    metric_cards(filtered)

    tabs = st.tabs(["Overview", "Sites", "Visits", "Queries", "Safety", "Validation"])

    with tabs[0]:
        left, right = st.columns([1.1, 1])
        with left:
            st.subheader("Site Enrollment Progress")
            fig = px.bar(
                filtered["site_metrics"],
                x="site_id",
                y="enrolled_n",
                color="visit_window_miss_rate",
                hover_data=["site_name", "target_enrollment", "open_query_n", "validation_issue_n"],
                color_continuous_scale="Tealrose",
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.subheader("Operational Notes")
            st.info(
                "Use enrollment, visit-window misses, query ageing, and validation flags together. A site with strong enrollment can still need data-cleaning attention."
            )
            st.dataframe(filtered["site_metrics"], use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Site-Level Metrics")
        st.dataframe(filtered["site_metrics"], use_container_width=True, hide_index=True)
        fig = px.scatter(
            filtered["site_metrics"],
            x="enrollment_to_target_rate",
            y="open_query_n",
            size="validation_issue_n",
            color="region",
            hover_name="site_name",
            labels={
                "enrollment_to_target_rate": "Enrollment to target",
                "open_query_n": "Open or answered queries",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.subheader("Visit Adherence")
        visit_summary = (
            filtered["visit_adherence"].groupby("visit_name", as_index=False)[["scheduled_n", "outside_window_n", "missed_n", "pending_n"]].sum()
        )
        fig = px.bar(
            visit_summary,
            y="visit_name",
            x=["outside_window_n", "missed_n", "pending_n"],
            orientation="h",
            barmode="group",
            labels={"value": "Visit count", "visit_name": "Visit"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(filtered["visit_adherence"], use_container_width=True, hide_index=True)

    with tabs[3]:
        st.subheader("Query Burden and Ageing")
        fig = px.bar(
            filtered["query_metrics"],
            x="site_id",
            y="open_query_n",
            color="median_query_age_days",
            hover_data=["query_n", "high_severity_n"],
            color_continuous_scale="Oranges",
        )
        st.plotly_chart(fig, use_container_width=True)
        aged = filtered["queries"][filtered["queries"]["status"].isin(["Open", "Answered"])].sort_values(
            "age_days", ascending=False
        )
        st.dataframe(aged.head(50), use_container_width=True, hide_index=True)

    with tabs[4]:
        st.subheader("Adverse Event Summary")
        fig = px.bar(
            filtered["ae_summary"],
            x="site_id",
            y="ae_n",
            color="seriousness",
            facet_col="severity",
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(filtered["adverse_events"], use_container_width=True, hide_index=True)

    with tabs[5]:
        st.subheader("Validation and Missingness")
        st.warning(
            "Validation flags are prompts for analyst review. They are not medical adjudications or sponsor SOP decisions."
        )
        st.dataframe(filtered["validation_flags"], use_container_width=True, hide_index=True)
        high_missing = filtered["missingness"].sort_values("missing_pct", ascending=False).head(25)
        fig = px.bar(high_missing, x="missing_pct", y="column_name", color="table_name", orientation="h")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(filtered["validation_issues"].head(100), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
