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

