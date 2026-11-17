# Methodology

## Study scenario

The project uses an invented multicentre Phase II metabolic study in adults aged 35 to 75 with type 2 diabetes and elevated HbA1c despite background metformin therapy. It is a protocol-shaped scenario. The fixed data cut is 30 June 2026.

The schedule covers screening, baseline/randomisation, Week 4, Week 8, Week 12/end of treatment and a 30-day safety follow-up. That gives enough structure to design the operational data around.

## Protocol to data

The protocol mapping identifies the population, eligibility concepts, visit schedule, expected assessments, operational outcomes and likely data-quality risks. Each implemented requirement is tied to a field or relationship and, where appropriate, a validation check.

The current schema supports age, consent timing, randomisation timing and screening/baseline HbA1c availability. Diagnosis evidence and metformin background therapy remain mapped requirements only.

See [`docs/protocol_to_data_mapping.md`](docs/protocol_to_data_mapping.md) for the field-level mapping.

## Synthetic data generation

`generate_all_tables(seed=42)` creates eight pandas dataframes:

- sites;
- participants;
- visits;
- labs;
- adverse events;
- queries;
- protocol deviations; and
- milestones.

Identifiers and repeated site or participant fields connect the tables. Participant screening cannot precede site activation. Screening is scheduled at day -7 with a ±7-day window, which gives an allowed interval of day -14 to day 0 relative to randomisation. Baseline/Randomisation occurs on the participant's recorded randomisation date. No actual visit, adverse-event or reporting date is generated after the data cut; visits due later remain `Pending`.

Lab rows act as expected assessment records. A missing result is a data-quality issue only when the related visit was performed. Blank results at missed or pending visits are retained for schedule visibility but are not counted as completed-visit omissions.

The same seed produces identical tables, reports and figures in the tested environment. The tests run two isolated builds and compare every generated file by SHA-256 hash.

## Validation design

Validation returns two tables:

- `issues`, with the check, severity, table, record, site, participant and message for each problem;
- `summary`, with one row for every registered check and a Pass or Review status.

The checks fall into six groups.

| Group | What is checked |
|---|---|
| Identifier uniqueness | Primary keys for all eight tables and one visit per participant/visit name |
| Referential integrity | Every documented site, participant and visit parent relationship |
| Context consistency | Repeated site and participant identifiers agree with parent records |
| Protocol timing and eligibility | Site activation, age 35 to 75, consent by screening, randomisation timing and required HbA1c |
| Record semantics | Performed versus missed/pending visits, visit windows, lab completeness and plausibility |
| Operational follow-up | Query ageing, adverse-event follow-up and milestone timing |

Critical visits receive High severity when performed outside their window; other visits receive Medium severity. Missed and pending visits cannot create a visit-window breach even if a stale `days_from_window` value is present.

Lab issues are split into `lab_result_completeness` and `lab_result_plausibility`. Serious adverse events require complete follow-up. Ongoing events remain visible because their follow-up cannot coherently be treated as finished.

## Operational definitions

These constants are defined in `src/clinical_informatics/config.py` and repeated in generated reports for inspection.

| Definition | Rule |
|---|---|
| Data cut | 30 June 2026 |
| Age range | 35 to 75 years, inclusive |
| Unresolved query | Status is `Open` or `Answered` |
| Aged unresolved query | More than 14 days old at the data cut |
| Milestone delay | Actual date is more than 7 calendar days after plan, or the item remains pending beyond that tolerance |
| Performed visit | Status is `Completed`, `Late` or `Early` |
| Unperformed visit | Status is `Missed` or `Pending` |
| Required HbA1c | At least one populated `HbA1c` lab at Screening or Baseline/Randomisation for a randomised participant |
| Empty unresolved age | `0.0` days, used as an explicit safe value when no unresolved query exists |

## Metric calculations

| Metric | Numerator | Denominator or subset |
|---|---|---|
| `visit_completion_rate` | Performed visits | All scheduled visit rows |
| `visit_window_miss_rate` | Performed visits outside their window | Performed visits only |
| `open_query_n` | `Open` plus `Answered` queries | Current filtered query table |
| `median_open_query_age_days` | Median `age_days` | The same `Open` plus `Answered` subset |
| `enrollment_to_target_rate` | Participants with a randomisation date | Illustrative site target |
| `high_severity_issue_n` | High plus Critical validation issues | Current filtered issue table |
| `open_follow_up_n` | Adverse events with `follow_up_status == "Open"` | Current AE grouping |

Site metrics use the same rules after selecting one site. Query charts label `Open` and `Answered` as unresolved so the display matches the calculation.

## Dashboard filtering

The app loads the generated raw tables, applies site, participant-status and visit filters, then reruns validation and metric derivation. Child tables are restricted by the retained participant and visit identifiers. Protocol deviations without a related visit remain visible when a visit filter is used because their relationship is intentionally blank.

Clearing a selector produces an empty affected subset. The app displays a notice and keeps zero-valued summary output, which avoids the more dangerous behaviour of treating “nothing selected” as “show everything”.

## Reproducibility

`python -m clinical_informatics.build_project --seed 42` is the build. It regenerates the raw tables, data dictionary, issue tables, summaries and static figures. `python notebooks/relational_data_practice.py` regenerates the join and aggregation examples.

GitHub Actions uses Python 3.12, installs the package and development dependencies, runs Ruff, enforces at least 80% test coverage, regenerates the project and confirms that the committed outputs match the code. No dependency lock is committed because Streamlit Community Cloud installs from `requirements.txt`. The version ranges in `pyproject.toml` and the CI run cover compatibility instead.
