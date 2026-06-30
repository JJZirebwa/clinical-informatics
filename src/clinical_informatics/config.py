from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

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


@dataclass(frozen=True)
class VisitDefinition:
    visit_name: str
    day_offset: int
    window_days: int
    critical: bool
    assessments: tuple[str, ...]


VISIT_SCHEDULE = [
    VisitDefinition("Screening", -14, 14, True, ("eligibility", "consent", "labs")),
    VisitDefinition("Baseline / Randomisation", 0, 3, True, ("randomization", "vitals", "labs")),
    VisitDefinition("Week 4", 28, 7, False, ("safety", "adherence", "labs")),
    VisitDefinition("Week 8", 56, 7, False, ("safety", "adherence", "labs")),
    VisitDefinition("Week 12 / End of Treatment", 84, 7, True, ("endpoint", "safety", "labs")),
    VisitDefinition("30-Day Safety Follow-up", 114, 10, True, ("safety_follow_up", "ae_review")),
]

CRITICAL_PARTICIPANT_FIELDS = [
    "participant_id",
    "site_id",
    "screening_date",
    "participant_status",
]

CRITICAL_VISIT_FIELDS = [
    "visit_id",
    "participant_id",
    "visit_name",
    "scheduled_date",
    "visit_status",
]

CRITICAL_LAB_FIELDS = ["lab_id", "participant_id", "visit_id", "test_name", "collection_date"]

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
        "screening_date": "Date of screening visit.",
        "consent_date": "Date informed consent was synthetically recorded.",
        "randomization_date": "Date randomized; blank for screen failures.",
        "participant_status": "Screen Failed, Active, Completed, or Discontinued.",
        "treatment_arm": "Synthetic blinded treatment assignment label.",
    },
    "visits": {
        "visit_id": "Synthetic visit identifier.",
        "participant_id": "Foreign key to participants.participant_id.",
        "visit_name": "Protocol visit label.",
        "scheduled_date": "Expected visit date from the synthetic schedule.",
        "actual_date": "Observed visit date; blank when missed or pending.",
        "visit_status": "Completed, Late, Early, Missed, or Pending.",
        "days_from_window": "Number of days outside the allowed visit window; zero when in window.",
    },
    "labs": {
        "lab_id": "Synthetic lab result identifier.",
        "visit_id": "Foreign key to visits.visit_id.",
        "test_name": "Synthetic lab test name.",
        "result_value": "Synthetic result value; blank where intentionally missing.",
        "unit": "Lab unit.",
        "abnormal_flag": "Low, Normal, High, Missing, or Implausible.",
    },
    "adverse_events": {
        "ae_id": "Synthetic adverse event identifier.",
        "participant_id": "Foreign key to participants.participant_id.",
        "onset_date": "Synthetic adverse event onset date.",
        "seriousness": "Non-serious or Serious.",
        "severity": "Mild, Moderate, or Severe.",
        "relationship": "Investigator-style causality category for demonstration.",
        "outcome": "Resolved, Recovering, Ongoing, or Unknown.",
    },
    "queries": {
        "query_id": "Synthetic EDC-style query identifier.",
        "table_name": "Table where the issue was observed.",
        "record_id": "Synthetic record identifier related to the query.",
        "status": "Open, Answered, or Closed.",
        "age_days": "Age in days for open or answered queries at data cut.",
    },
    "protocol_deviations": {
        "deviation_id": "Synthetic protocol deviation identifier.",
        "category": "Eligibility, Visit Window, Safety Reporting, or Procedure.",
        "impact": "Minor, Major, or Critical.",
        "action_taken": "Illustrative corrective or preventive action.",
    },
    "milestones": {
        "milestone_id": "Synthetic milestone identifier.",
        "milestone_type": "Activation, First Participant In, Enrollment Target, or Database Snapshot.",
        "planned_date": "Planned milestone date.",
        "actual_date": "Actual date; blank if not achieved.",
        "status": "Met, Delayed, or Pending.",
    },
}


def ensure_project_directories() -> None:
    for path in [DATA_DIR, SYNTHETIC_DIR, OUTPUT_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)

