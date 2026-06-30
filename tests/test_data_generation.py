from clinical_informatics.generate_synthetic_data import generate_all_tables


def test_generate_all_tables_returns_expected_linked_tables():
    tables = generate_all_tables(seed=7)

    assert set(tables) == {
        "sites",
        "participants",
        "visits",
        "labs",
        "adverse_events",
        "queries",
        "protocol_deviations",
        "milestones",
    }
    assert len(tables["participants"]) >= 90
    assert len(tables["sites"]) >= 5
    assert set(tables["visits"]["participant_id"]).issubset(set(tables["participants"]["participant_id"]))
    assert set(tables["participants"]["site_id"]).issubset(set(tables["sites"]["site_id"]))


def test_synthetic_tables_have_core_operational_columns():
    tables = generate_all_tables(seed=11)

    assert {
        "participant_id",
        "site_id",
        "participant_status",
        "screening_date",
        "randomization_date",
        "treatment_arm",
    }.issubset(tables["participants"].columns)
    assert {
        "visit_id",
        "participant_id",
        "visit_name",
        "scheduled_date",
        "actual_date",
        "visit_status",
        "days_from_window",
    }.issubset(tables["visits"].columns)
    assert {"query_id", "table_name", "status", "age_days", "severity"}.issubset(
        tables["queries"].columns
    )

