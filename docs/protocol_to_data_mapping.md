# Protocol-to-data mapping

## Synthetic study objective

The scenario asks how a clinical operations team might monitor a multicentre Phase II study of an investigational metabolic therapy over 12 weeks in adults with type 2 diabetes and elevated HbA1c despite background metformin therapy.

It is an invented protocol-shaped exercise. The dashboard uses clinical measurements for completeness and follow-up review, not for efficacy inference.

## Population and eligibility

| Requirement | Demonstration field or concept | Implementation status | Validation question |
|---|---|---|---|
| Age 35 to 75 years | `participants.age_years` | Implemented | Is age within the inclusive protocol range? |
| Consent before study procedures | `participants.consent_date`, `screening_date` | Implemented | Is consent on or before screening? |
| Randomisation after screening | `participants.randomization_date`, `screening_date` | Implemented | Is the date present when required and on or after screening? |
| Screening or baseline HbA1c | `labs.test_name`, `result_value`, linked `visits.visit_name` | Implemented | Does each randomised participant have at least one populated HbA1c result at Screening or Baseline/Randomisation? |
| Type 2 diabetes evidence | Eligibility form concept | Mapped only | No diagnosis-evidence field exists in the current schema. |
| Background metformin therapy | Concomitant-medication concept | Mapped only | No medication field exists in the current schema. |

The last two requirements remain visible because they matter to protocol interpretation. Omitting them from the schema is a declared limit, not an implied validation.

## Exclusion and safety concepts

| Concept | Demonstration field | Implemented review |
|---|---|---|
| Broad hepatic plausibility | `labs.test_name == "ALT"` | Missing and implausible results are separated; reference flags remain synthetic |
| Broad renal plausibility | `labs.test_name == "Creatinine"` | Missing and implausible results are separated; no clinical exclusion decision is made |
| Serious adverse event | `adverse_events.seriousness` | Incomplete follow-up is flagged |
| Ongoing adverse event | `adverse_events.outcome` | The event remains visible until it is no longer ongoing |
| Eligibility uncertainty | `protocol_deviations.category == "Eligibility"` | Record is visible as a synthetic deviation, without adjudication |

## Schedule of assessments

| Visit | Target day | Allowed window | Core expected data |
|---|---:|---:|---|
| Screening | -7 | ±7 days, giving day -14 to day 0 | consent, eligibility, demographics, HbA1c, ALT, creatinine |
| Baseline / Randomisation | 0 | ±3 days | randomisation, treatment arm, HbA1c, ALT, creatinine |
| Week 4 | 28 | ±7 days | safety, adherence and labs |
| Week 8 | 56 | ±7 days | safety, adherence and labs |
| Week 12 / End of Treatment | 84 | ±7 days | endpoint completeness, safety and labs |
| 30-Day Safety Follow-up | 114 | ±10 days | adverse-event review and follow-up |

The generator records Screening against the pre-randomisation window and fixes Baseline/Randomisation to the participant's recorded randomisation date. Later visits may be completed, early, late, missed or pending at the data cut.

## Operational outcomes

| Concept | Fields | Dashboard or report use |
|---|---|---|
| Site progress | target and randomised participant count | Illustrative progress towards target |
| Visit completion | scheduled rows and visit status | Performed, missed and pending counts |
| Visit adherence | actual date, scheduled date and window | Window-miss rate among performed visits |
| Data cleaning | query status, severity and age | Unresolved burden and median unresolved age |
| Safety follow-up | seriousness, outcome and follow-up status | Serious and ongoing event visibility |
| Protocol deviations | category, impact and related visit | Record-level operational context |
| Milestones | planned date, actual date and status | Delay beyond a 7-day tolerance |
| Data quality | validation check, severity and record | Trace from summary to affected record |

## Expected tables

- `sites.csv`
- `participants.csv`
- `visits.csv`
- `labs.csv`
- `adverse_events.csv`
- `queries.csv`
- `protocol_deviations.csv`
- `milestones.csv`

## Sources used for structure

- [NIH protocol templates for clinical trials](https://grants.nih.gov/policy-and-compliance/policy-topics/clinical-trials/protocol-template)
- [ClinicalTrials.gov glossary and protocol definitions](https://clinicaltrials.gov/policy/protocol-definitions)
- [NIMH clinical research toolbox](https://www.nimh.nih.gov/funding/clinical-research/clinical-research-toolbox/nimh-clinical-research-toolbox)

These sources informed the shape and vocabulary of the exercise. The synthetic scenario is not derived from a registered study.
