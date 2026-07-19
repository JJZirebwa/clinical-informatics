import pandas as pd
from pandas.testing import assert_frame_equal

from clinical_informatics.generate_synthetic_data import DATA_CUT_DATE, generate_all_tables


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


def test_generation_is_deterministic_for_a_fixed_seed():
    first = generate_all_tables(seed=42)
    second = generate_all_tables(seed=42)

    for table_name in first:
        assert_frame_equal(first[table_name], second[table_name])


def test_generated_records_respect_site_activation_and_data_cut():
    tables = generate_all_tables(seed=42)
    participants = tables["participants"].merge(
        tables["sites"][["site_id", "activation_date"]], on="site_id", how="left"
    )

    assert (
        pd.to_datetime(participants["screening_date"])
        >= pd.to_datetime(participants["activation_date"])
    ).all()

    visits_with_dates = tables["visits"].loc[
        tables["visits"]["actual_date"].astype(str).str.strip() != ""
    ]
    assert (
        pd.to_datetime(visits_with_dates["actual_date"]) <= DATA_CUT_DATE
    ).all()

    for date_column in ["onset_date", "reported_date", "resolution_date"]:
        populated = tables["adverse_events"].loc[
            tables["adverse_events"][date_column].astype(str).str.strip() != "",
            date_column,
        ]
        assert (pd.to_datetime(populated) <= DATA_CUT_DATE).all()


def test_screening_and_randomisation_visits_match_participant_event_dates():
    tables = generate_all_tables(seed=42)
    participants = tables["participants"][
        ["participant_id", "screening_date", "randomization_date"]
    ]

    screening = tables["visits"].loc[
        tables["visits"]["visit_name"] == "Screening"
    ].merge(participants, on="participant_id", how="left")
    assert (
        pd.to_datetime(screening["actual_date"])
        == pd.to_datetime(screening["screening_date"])
    ).all()

    baseline = tables["visits"].loc[
        tables["visits"]["visit_name"] == "Baseline / Randomisation"
    ].merge(participants, on="participant_id", how="left")
    assert (
        pd.to_datetime(baseline["actual_date"])
        == pd.to_datetime(baseline["randomization_date"])
    ).all()
