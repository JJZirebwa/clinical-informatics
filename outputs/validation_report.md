# Validation Report

This report demonstrates clinical data validation checks on synthetic data. It is not a validated clinical data-management system and is not suitable for regulated operational use.

## Summary

| Check | Status | Severity | Issue count |
|---|---:|---|---:|
| `participant_site_integrity` | Pass | None | 0 |
| `visit_participant_integrity` | Pass | None | 0 |
| `lab_visit_integrity` | Pass | None | 0 |
| `duplicate_participants` | Pass | None | 0 |
| `duplicate_visits` | Pass | None | 0 |
| `randomization_after_screening` | Pass | None | 0 |
| `critical_field_completeness` | Pass | None | 0 |
| `visit_window_adherence` | Review | High; Medium | 109 |
| `lab_plausibility` | Review | High; Medium | 218 |
| `query_ageing` | Review | High; Medium | 27 |
| `ae_follow_up` | Review | High; Medium | 5 |
| `milestone_timeliness` | Review | Medium | 2 |

## Highest Priority Issues

| Severity | Table | Record | Message |
|---|---|---|---|
| High | visits | `V-00001` | Screening is 3 day(s) outside the protocol visit window. |
| High | visits | `V-00014` | Screening is 18 day(s) outside the protocol visit window. |
| High | visits | `V-00015` | Baseline / Randomisation is 3 day(s) outside the protocol visit window. |
| High | visits | `V-00020` | Screening is 9 day(s) outside the protocol visit window. |
| High | visits | `V-00043` | 30-Day Safety Follow-up is 10 day(s) outside the protocol visit window. |
| High | visits | `V-00045` | Baseline / Randomisation is 9 day(s) outside the protocol visit window. |
| High | visits | `V-00048` | Week 12 / End of Treatment is 5 day(s) outside the protocol visit window. |
| High | visits | `V-00051` | Baseline / Randomisation is 3 day(s) outside the protocol visit window. |
| High | visits | `V-00054` | Week 12 / End of Treatment is 9 day(s) outside the protocol visit window. |
| High | visits | `V-00055` | 30-Day Safety Follow-up is 3 day(s) outside the protocol visit window. |
| High | visits | `V-00068` | Screening is 8 day(s) outside the protocol visit window. |
| High | visits | `V-00072` | Screening is 8 day(s) outside the protocol visit window. |
| High | visits | `V-00092` | 30-Day Safety Follow-up is 4 day(s) outside the protocol visit window. |
| High | visits | `V-00111` | Screening is 3 day(s) outside the protocol visit window. |
| High | visits | `V-00125` | Week 12 / End of Treatment is 10 day(s) outside the protocol visit window. |
| High | visits | `V-00132` | Baseline / Randomisation is 1 day(s) outside the protocol visit window. |
| High | visits | `V-00136` | 30-Day Safety Follow-up is 7 day(s) outside the protocol visit window. |
| High | visits | `V-00152` | 30-Day Safety Follow-up is 2 day(s) outside the protocol visit window. |
| High | visits | `V-00160` | Screening is 7 day(s) outside the protocol visit window. |
| High | visits | `V-00166` | Screening is 8 day(s) outside the protocol visit window. |

## Assumption Log

- Query ageing threshold: open or answered queries older than 14 days require review.
- Visit-window flags are operational prompts, not automatic protocol-deviation adjudications.
- Lab plausibility thresholds are broad synthetic checks and do not represent protocol safety criteria.
- Serious or ongoing adverse events are highlighted when follow-up status remains open.
- Validation output is issue-oriented so a dashboard user can move from metric to record-level review.

## ALCOA+ Awareness Note

The checks are designed to make records attributable to a table and record identifier, readable in tabular form, time-aware through date fields, original to the generated synthetic record and accurate enough for demonstration. The reports also emphasise completeness, consistency, durable CSV/Markdown outputs and availability for review.