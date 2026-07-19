from __future__ import annotations

import hashlib

import pandas as pd

from app.streamlit_app import (
    RAW_TABLES,
    apply_filters,
    derive_dashboard_tables,
    load_data,
    render_chart,
)
from clinical_informatics.build_project import build
from clinical_informatics.generate_synthetic_data import generate_all_tables


def test_dashboard_status_filter_recomputes_aggregate_metrics():
    raw_tables = generate_all_tables(seed=42)

    filtered_raw = apply_filters(
        raw_tables,
        selected_sites=None,
        statuses=["Screen Failed"],
        visits=None,
    )
    dashboard = derive_dashboard_tables(filtered_raw)

    assert set(filtered_raw["participants"]["participant_status"]) == {"Screen Failed"}
    assert dashboard["overview"].loc[0, "participant_n"] == len(filtered_raw["participants"])
    assert dashboard["overview"].loc[0, "randomized_n"] == 0
    assert dashboard["site_metrics"]["enrolled_n"].sum() == 0
    assert dashboard["query_metrics"]["open_query_n"].sum() <= len(filtered_raw["queries"])
    assert dashboard["ae_summary"]["ae_n"].sum() == len(filtered_raw["adverse_events"])


def test_dashboard_loader_includes_all_raw_tables_used_by_filters():
    data = load_data()
    assert set(RAW_TABLES).issubset(data)
    filtered_raw = apply_filters(
        data, selected_sites=None, statuses=None, visits=None
    )

    assert set(RAW_TABLES).issubset(filtered_raw)


def test_dashboard_site_filter_limits_validation_issues_to_selected_site():
    raw_tables = generate_all_tables(seed=42)

    filtered_raw = apply_filters(
        raw_tables, selected_sites=["S006"], statuses=None, visits=None
    )
    dashboard = derive_dashboard_tables(filtered_raw)
    nonblank_sites = set(
        dashboard["validation_issues"].loc[
            dashboard["validation_issues"]["site_id"].astype(str).str.strip() != "", "site_id"
        ]
    )

    assert nonblank_sites.issubset({"S006"})
    assert set(dashboard["site_metrics"]["site_id"]) == {"S006"}


def test_dashboard_filter_derivation_is_internally_consistent():
    raw_tables = generate_all_tables(seed=42)
    filtered_raw = apply_filters(
        raw_tables,
        selected_sites=["S001"],
        statuses=["Active"],
        visits=["Screening"],
    )

    dashboard = derive_dashboard_tables(filtered_raw)
    overview = dashboard["overview"].iloc[0]
    unresolved = dashboard["queries"]["status"].isin(["Open", "Answered"])

    assert overview["participant_n"] == len(dashboard["participants"])
    assert overview["open_query_n"] == int(unresolved.sum())
    assert dashboard["site_metrics"]["open_query_n"].sum() == int(unresolved.sum())
    assert dashboard["visit_adherence"]["scheduled_n"].sum() == len(
        dashboard["visits"]
    )
    assert set(dashboard["visits"]["visit_name"]) <= {"Screening"}


def test_empty_site_selection_produces_safe_empty_dashboard_tables():
    raw_tables = generate_all_tables(seed=42)

    filtered_raw = apply_filters(
        raw_tables, selected_sites=[], statuses=None, visits=None
    )
    dashboard = derive_dashboard_tables(filtered_raw)

    assert dashboard["sites"].empty
    assert dashboard["participants"].empty
    assert dashboard["overview"].loc[0, "participant_n"] == 0
    assert dashboard["site_metrics"].empty
    assert set(
        [
            "site_id",
            "enrolled_n",
            "open_query_n",
            "median_open_query_age_days",
        ]
    ).issubset(dashboard["site_metrics"].columns)


def test_empty_chart_data_renders_a_message_without_calling_plotly(monkeypatch):
    messages = []
    rendered = []
    monkeypatch.setattr("app.streamlit_app.st.info", messages.append)
    monkeypatch.setattr(
        "app.streamlit_app.st.plotly_chart",
        lambda *args, **kwargs: rendered.append((args, kwargs)),
    )

    render_chart(pd.DataFrame(), object(), "No matching data.")

    assert messages == ["No matching data."]
    assert rendered == []


def test_build_project_writes_documented_outputs_to_an_isolated_root(tmp_path):
    build_root = tmp_path / "build"
    build(seed=42, output_root=build_root)
    required = [
        "data/synthetic/participants.csv",
        "data/synthetic/visits.csv",
        "data/data_dictionary.md",
        "outputs/validation_report.md",
        "outputs/metrics_summary.md",
        "outputs/build_manifest.md",
        "outputs/figures/site_enrollment_progress.png",
        "outputs/figures/site_query_burden.png",
        "outputs/figures/visit_window_misses.png",
    ]

    for relative_path in required:
        path = build_root / relative_path
        assert path.exists(), relative_path
        assert path.stat().st_size > 0, relative_path


def test_full_build_is_byte_deterministic_for_a_fixed_seed(tmp_path):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"

    build(seed=42, output_root=first_root)
    build(seed=42, output_root=second_root)

    first_files = sorted(
        path.relative_to(first_root) for path in first_root.rglob("*") if path.is_file()
    )
    second_files = sorted(
        path.relative_to(second_root)
        for path in second_root.rglob("*")
        if path.is_file()
    )
    assert first_files == second_files

    for relative_path in first_files:
        first_hash = hashlib.sha256((first_root / relative_path).read_bytes()).hexdigest()
        second_hash = hashlib.sha256(
            (second_root / relative_path).read_bytes()
        ).hexdigest()
        assert first_hash == second_hash, relative_path
