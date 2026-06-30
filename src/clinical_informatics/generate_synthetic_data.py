from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from .config import LAB_REFERENCE, SYNTHETIC_DIR, TABLE_NAMES, VISIT_SCHEDULE, ensure_project_directories

DATA_CUT_DATE = pd.Timestamp("2026-06-30")


def _iso(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).date().isoformat()


def generate_sites() -> pd.DataFrame:
    rows = [
        ("S001", "Northgate Research Centre", "North England", "2026-01-08", 22, "Active"),
        ("S002", "Fenland Metabolic Unit", "East England", "2026-01-15", 18, "Active"),
        ("S003", "Severn Clinical Studies", "West England", "2026-01-29", 20, "Active"),
        ("S004", "Southbank Trials Clinic", "London", "2026-02-05", 24, "Active"),
        ("S005", "Clyde Health Research", "Scotland", "2026-02-11", 16, "Active"),
        ("S006", "Vale Primary Care Research", "Wales", "2026-02-20", 14, "Activation Hold"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "site_id",
            "site_name",
            "region",
            "activation_date",
            "target_enrollment",
            "site_status",
        ],
    )


def generate_participants(seed: int = 42, n: int = 126) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sites = generate_sites()
    site_ids = sites["site_id"].to_numpy()
    site_prob = np.array([0.18, 0.17, 0.18, 0.22, 0.15, 0.10])
    statuses = np.array(["Active", "Completed", "Discontinued", "Screen Failed"])
    status_prob = np.array([0.37, 0.34, 0.12, 0.17])
    start = pd.Timestamp(date(2026, 2, 1))
    rows: list[dict[str, object]] = []

    for index in range(1, n + 1):
        site_id = str(rng.choice(site_ids, p=site_prob))
        screening_date = start + timedelta(days=int(rng.integers(0, 95)))
        consent_date = screening_date - timedelta(days=int(rng.integers(0, 3)))
        status = str(rng.choice(statuses, p=status_prob))
        if status == "Screen Failed":
            randomization_date = pd.NaT
            treatment_arm = "Not randomized"
            discontinuation_reason = "Eligibility criteria not met"
        else:
            randomization_date = screening_date + timedelta(days=int(rng.integers(4, 18)))
            treatment_arm = str(rng.choice(["Arm A", "Arm B"]))
            discontinuation_reason = ""
            if status == "Discontinued":
                discontinuation_reason = str(
                    rng.choice(["Withdrawal", "Lost to follow-up", "Adverse event", "Protocol decision"])
                )

        rows.append(
            {
                "participant_id": f"P-{index:04d}",
                "site_id": site_id,
                "age_years": int(rng.integers(35, 76)),
                "sex": str(rng.choice(["Female", "Male"], p=[0.46, 0.54])),
                "screening_date": _iso(screening_date),
                "consent_date": _iso(consent_date),
                "randomization_date": _iso(randomization_date),
                "participant_status": status,
                "treatment_arm": treatment_arm,
                "baseline_hba1c": round(float(rng.normal(8.4, 1.0)), 1),
                "discontinuation_reason": discontinuation_reason,
                "source": "synthetic",
            }
        )

    return pd.DataFrame(rows)


