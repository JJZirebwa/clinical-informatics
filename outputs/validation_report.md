# Validation report

This report lists the record-level validation checks run on the synthetic snapshot and the issues each one found.

## Summary

| Check | Status | Severity | Issue count |
|---|---:|---|---:|
| `primary_key_uniqueness` | Pass | None | 0 |
| `participant_visit_uniqueness` | Pass | None | 0 |
| `participant_site_integrity` | Pass | None | 0 |
| `visit_participant_integrity` | Pass | None | 0 |
| `visit_site_integrity` | Pass | None | 0 |
| `visit_participant_site_consistency` | Pass | None | 0 |
| `lab_visit_integrity` | Pass | None | 0 |
| `lab_participant_integrity` | Pass | None | 0 |
| `lab_site_integrity` | Pass | None | 0 |
| `lab_visit_participant_consistency` | Pass | None | 0 |
| `lab_visit_site_consistency` | Pass | None | 0 |
| `lab_participant_site_consistency` | Pass | None | 0 |
| `ae_participant_integrity` | Pass | None | 0 |
| `ae_site_integrity` | Pass | None | 0 |
| `ae_participant_site_consistency` | Pass | None | 0 |
| `query_participant_integrity` | Pass | None | 0 |
| `query_site_integrity` | Pass | None | 0 |
| `query_participant_site_consistency` | Pass | None | 0 |
| `deviation_participant_integrity` | Pass | None | 0 |
| `deviation_site_integrity` | Pass | None | 0 |
| `deviation_visit_integrity` | Pass | None | 0 |
| `deviation_participant_site_consistency` | Pass | None | 0 |
| `deviation_visit_participant_consistency` | Pass | None | 0 |
| `deviation_visit_site_consistency` | Pass | None | 0 |
| `milestone_site_integrity` | Pass | None | 0 |
| `screening_after_site_activation` | Pass | None | 0 |
| `age_eligibility` | Pass | None | 0 |
| `consent_before_screening` | Pass | None | 0 |
| `randomization_timing` | Pass | None | 0 |
| `required_hba1c_availability` | Review | High | 1 |
| `critical_field_completeness` | Pass | None | 0 |
| `visit_status_date_consistency` | Pass | None | 0 |
| `visit_window_adherence` | Review | High; Medium | 96 |
| `lab_result_completeness` | Review | High; Medium | 46 |
| `lab_result_plausibility` | Review | High | 14 |
| `query_ageing` | Review | High; Medium | 37 |
| `ae_follow_up` | Review | High; Medium | 20 |
| `milestone_timeliness` | Review | Medium | 2 |

## Highest priority issues

| Severity | Table | Record | Message |
|---|---|---|---|
| High | participants | `P-0032` | No populated HbA1c result is available at screening or baseline. |
| High | visits | `V-00002` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00018` | Week 12 / End of Treatment is 1 day outside the protocol visit window. |
| High | visits | `V-00056` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00062` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00066` | Week 12 / End of Treatment is 9 days outside the protocol visit window. |
| High | visits | `V-00068` | Screening is 3 days outside the protocol visit window. |
| High | visits | `V-00083` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00086` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00104` | Screening is 2 days outside the protocol visit window. |
| High | visits | `V-00114` | Screening is 3 days outside the protocol visit window. |
| High | visits | `V-00120` | Screening is 2 days outside the protocol visit window. |
| High | visits | `V-00126` | Screening is 3 days outside the protocol visit window. |
| High | visits | `V-00148` | Screening is 3 days outside the protocol visit window. |
| High | visits | `V-00161` | Screening is 2 days outside the protocol visit window. |
| High | visits | `V-00193` | Week 12 / End of Treatment is 2 days outside the protocol visit window. |
| High | visits | `V-00201` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00204` | Screening is 2 days outside the protocol visit window. |
| High | visits | `V-00216` | Screening is 1 day outside the protocol visit window. |
| High | visits | `V-00228` | Screening is 2 days outside the protocol visit window. |

## Assumptions and thresholds

- Unresolved query threshold: Open or Answered queries older than 14 days require review.
- Milestone delay tolerance: 7 calendar days after the planned date.
- Visit-window flags apply only to performed visits. Missed and pending visits are reported separately.
- Lab plausibility thresholds are broad synthetic checks and do not represent protocol safety criteria.
- Missing lab results are flagged only for performed visits; planned records for missed or pending visits are not treated as completed-data omissions.
- Serious adverse events require complete follow-up; ongoing events remain visible until resolved.
- Validation output is issue-oriented so a dashboard user can move from metric to record-level review.

## ALCOA+ note

The checks make each issue attributable to a table and record identifier, readable in tabular form and time-aware through explicit dates. CSV and Markdown outputs support completeness, consistency and availability for review.
