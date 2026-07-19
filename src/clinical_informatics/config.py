from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
DATA_CUT_DATE = pd.Timestamp("2026-06-30")

PROTOCOL_AGE_MIN_YEARS = 35
PROTOCOL_AGE_MAX_YEARS = 75
QUERY_AGE_THRESHOLD_DAYS = 14
MILESTONE_DELAY_TOLERANCE_DAYS = 7

COMPLETED_VISIT_STATUSES = ("Completed", "Late", "Early")
UNPERFORMED_VISIT_STATUSES = ("Missed", "Pending")
UNRESOLVED_QUERY_STATUSES = ("Open", "Answered")
REQUIRED_HBA1C_VISITS = ("Screening", "Baseline / Randomisation")

TABLE_NAMES = [
    "sites",
    "participants",
    "visits",
    "labs",
    "adverse_events",
    "queries",
    "protocol_deviations",
    "milestones",
]

PRIMARY_KEYS = {
    "sites": "site_id",
    "participants": "participant_id",
    "visits": "visit_id",
    "labs": "lab_id",
    "adverse_events": "ae_id",
    "queries": "query_id",
    "protocol_deviations": "deviation_id",
    "milestones": "milestone_id",
}


@dataclass(frozen=True)
class VisitDefinition:
    visit_name: str
    day_offset: int
    window_days: int
    critical: bool
    assessments: tuple[str, ...]


VISIT_SCHEDULE = [
    VisitDefinition("Screening", -7, 7, True, ("eligibility", "consent", "labs")),
    VisitDefinition("Baseline / Randomisation", 0, 3, True, ("randomisation", "vitals", "labs")),
    VisitDefinition("Week 4", 28, 7, False, ("safety", "adherence", "labs")),
    VisitDefinition("Week 8", 56, 7, False, ("safety", "adherence", "labs")),
    VisitDefinition("Week 12 / End of Treatment", 84, 7, True, ("endpoint", "safety", "labs")),
    VisitDefinition("30-Day Safety Follow-up", 114, 10, True, ("safety_follow_up", "ae_review")),
]

CRITICAL_PARTICIPANT_FIELDS = [
    "participant_id",
    "site_id",
    "age_years",
    "screening_date",
    "consent_date",
    "participant_status",
]

CRITICAL_VISIT_FIELDS = [
    "visit_id",
    "participant_id",
    "site_id",
    "visit_name",
    "scheduled_date",
    "visit_status",
]

CRITICAL_LAB_FIELDS = ["lab_id", "participant_id", "site_id", "visit_id", "test_name"]

LAB_REFERENCE = {
    "HbA1c": {"unit": "%", "low": 4.0, "high": 13.0, "plausible_low": 3.5, "plausible_high": 16.0},
    "ALT": {"unit": "U/L", "low": 7.0, "high": 56.0, "plausible_low": 3.0, "plausible_high": 320.0},
    "Creatinine": {
        "unit": "umol/L",
        "low": 45.0,
        "high": 120.0,
        "plausible_low": 25.0,
        "plausible_high": 600.0,
    },
}

