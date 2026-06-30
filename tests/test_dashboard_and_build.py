from pathlib import Path

from app.streamlit_app import RAW_TABLES, apply_filters, derive_dashboard_tables, load_data
from clinical_informatics.build_project import build
from clinical_informatics.generate_synthetic_data import generate_all_tables


def test_dashboard_status_filter_recomputes_aggregate_metrics():
    raw_tables = generate_all_tables(seed=42)

    filtered_raw = apply_filters(raw_tables, selected_sites=[], statuses=["Screen Failed"], visits=[])
    dashboard = derive_dashboard_tables(filtered_raw)

    assert set(filtered_raw["participants"]["participant_status"]) == {"Screen Failed"}
    assert dashboard["overview"].loc[0, "participant_n"] == len(filtered_raw["participants"])
    assert dashboard["overview"].loc[0, "randomized_n"] == 0
    assert dashboard["site_metrics"]["enrolled_n"].sum() == 0
    assert dashboard["query_metrics"]["open_query_n"].sum() <= len(filtered_raw["queries"])
    assert dashboard["ae_summary"]["ae_n"].sum() == len(filtered_raw["adverse_events"])


def test_dashboard_loader_includes_all_raw_tables_used_by_filters():
    build(seed=42)

    data = load_data()
    assert set(RAW_TABLES).issubset(data)
    filtered_raw = apply_filters(data, selected_sites=[], statuses=[], visits=[])

    assert set(RAW_TABLES).issubset(filtered_raw)


def test_dashboard_site_filter_limits_validation_issues_to_selected_site():
    raw_tables = generate_all_tables(seed=42)

    filtered_raw = apply_filters(raw_tables, selected_sites=["S006"], statuses=[], visits=[])
    dashboard = derive_dashboard_tables(filtered_raw)
    nonblank_sites = set(
        dashboard["validation_issues"].loc[
            dashboard["validation_issues"]["site_id"].astype(str).str.strip() != "", "site_id"
        ]
    )

    assert nonblank_sites.issubset({"S006"})
    assert set(dashboard["site_metrics"]["site_id"]) == {"S006"}


def test_build_project_writes_documented_outputs():
    build(seed=42)
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
        path = Path(relative_path)
        assert path.exists(), relative_path
        assert path.stat().st_size > 0, relative_path