def generate_visits(participants: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    rows: list[dict[str, object]] = []

    for participant in participants.itertuples(index=False):
        screening_date = pd.Timestamp(participant.screening_date)
        randomization_date = (
            pd.Timestamp(participant.randomization_date)
            if participant.randomization_date
            else screening_date + timedelta(days=14)
        )
        max_visit_count = 1 if participant.participant_status == "Screen Failed" else len(VISIT_SCHEDULE)
        if participant.participant_status == "Discontinued":
            max_visit_count = int(rng.choice([3, 4, 5], p=[0.35, 0.45, 0.20]))

        for visit_def in VISIT_SCHEDULE[:max_visit_count]:
            anchor = screening_date if visit_def.visit_name == "Screening" else randomization_date
            scheduled = anchor + timedelta(days=visit_def.day_offset if visit_def.visit_name != "Screening" else 0)
            miss_probability = 0.03 if visit_def.critical else 0.09
            pending_probability = 0.06 if scheduled > DATA_CUT_DATE - timedelta(days=20) else 0.01
            visit_draw = rng.random()

            if visit_draw < miss_probability:
                actual = pd.NaT
                status = "Missed"
                signed_delta = np.nan
            elif visit_draw < miss_probability + pending_probability:
                actual = pd.NaT
                status = "Pending"
                signed_delta = np.nan
            else:
                signed_delta = int(rng.normal(0, visit_def.window_days / 1.4))
                if rng.random() < 0.13:
                    signed_delta += int(rng.choice([-1, 1]) * rng.integers(visit_def.window_days + 1, visit_def.window_days + 11))
                actual = scheduled + timedelta(days=signed_delta)
                if abs(signed_delta) <= visit_def.window_days:
                    status = "Completed"
                elif signed_delta > visit_def.window_days:
                    status = "Late"
                else:
                    status = "Early"

            days_from_window = (
                max(int(abs(signed_delta) - visit_def.window_days), 0) if not pd.isna(signed_delta) else ""
            )
            rows.append(
                {
                    "visit_id": f"V-{len(rows) + 1:05d}",
                    "participant_id": participant.participant_id,
                    "site_id": participant.site_id,
                    "visit_name": visit_def.visit_name,
                    "scheduled_date": _iso(scheduled),
                    "actual_date": _iso(actual),
                    "window_days": visit_def.window_days,
                    "visit_status": status,
                    "signed_delta_days": "" if pd.isna(signed_delta) else int(signed_delta),
                    "days_from_window": days_from_window,
                    "critical_visit": visit_def.critical,
                    "assessments_expected": "; ".join(visit_def.assessments),
                    "source": "synthetic",
                }
            )

    return pd.DataFrame(rows)


def generate_labs(visits: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 2)
    rows: list[dict[str, object]] = []
    lab_visits = visits[visits["visit_name"].isin(["Screening", "Baseline / Randomisation", "Week 4", "Week 8", "Week 12 / End of Treatment"])]

    for visit in lab_visits.itertuples(index=False):
        collection_date = visit.actual_date or visit.scheduled_date
        for test_name, ref in LAB_REFERENCE.items():
            missing = visit.visit_status in {"Missed", "Pending"} or rng.random() < 0.035
            if missing:
                result_value = ""
                abnormal = "Missing"
            else:
                if test_name == "HbA1c":
                    value = float(rng.normal(8.1, 1.1))
                elif test_name == "ALT":
                    value = float(rng.lognormal(mean=3.25, sigma=0.45))
                else:
                    value = float(rng.normal(84, 22))
                if rng.random() < 0.01:
                    value = ref["plausible_high"] + float(rng.integers(20, 80))
                result_value = round(value, 1)
                if value < ref["plausible_low"] or value > ref["plausible_high"]:
                    abnormal = "Implausible"
                elif value < ref["low"]:
                    abnormal = "Low"
                elif value > ref["high"]:
                    abnormal = "High"
                else:
                    abnormal = "Normal"

            rows.append(
                {
                    "lab_id": f"L-{len(rows) + 1:05d}",
                    "participant_id": visit.participant_id,
                    "site_id": visit.site_id,
                    "visit_id": visit.visit_id,
                    "test_name": test_name,
                    "collection_date": collection_date,
                    "result_value": result_value,
                    "unit": ref["unit"],
                    "reference_low": ref["low"],
                    "reference_high": ref["high"],
                    "abnormal_flag": abnormal,
                    "source": "synthetic",
                }
            )

    return pd.DataFrame(rows)


def generate_adverse_events(participants: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 3)
    event_terms = ["Headache", "Nausea", "Hypoglycaemia", "Injection-site reaction", "Dizziness", "Elevated ALT"]
    rows: list[dict[str, object]] = []
    eligible = participants[participants["participant_status"] != "Screen Failed"]

    for participant in eligible.itertuples(index=False):
        event_count = int(rng.choice([0, 1, 2, 3], p=[0.48, 0.34, 0.14, 0.04]))
        randomization = pd.Timestamp(participant.randomization_date)
        for _ in range(event_count):
            onset = randomization + timedelta(days=int(rng.integers(1, 100)))
            serious = bool(rng.random() < 0.08)
            severity = str(rng.choice(["Mild", "Moderate", "Severe"], p=[0.52, 0.39, 0.09]))
            resolution_lag = int(rng.integers(1, 35))
            ongoing = rng.random() < (0.16 if not serious else 0.28)
            reported_lag = int(rng.integers(0, 5 if serious else 12))
            rows.append(
                {
                    "ae_id": f"AE-{len(rows) + 1:04d}",
                    "participant_id": participant.participant_id,
                    "site_id": participant.site_id,
                    "term": str(rng.choice(event_terms)),
                    "onset_date": _iso(onset),
                    "resolution_date": "" if ongoing else _iso(onset + timedelta(days=resolution_lag)),
                    "reported_date": _iso(onset + timedelta(days=reported_lag)),
                    "seriousness": "Serious" if serious else "Non-serious",
                    "severity": severity,
                    "relationship": str(rng.choice(["Unrelated", "Possible", "Probable"], p=[0.55, 0.35, 0.10])),
                    "action_taken": str(rng.choice(["None", "Dose interrupted", "Study drug withdrawn"], p=[0.72, 0.20, 0.08])),
                    "outcome": "Ongoing" if ongoing else str(rng.choice(["Resolved", "Recovering"], p=[0.82, 0.18])),
                    "follow_up_required": serious or severity == "Severe" or ongoing,
                    "follow_up_status": str(rng.choice(["Open", "Complete"], p=[0.36, 0.64])) if serious or ongoing else "Not required",
                    "source": "synthetic",
                }
            )

    return pd.DataFrame(rows)


def generate_protocol_deviations(participants: pd.DataFrame, visits: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 4)
    late_visits = visits[visits["visit_status"].isin(["Late", "Early", "Missed"])].sample(
        n=min(28, len(visits[visits["visit_status"].isin(["Late", "Early", "Missed"])])),
        random_state=seed,
    )
    rows: list[dict[str, object]] = []

    for visit in late_visits.itertuples(index=False):
        rows.append(
            {
                "deviation_id": f"PD-{len(rows) + 1:04d}",
                "participant_id": visit.participant_id,
                "site_id": visit.site_id,
                "related_visit_id": visit.visit_id,
                "deviation_date": visit.actual_date or visit.scheduled_date,
                "category": "Visit Window" if visit.visit_status != "Missed" else "Procedure",
                "impact": str(rng.choice(["Minor", "Major"], p=[0.72, 0.28])),
                "description": f"{visit.visit_name} recorded as {visit.visit_status.lower()}.",
                "action_taken": str(rng.choice(["Site retraining", "Monitor follow-up", "Documented rationale"])),
                "source": "synthetic",
            }
        )

    screen_failures = participants[participants["participant_status"] == "Screen Failed"].sample(
        n=min(6, (participants["participant_status"] == "Screen Failed").sum()),
        random_state=seed,
    )
    for participant in screen_failures.itertuples(index=False):
        rows.append(
            {
                "deviation_id": f"PD-{len(rows) + 1:04d}",
                "participant_id": participant.participant_id,
                "site_id": participant.site_id,
                "related_visit_id": "",
                "deviation_date": participant.screening_date,
                "category": "Eligibility",
                "impact": str(rng.choice(["Major", "Critical"], p=[0.85, 0.15])),
                "description": "Eligibility evidence required clarification before enrollment decision.",
                "action_taken": "Eligibility checklist review",
                "source": "synthetic",
            }
        )

    return pd.DataFrame(rows)


def generate_queries(
    participants: pd.DataFrame,
    visits: pd.DataFrame,
    labs: pd.DataFrame,
    adverse_events: pd.DataFrame,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 5)
    rows: list[dict[str, object]] = []

    candidates: list[dict[str, str]] = []
    for visit in visits[visits["visit_status"].isin(["Late", "Early", "Missed"])].sample(
        n=min(42, len(visits[visits["visit_status"].isin(["Late", "Early", "Missed"])])),
        random_state=seed,
    ).itertuples(index=False):
        candidates.append(
            {
                "site_id": visit.site_id,
                "participant_id": visit.participant_id,
                "table_name": "visits",
                "field_name": "actual_date",
                "record_id": visit.visit_id,
                "query_text": f"Confirm {visit.visit_name} timing and protocol-window rationale.",
            }
        )

    for lab in labs[labs["abnormal_flag"].isin(["Missing", "Implausible"])].sample(
        n=min(34, len(labs[labs["abnormal_flag"].isin(["Missing", "Implausible"])])),
        random_state=seed + 1,
    ).itertuples(index=False):
        candidates.append(
            {
                "site_id": lab.site_id,
                "participant_id": lab.participant_id,
                "table_name": "labs",
                "field_name": "result_value",
                "record_id": lab.lab_id,
                "query_text": f"Review {lab.test_name} result entry.",
            }
        )

    for ae in adverse_events[(adverse_events["seriousness"] == "Serious") | (adverse_events["follow_up_status"] == "Open")].itertuples(index=False):
        candidates.append(
            {
                "site_id": ae.site_id,
                "participant_id": ae.participant_id,
                "table_name": "adverse_events",
                "field_name": "follow_up_status",
                "record_id": ae.ae_id,
                "query_text": "Confirm AE follow-up and reconciliation status.",
            }
        )

    rng.shuffle(candidates)
    for candidate in candidates[:72]:
        opened = DATA_CUT_DATE - timedelta(days=int(rng.integers(1, 44)))
        status = str(rng.choice(["Open", "Answered", "Closed"], p=[0.46, 0.18, 0.36]))
        closed = ""
        if status == "Closed":
            closed_date = opened + timedelta(days=int(rng.integers(1, 14)))
            age_days = max((closed_date - opened).days, 0)
            closed = _iso(closed_date)
        else:
            age_days = (DATA_CUT_DATE - opened).days

        rows.append(
            {
                "query_id": f"Q-{len(rows) + 1:04d}",
                **candidate,
                "opened_date": _iso(opened),
                "closed_date": closed,
                "status": status,
                "age_days": int(age_days),
                "severity": str(rng.choice(["Low", "Medium", "High"], p=[0.38, 0.48, 0.14])),
                "source": "synthetic",
            }
        )

    return pd.DataFrame(rows)


def generate_milestones(sites: pd.DataFrame, participants: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 6)
    rows: list[dict[str, object]] = []
    for site in sites.itertuples(index=False):
        activation = pd.Timestamp(site.activation_date)
        site_participants = participants[participants["site_id"] == site.site_id]
        randomized = site_participants[site_participants["randomization_date"] != ""]
        first_in = pd.Timestamp(randomized["randomization_date"].min()) if len(randomized) else pd.NaT
        milestones = [
            ("Site Activation", activation - timedelta(days=3), activation),
            ("First Participant In", activation + timedelta(days=21), first_in),
            ("Enrollment Target", activation + timedelta(days=150), pd.NaT),
            ("Database Snapshot", DATA_CUT_DATE, DATA_CUT_DATE),
        ]
        for milestone_type, planned, actual in milestones:
            if pd.isna(actual):
                status = "Pending"
            elif pd.Timestamp(actual) > pd.Timestamp(planned) + timedelta(days=7):
                status = "Delayed"
            else:
                status = "Met"
            if milestone_type == "Enrollment Target" and len(randomized) >= int(site.target_enrollment):
                actual = DATA_CUT_DATE - timedelta(days=int(rng.integers(1, 20)))
                status = "Met"
            rows.append(
                {
                    "milestone_id": f"M-{len(rows) + 1:04d}",
                    "site_id": site.site_id,
                    "milestone_type": milestone_type,
                    "planned_date": _iso(pd.Timestamp(planned)),
                    "actual_date": _iso(actual),
                    "status": status,
                    "source": "synthetic",
                }
            )
    return pd.DataFrame(rows)


def generate_all_tables(seed: int = 42) -> dict[str, pd.DataFrame]:
    sites = generate_sites()
    participants = generate_participants(seed=seed)
    visits = generate_visits(participants, seed=seed)
    labs = generate_labs(visits, seed=seed)
    adverse_events = generate_adverse_events(participants, seed=seed)
    protocol_deviations = generate_protocol_deviations(participants, visits, seed=seed)
    queries = generate_queries(participants, visits, labs, adverse_events, seed=seed)
    milestones = generate_milestones(sites, participants, seed=seed)

    return {
        "sites": sites,
        "participants": participants,
        "visits": visits,
        "labs": labs,
        "adverse_events": adverse_events,
        "queries": queries,
        "protocol_deviations": protocol_deviations,
        "milestones": milestones,
    }


def write_tables(tables: dict[str, pd.DataFrame], output_dir= SYNTHETIC_DIR) -> None:
    ensure_project_directories()
    for table_name in TABLE_NAMES:
        tables[table_name].to_csv(output_dir / f"{table_name}.csv", index=False)


def load_tables(input_dir= SYNTHETIC_DIR) -> dict[str, pd.DataFrame]:
    return {table_name: pd.read_csv(input_dir / f"{table_name}.csv", keep_default_na=False) for table_name in TABLE_NAMES}

