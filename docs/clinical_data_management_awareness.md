# Clinical Data Management Awareness

## Positioning

This document records concepts that shaped the synthetic workflow.

## Concepts Used

| Concept | How it appears in this project |
|---|---|
| Protocol-driven data collection | The synthetic schedule of assessments drives visits, labs, AEs, queries and dashboard questions. |
| Source-to-eCRF traceability | Each query points to a table, field and record identifier. |
| Data-quality checks | Completeness, referential integrity, dates, duplicates, outliers, query ageing and AE follow-up are checked. |
| EDC query thinking | Queries are generated for missing, inconsistent or review-needed records and include status plus age. |
| Audit trail awareness | The project uses generated record IDs, build manifests, issue logs and reproducible scripts. |
| Risk-based focus | The dashboard prioritises critical visits, open SAE follow-up, high-severity queries and site-level patterns. |
| ALCOA+ awareness | See `LIMITATIONS_AND_GOVERNANCE.md` for how the project maps ALCOA+ to synthetic outputs. |
| Standards awareness | CDASH and SDTM are treated as vocabulary/context. |

## Practical Checks

- Are all child records linked to parent records?
- Are critical fields populated?
- Are study dates logically ordered?
- Are visits inside allowed windows?
- Are high-priority queries ageing?
- Are serious or ongoing adverse events followed up?
- Are site milestones delayed?
- Are missing data patterns visible?

## Source Links

- [EMA ICH E6 Good Clinical Practice page](https://www.ema.europa.eu/en/ich-e6-good-clinical-practice-scientific-guideline)
- [ICH E6(R3) Step 4 Final Guideline](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf)
- [FDA Electronic Source Data in Clinical Investigations](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/electronic-source-data-clinical-investigations)
- [FDA Risk-Based Monitoring Guidance](https://www.fda.gov/media/116754/download)
- [MHRA GxP Data Integrity Guidance](https://assets.publishing.service.gov.uk/media/5aa2b9ede5274a3e391e37f3/MHRA_GxP_data_integrity_guide_March_edited_Final.pdf)
- [CDISC CDASH](https://www.cdisc.org/standards/foundational/cdash)
- [CDISC SDTM](https://www.cdisc.org/standards/foundational/sdtm)