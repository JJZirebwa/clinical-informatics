# Clinical data management concepts

## Purpose

The clinical data-management ideas that shaped the workflow, where each one shows up, and what a fuller system would add.

| Concept | How it appears here | Not modelled yet |
|---|---|---|
| Protocol-driven collection | The schedule defines expected visits, labs and review questions. | The scenario is invented and much smaller than a real protocol. |
| Record traceability | Issues include a table, record, site and participant where applicable. | There is no source document or source-data verification. |
| Query management | Queries have Open, Answered and Closed states plus age and severity. | There is no status history, role workflow or audit trail. |
| Data review | Checks cover completeness, relationships, dates, plausibility and follow-up. | Rules are illustrative and do not reproduce sponsor procedures. |
| Risk-focused review | Critical visits, unresolved queries and AE follow-up are visible. | Dashboard measures are not monitoring decisions or site judgements. |
| Data integrity | Stable identifiers, explicit dates and reproducible outputs support inspection. | Files do not provide access control, electronic signatures or validated audit trails. |
| CDASH and SDTM | The standards inform vocabulary and the separation of collection from submission structures. | No CDASH conformance or SDTM transformation is implemented. |

## Questions the workflow can answer

- Does every child record have the documented parent?
- Do repeated site and participant identifiers agree?
- Was consent recorded on or before screening?
- Is randomisation timing logically consistent?
- Does each randomised participant have a screening or baseline HbA1c result?
- Which performed visits are outside their window?
- Which performed visits have a missing lab result?
- Which unresolved queries are older than 14 days?
- Which serious or ongoing adverse events need follow-up?
- Which milestones are beyond the stated tolerance?

## Reference material

- [EMA page for ICH E6 Good Clinical Practice](https://www.ema.europa.eu/en/ich-e6-good-clinical-practice-scientific-guideline)
- [ICH E6(R3) Step 4 final guideline](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- [FDA guidance on electronic source data in clinical investigations](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/electronic-source-data-clinical-investigations)
- [FDA risk-based monitoring questions and answers](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/risk-based-approach-monitoring-clinical-investigations-questions-and-answers)
- [MHRA guidance on GxP data integrity](https://www.gov.uk/government/publications/guidance-on-gxp-data-integrity)
- [CDISC CDASH](https://www.cdisc.org/standards/foundational/cdash)
- [CDISC SDTM](https://www.cdisc.org/standards/foundational/sdtm)

I used these for terminology and design questions.
