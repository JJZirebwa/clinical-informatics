# Data dictionary

All datasets in this repository are synthetic, generated with a fixed seed. They contain no real patient, site, sponsor or EDC data.

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
| `age_years` | `int64` | Age in years at screening. |
| `sex` | `object` | Synthetic sex category. |
| `screening_date` | `object` | Date of screening visit. |
| `consent_date` | `object` | Date informed consent was synthetically recorded. |
| `randomization_date` | `object` | Date randomised; blank for screen failures. |
| `participant_status` | `object` | Screen Failed, Active, Completed, or Discontinued. |
| `treatment_arm` | `object` | Synthetic blinded treatment assignment label. |
| `baseline_hba1c` | `float64` | Synthetic HbA1c value used to populate the screening lab record. |
| `discontinuation_reason` | `object` | Synthetic reason; populated for discontinued participants. |
| `source` | `object` | Synthetic provenance marker. |

## visits.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `visit_id` | `object` | Synthetic visit identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `site_id` | `object` | Foreign key to sites.site_id; expected to match the participant. |
| `visit_name` | `object` | Protocol visit label. |
| `scheduled_date` | `object` | Expected visit date from the synthetic schedule. |
| `actual_date` | `object` | Observed visit date; blank when missed or pending. |
| `window_days` | `int64` | Allowed deviation in days either side of the scheduled date. |
| `visit_status` | `object` | Completed, Late, Early, Missed, or Pending. |
| `signed_delta_days` | `object` | Actual date minus scheduled date in days; blank when unperformed. |
| `days_from_window` | `object` | Number of days outside the allowed visit window; zero when in window. |
| `critical_visit` | `bool` | Whether an out-of-window completed visit receives high severity. |
| `assessments_expected` | `object` | Semicolon-delimited assessments expected for the visit. |
| `source` | `object` | Synthetic provenance marker. |

## labs.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `lab_id` | `object` | Synthetic lab result identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id; expected to match the visit. |
| `site_id` | `object` | Foreign key to sites.site_id; expected to match the visit and participant. |
| `visit_id` | `object` | Foreign key to visits.visit_id. |
| `test_name` | `object` | Synthetic lab test name. |
| `collection_date` | `object` | Collection date; blank when the planned visit was not performed. |
| `result_value` | `object` | Synthetic result value; blank where intentionally missing. |
| `unit` | `object` | Lab unit. |
| `reference_low` | `float64` | Illustrative lower reference limit. |
| `reference_high` | `float64` | Illustrative upper reference limit. |
| `abnormal_flag` | `object` | Low, Normal, High, Missing, or Implausible. |
| `source` | `object` | Synthetic provenance marker. |

## adverse_events.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `ae_id` | `object` | Synthetic adverse event identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `site_id` | `object` | Foreign key to sites.site_id; expected to match the participant. |
| `term` | `object` | Synthetic adverse event term. |
| `onset_date` | `object` | Synthetic adverse event onset date. |
| `resolution_date` | `object` | Resolution date; blank for ongoing events. |
| `reported_date` | `object` | Synthetic date the event was reported. |
| `seriousness` | `object` | Non-serious or Serious. |
| `severity` | `object` | Mild, Moderate, or Severe. |
| `relationship` | `object` | Investigator-style causality category. |
| `action_taken` | `object` | Illustrative action following the event. |
| `outcome` | `object` | Resolved, Recovering, Ongoing, or Unknown. |
| `follow_up_required` | `bool` | Whether follow-up is operationally required. |
| `follow_up_status` | `object` | Open, Complete, or Not required. |
| `source` | `object` | Synthetic provenance marker. |

## queries.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `query_id` | `object` | Synthetic EDC-style query identifier. |
| `site_id` | `object` | Foreign key to sites.site_id; expected to match the participant. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `table_name` | `object` | Table where the issue was observed. |
| `field_name` | `object` | Field where the query was raised. |
| `record_id` | `object` | Synthetic record identifier related to the query. |
| `query_text` | `object` | Synthetic query wording. |
| `opened_date` | `object` | Date the query was opened. |
| `closed_date` | `object` | Closure date; blank while unresolved. |
| `status` | `object` | Open, Answered, or Closed. |
| `age_days` | `int64` | Age at data cut for unresolved queries; elapsed time to closure for closed queries. |
| `severity` | `object` | Illustrative Low, Medium, or High operational priority. |
| `source` | `object` | Synthetic provenance marker. |

## protocol_deviations.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `deviation_id` | `object` | Synthetic protocol deviation identifier. |
| `participant_id` | `object` | Foreign key to participants.participant_id. |
| `site_id` | `object` | Foreign key to sites.site_id; expected to match the participant and related visit. |
| `related_visit_id` | `object` | Optional foreign key to visits.visit_id. |
| `deviation_date` | `object` | Date of the synthetic deviation. |
| `category` | `object` | Eligibility, Visit Window, Safety Reporting, or Procedure. |
| `impact` | `object` | Minor, Major, or Critical. |
| `description` | `object` | Synthetic deviation description. |
| `action_taken` | `object` | Illustrative corrective or preventive action. |
| `source` | `object` | Synthetic provenance marker. |

## milestones.csv

| Field | Type | Meaning / notes |
|---|---|---|
| `milestone_id` | `object` | Synthetic milestone identifier. |
| `site_id` | `object` | Foreign key to sites.site_id. |
| `milestone_type` | `object` | Activation, First Participant In, Enrolment Target, or Database Snapshot. |
| `planned_date` | `object` | Planned milestone date. |
| `actual_date` | `object` | Actual date; blank if not achieved. |
| `status` | `object` | Met, Delayed, or Pending. |
| `source` | `object` | Synthetic provenance marker. |
