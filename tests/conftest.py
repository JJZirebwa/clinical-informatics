from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def valid_tables() -> dict[str, pd.DataFrame]:
    """Return a small, internally consistent synthetic study snapshot."""
    return {
        "sites": pd.DataFrame(
            [
                {
                    "site_id": "S001",
                    "site_name": "Test Site One",
                    "region": "North England",
                    "activation_date": "2026-01-01",
                    "target_enrollment": 10,
                    "site_status": "Active",
                },
                {
                    "site_id": "S002",
                    "site_name": "Test Site Two",
                    "region": "South England",
                    "activation_date": "2026-01-02",
                    "target_enrollment": 8,
                    "site_status": "Active",
                },
            ]
        ),
        "participants": pd.DataFrame(
            [
                {
                    "participant_id": "P-0001",
                    "site_id": "S001",
                    "age_years": 55,
                    "sex": "Female",
                    "screening_date": "2026-02-01",
                    "consent_date": "2026-02-01",
                    "randomization_date": "2026-02-08",
                    "participant_status": "Active",
                    "treatment_arm": "Arm A",
                    "baseline_hba1c": 8.2,
                    "discontinuation_reason": "",
                    "source": "synthetic",
                },
                {
                    "participant_id": "P-0002",
                    "site_id": "S002",
                    "age_years": 62,
                    "sex": "Male",
                    "screening_date": "2026-02-03",
                    "consent_date": "2026-02-02",
                    "randomization_date": "2026-02-10",
                    "participant_status": "Completed",
                    "treatment_arm": "Arm B",
                    "baseline_hba1c": 7.9,
                    "discontinuation_reason": "",
                    "source": "synthetic",
                },
            ]
        ),
        "visits": pd.DataFrame(
            [
                {
                    "visit_id": "V-00001",
                    "participant_id": "P-0001",
                    "site_id": "S001",
                    "visit_name": "Screening",
                    "scheduled_date": "2026-02-01",
                    "actual_date": "2026-02-01",
                    "window_days": 14,
                    "visit_status": "Completed",
                    "signed_delta_days": 0,
                    "days_from_window": 0,
                    "critical_visit": True,
                    "assessments_expected": "eligibility; consent; labs",
                    "source": "synthetic",
                },
                {
                    "visit_id": "V-00002",
                    "participant_id": "P-0002",
                    "site_id": "S002",
                    "visit_name": "Screening",
                    "scheduled_date": "2026-02-03",
                    "actual_date": "2026-02-03",
                    "window_days": 14,
                    "visit_status": "Completed",
                    "signed_delta_days": 0,
                    "days_from_window": 0,
                    "critical_visit": True,
                    "assessments_expected": "eligibility; consent; labs",
                    "source": "synthetic",
                },
            ]
        ),
        "labs": pd.DataFrame(
            [
                {
                    "lab_id": "L-00001",
                    "participant_id": "P-0001",
                    "site_id": "S001",
                    "visit_id": "V-00001",
                    "test_name": "HbA1c",
                    "collection_date": "2026-02-01",
                    "result_value": "8.2",
                    "unit": "%",
                    "reference_low": 4.0,
                    "reference_high": 13.0,
                    "abnormal_flag": "Normal",
                    "source": "synthetic",
                },
                {
                    "lab_id": "L-00002",
                    "participant_id": "P-0002",
                    "site_id": "S002",
                    "visit_id": "V-00002",
                    "test_name": "HbA1c",
                    "collection_date": "2026-02-03",
                    "result_value": "7.9",
                    "unit": "%",
                    "reference_low": 4.0,
                    "reference_high": 13.0,
                    "abnormal_flag": "Normal",
                    "source": "synthetic",
                },
            ]
        ),
        "adverse_events": pd.DataFrame(
            [
                {
                    "ae_id": "AE-0001",
                    "participant_id": "P-0001",
                    "site_id": "S001",
                    "term": "Headache",
                    "onset_date": "2026-02-15",
                    "resolution_date": "2026-02-16",
                    "reported_date": "2026-02-15",
                    "seriousness": "Non-serious",
                    "severity": "Mild",
                    "relationship": "Unrelated",
                    "action_taken": "None",
                    "outcome": "Resolved",
                    "follow_up_required": False,
                    "follow_up_status": "Not required",
                    "source": "synthetic",
                }
            ]
        ),
        "queries": pd.DataFrame(
            [
                {
                    "query_id": "Q-0001",
                    "site_id": "S001",
                    "participant_id": "P-0001",
                    "table_name": "visits",
                    "field_name": "actual_date",
                    "record_id": "V-00001",
                    "query_text": "Confirm visit date.",
                    "opened_date": "2026-06-25",
                    "closed_date": "",
                    "status": "Open",
                    "age_days": 5,
                    "severity": "Low",
                    "source": "synthetic",
                }
            ]
        ),
        "protocol_deviations": pd.DataFrame(
            [
                {
                    "deviation_id": "PD-0001",
                    "participant_id": "P-0001",
                    "site_id": "S001",
                    "related_visit_id": "V-00001",
                    "deviation_date": "2026-02-01",
                    "category": "Procedure",
                    "impact": "Minor",
                    "description": "Synthetic test deviation.",
                    "action_taken": "Documented rationale",
                    "source": "synthetic",
                }
            ]
        ),
        "milestones": pd.DataFrame(
            [
                {
                    "milestone_id": "M-0001",
                    "site_id": "S001",
                    "milestone_type": "Site Activation",
                    "planned_date": "2026-01-01",
                    "actual_date": "2026-01-01",
                    "status": "Met",
                    "source": "synthetic",
                }
            ]
        ),
    }
