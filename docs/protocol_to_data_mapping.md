# Protocol-to-Data Mapping

## Study-Style Objective

Demonstrate how a clinical operations team might monitor a synthetic multicentre Phase II study evaluating whether an investigational metabolic therapy improves glycaemic control over 12 weeks in adults with type 2 diabetes inadequately controlled on metformin.

This scenario is synthetic and inspired by public protocol structures.

## Population

Adults aged 35 to 75 with type 2 diabetes, background metformin therapy and elevated baseline HbA1c.

## Inclusion Criteria

| Criterion | Data fields | Validation question |
|---|---|---|
| Adult participant | `age_years` | Is age in the protocol range? |
| Type 2 diabetes history | eligibility form concept | Is diagnosis evidence documented? |
| Metformin background therapy | concomitant medication concept | Is background therapy captured before randomization? |
| HbA1c above threshold | `labs.test_name`, `labs.result_value` | Is screening or baseline HbA1c present? |
| Consent before study procedures | `consent_date`, `screening_date` | Is consent on or before screening? |

## Exclusion Criteria

| Criterion | Data fields | Validation question |
|---|---|---|
| Severe hepatic abnormality | `labs.test_name = ALT` | Are implausible or high ALT values reviewed? |
| Severe renal impairment | `labs.test_name = Creatinine` | Are high creatinine values visible? |
| Recent serious adverse event | `adverse_events.seriousness`, `onset_date` | Are SAE records followed up? |
| Eligibility evidence unclear | `protocol_deviations.category = Eligibility` | Was the enrollment decision documented? |

## Schedule of Assessments

| Visit | Target day | Window | Core data expected |
|---|---:|---:|---|
| Screening | -14 to 0 | 14 days | consent, eligibility, demographics, baseline labs |
| Baseline / Randomisation | 0 | 3 days | randomization, vitals, labs, treatment arm |
| Week 4 | 28 | 7 days | safety, adherence, labs |
| Week 8 | 56 | 7 days | safety, adherence, labs |
| Week 12 / End of Treatment | 84 | 7 days | endpoint labs, safety, discontinuation status |
| 30-Day Safety Follow-up | 114 | 10 days | AE review, follow-up status |

## Endpoints and Operational Outcomes

| Concept | Demonstration field(s) | Dashboard use |
|---|---|---|
| Primary clinical endpoint proxy | HbA1c at Week 12 | Data completeness and readiness, not efficacy inference |
| Safety monitoring | AE seriousness, severity, outcome, follow-up | SAE visibility and open follow-up |
| Visit adherence | scheduled date, actual date, window | Site-level window-miss rate |
| Data cleaning | EDC-style queries | Query burden and ageing |
| Site performance | milestones and enrollment | Target progress and delayed milestones |

## Expected Tables

- `sites.csv`
- `participants.csv`
- `visits.csv`
- `labs.csv`
- `adverse_events.csv`
- `queries.csv`
- `protocol_deviations.csv`
- `milestones.csv`

## Data-Quality Risks

- randomized participant missing a randomisation date
- visit completed outside the protocol window
- lab result missing at a critical visit
- implausible lab value requiring review
- open query ageing beyond an operational threshold
- SAE or ongoing AE without complete follow-up
- delayed site milestone
- participant, visit, or lab record referencing a missing parent record

## Dashboard Questions

- Which sites are behind enrollment target?
- Which sites have the highest open query burden?
- Which visits are most often outside window?
- Are safety follow-up items still open?
- Which validation checks need analyst review?
- Which fields have the highest missingness?

## Sources Used for Structure

- [NIH Protocol Templates for Clinical Trials](https://grants.nih.gov/policy-and-compliance/policy-topics/clinical-trials/protocol-template)
- [ClinicalTrials.gov Protocol Definitions](https://clinicaltrials.gov/policy/protocol-definitions)
- [NIMH Clinical Research Toolbox](https://www.nimh.nih.gov/funding/clinical-research/clinical-research-toolbox/nimh-clinical-research-toolbox)