DATA_DICTIONARY = {
    "sites": {
        "site_id": "Synthetic site identifier.",
        "site_name": "Synthetic site display name.",
        "region": "Synthetic UK region grouping.",
        "activation_date": "Date the synthetic site became active.",
        "target_enrollment": "Illustrative participant recruitment target.",
        "site_status": "Operational site status.",
    },
    "participants": {
        "participant_id": "Synthetic participant identifier.",
        "site_id": "Foreign key to sites.site_id.",
        "age_years": "Age in years at screening.",
        "sex": "Synthetic sex category.",
        "screening_date": "Date of screening visit.",
        "consent_date": "Date informed consent was synthetically recorded.",
        "randomization_date": "Date randomised; blank for screen failures.",
        "participant_status": "Screen Failed, Active, Completed, or Discontinued.",
        "treatment_arm": "Synthetic blinded treatment assignment label.",
        "baseline_hba1c": "Synthetic HbA1c value used to populate the screening lab record.",
        "discontinuation_reason": "Synthetic reason; populated for discontinued participants.",
        "source": "Synthetic provenance marker.",
    },
    "visits": {
        "visit_id": "Synthetic visit identifier.",
        "participant_id": "Foreign key to participants.participant_id.",
        "site_id": "Foreign key to sites.site_id; expected to match the participant.",
        "visit_name": "Protocol visit label.",
        "scheduled_date": "Expected visit date from the synthetic schedule.",
        "actual_date": "Observed visit date; blank when missed or pending.",
        "window_days": "Allowed deviation in days either side of the scheduled date.",
        "visit_status": "Completed, Late, Early, Missed, or Pending.",
        "signed_delta_days": "Actual date minus scheduled date in days; blank when unperformed.",
        "days_from_window": "Number of days outside the allowed visit window; zero when in window.",
        "critical_visit": "Whether an out-of-window completed visit receives high severity.",
        "assessments_expected": "Semicolon-delimited assessments expected for the visit.",
        "source": "Synthetic provenance marker.",
    },
    "labs": {
        "lab_id": "Synthetic lab result identifier.",
        "participant_id": "Foreign key to participants.participant_id; expected to match the visit.",
        "site_id": "Foreign key to sites.site_id; expected to match the visit and participant.",
        "visit_id": "Foreign key to visits.visit_id.",
        "test_name": "Synthetic lab test name.",
        "collection_date": "Collection date; blank when the planned visit was not performed.",
        "result_value": "Synthetic result value; blank where intentionally missing.",
        "unit": "Lab unit.",
        "reference_low": "Illustrative lower reference limit.",
        "reference_high": "Illustrative upper reference limit.",
        "abnormal_flag": "Low, Normal, High, Missing, or Implausible.",
        "source": "Synthetic provenance marker.",
    },
    "adverse_events": {
        "ae_id": "Synthetic adverse event identifier.",
        "participant_id": "Foreign key to participants.participant_id.",
        "site_id": "Foreign key to sites.site_id; expected to match the participant.",
        "term": "Synthetic adverse event term.",
        "onset_date": "Synthetic adverse event onset date.",
        "resolution_date": "Resolution date; blank for ongoing events.",
        "reported_date": "Synthetic date the event was reported.",
        "seriousness": "Non-serious or Serious.",
        "severity": "Mild, Moderate, or Severe.",
        "relationship": "Investigator-style causality category for demonstration.",
        "action_taken": "Illustrative action following the event.",
        "outcome": "Resolved, Recovering, Ongoing, or Unknown.",
        "follow_up_required": "Whether follow-up is operationally required.",
        "follow_up_status": "Open, Complete, or Not required.",
        "source": "Synthetic provenance marker.",
    },
    "queries": {
        "query_id": "Synthetic EDC-style query identifier.",
        "site_id": "Foreign key to sites.site_id; expected to match the participant.",
        "participant_id": "Foreign key to participants.participant_id.",
        "table_name": "Table where the issue was observed.",
        "field_name": "Field where the query was raised.",
        "record_id": "Synthetic record identifier related to the query.",
        "query_text": "Synthetic query wording.",
        "opened_date": "Date the query was opened.",
        "closed_date": "Closure date; blank while unresolved.",
        "status": "Open, Answered, or Closed.",
        "age_days": "Age at data cut for unresolved queries; elapsed time to closure for closed queries.",
        "severity": "Illustrative Low, Medium, or High operational priority.",
        "source": "Synthetic provenance marker.",
    },
    "protocol_deviations": {
        "deviation_id": "Synthetic protocol deviation identifier.",
        "participant_id": "Foreign key to participants.participant_id.",
        "site_id": "Foreign key to sites.site_id; expected to match the participant and related visit.",
        "related_visit_id": "Optional foreign key to visits.visit_id.",
        "deviation_date": "Date of the synthetic deviation.",
        "category": "Eligibility, Visit Window, Safety Reporting, or Procedure.",
        "impact": "Minor, Major, or Critical.",
        "description": "Synthetic deviation description.",
        "action_taken": "Illustrative corrective or preventive action.",
        "source": "Synthetic provenance marker.",
    },
    "milestones": {
        "milestone_id": "Synthetic milestone identifier.",
        "site_id": "Foreign key to sites.site_id.",
        "milestone_type": "Activation, First Participant In, Enrolment Target, or Database Snapshot.",
        "planned_date": "Planned milestone date.",
        "actual_date": "Actual date; blank if not achieved.",
        "status": "Met, Delayed, or Pending.",
        "source": "Synthetic provenance marker.",
    },
}


def ensure_project_directories() -> None:
    for path in [DATA_DIR, SYNTHETIC_DIR, OUTPUT_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
