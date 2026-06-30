# Data Dictionary

All datasets in this repository are synthetic and created for demonstration. They do not contain real patient, site, sponsor, or EDC data.

## sites.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `site_id` | `object` | Synthetic site identifier. |
| `site_name` | `object` | Synthetic site display name. |
| `region` | `object` | Synthetic UK region grouping. |
| `activation_date` | `object` | Date the synthetic site became active. |
| `target_enrollment` | `int64` | Illustrative participant recruitment target. |
| `site_status` | `object` | Operational site status. |

## participants.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `participant_id` | `object` | Synthetic participant identifier. |
| `site_id` | `object` | Foreign key to sites.site_id. |
| `age_years` | `int64` | Synthetic demonstration field. |
| `sex` | `object` | Synthetic demonstration field. |
| `screening_date` | `object` | Date of screening visit. |
| `consent_date` | `object` | Date informed consent was synthetically recorded. |
| `randomization_date` | `object` | Date randomized; blank for screen failures. |
| `participant_status` | `object` | Screen Failed, Active, Completed, or Discontinued. |
| `treatment_arm` | `object` | Synthetic blinded treatment assignment label. |
| `baseline_hba1c` | `float64` | Synthetic demonstration field. |
| `discontinuation_reason` | `object` | Synthetic demonstration field. |
| `source` | `object` | Synthetic demonstration field. |

## visits.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `visit_id` | `object` | Synthetic visit identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `site_id` | `object` | Synthetic demonstration field. |
| `visit_name` | `object` | Protocol visit label. |
| `scheduled_date` | `object` | Expected visit date from the synthetic schedule. |
| `actual_date` | `object` | Observed visit date; blank when missed or pending. |
| `window_days` | `int64` | Synthetic demonstration field. |
| `visit_status` | `object` | Completed, Late, Early, Missed, or Pending. |
| `signed_delta_days` | `object` | Synthetic demonstration field. |
| `days_from_window` | `object` | Number of days outside the allowed visit window; zero when in window. |
| `critical_visit` | `bool` | Synthetic demonstration field. |
| `assessments_expected` | `object` | Synthetic demonstration field. |
| `source` | `object` | Synthetic demonstration field. |

## labs.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `lab_id` | `object` | Synthetic lab result identifier. |
| `participant_id` | `object` | Synthetic demonstration field. |
| `site_id` | `object` | Synthetic demonstration field. |
| `visit_id` | `object` | Foreign key to visits.visit_id. |
| `test_name` | `object` | Synthetic lab test name. |
| `collection_date` | `object` | Synthetic demonstration field. |
| `result_value` | `object` | Synthetic result value; blank where intentionally missing. |
| `unit` | `object` | Lab unit. |
| `reference_low` | `float64` | Synthetic demonstration field. |
| `reference_high` | `float64` | Synthetic demonstration field. |
| `abnormal_flag` | `object` | Low, Normal, High, Missing, or Implausible. |
| `source` | `object` | Synthetic demonstration field. |

## adverse_events.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `ae_id` | `object` | Synthetic adverse event identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `site_id` | `object` | Synthetic demonstration field. |
| `term` | `object` | Synthetic demonstration field. |
| `onset_date` | `object` | Synthetic adverse event onset date. |
| `resolution_date` | `object` | Synthetic demonstration field. |
| `reported_date` | `object` | Synthetic demonstration field. |
| `seriousness` | `object` | Non-serious or Serious. |
| `severity` | `object` | Mild, Moderate, or Severe. |
| `relationship` | `object` | Investigator-style causality category for demonstration. |
| `action_taken` | `object` | Synthetic demonstration field. |
| `outcome` | `object` | Resolved, Recovering, Ongoing, or Unknown. |
| `follow_up_required` | `bool` | Synthetic demonstration field. |
| `follow_up_status` | `object` | Synthetic demonstration field. |
| `source` | `object` | Synthetic demonstration field. |

## queries.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `query_id` | `object` | Synthetic EDC-style query identifier. |
| `site_id` | `object` | Synthetic demonstration field. |
| `participant_id` | `object` | Synthetic demonstration field. |
| `table_name` | `object` | Table where the issue was observed. |
| `field_name` | `object` | Synthetic demonstration field. |
| `record_id` | `object` | Synthetic record identifier related to the query. |
| `query_text` | `object` | Synthetic demonstration field. |
| `opened_date` | `object` | Synthetic demonstration field. |
| `closed_date` | `object` | Synthetic demonstration field. |
| `status` | `object` | Open, Answered, or Closed. |
| `age_days` | `int64` | Age in days for open or answered queries at data cut. |
| `severity` | `object` | Synthetic demonstration field. |
| `source` | `object` | Synthetic demonstration field. |

## protocol_deviations.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `deviation_id` | `object` | Synthetic protocol deviation identifier. |
| `participant_id` | `object` | Synthetic demonstration field. |
| `site_id` | `object` | Synthetic demonstration field. |
| `related_visit_id` | `object` | Synthetic demonstration field. |
| `deviation_date` | `object` | Synthetic demonstration field. |
| `category` | `object` | Eligibility, Visit Window, Safety Reporting, or Procedure. |
| `impact` | `object` | Minor, Major, or Critical. |
| `description` | `object` | Synthetic demonstration field. |
| `action_taken` | `object` | Illustrative corrective or preventive action. |
| `source` | `object` | Synthetic demonstration field. |

## milestones.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `milestone_id` | `object` | Synthetic milestone identifier. |
| `site_id` | `object` | Synthetic demonstration field. |
| `milestone_type` | `object` | Activation, First Participant In, Enrollment Target, or Database Snapshot. |
| `planned_date` | `object` | Planned milestone date. |
| `actual_date` | `object` | Actual date; blank if not achieved. |
| `status` | `object` | Met, Delayed, or Pending. |
| `source` | `object` | Synthetic demonstration field. |
