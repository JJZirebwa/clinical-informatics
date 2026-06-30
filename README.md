# Clinical Informatics Trial Operations Demo

A clinical informatics demonstration project translating a study-style protocol into data requirements, relational data checks, operational metrics and a Streamlit dashboard using synthetic trial-operations data.

# Live Dashboard:
https://clinical-informatics.streamlit.app

## What This Shows

This project is built as a compact analyst workflow:

1. Read a protocol-style study scenario.
2. Translate inclusion criteria, visits, safety monitoring and endpoints into data requirements.
3. Generate linked synthetic trial-style tables.
4. Run validation checks for completeness, referential integrity, visit windows, query ageing, adverse-event follow-up and lab plausibility.
5. Summarise operational metrics in reports and an interactive dashboard.

The work demonstrates protocol-to-data mapping, relational-table reasoning, data-quality consideration, reproducible Python and clear communication for clinical operations and health-data audiences.

## Scenario

The synthetic scenario is a multicentre Phase II metabolic outcomes study in adults with type 2 diabetes inadequately controlled on metformin. It uses a screening, baseline/randomization, Week 4, Week 8, Week 12, and 30-day safety follow-up schedule.

The structure is inspired by public clinical trial protocol and data-management guidance, including NIH protocol templates, ClinicalTrials.gov protocol elements, ICH E6(R3), FDA eSource and risk-based monitoring guidance, MHRA ALCOA+ data integrity concepts, and CDISC CDASH/SDTM awareness.

## Repository Map

- `docs/protocol_to_data_mapping.md`: study question, criteria, schedule, endpoints, data fields, quality risks and dashboard questions.
- `src/clinical_informatics/`: synthetic data generation, validation checks, metrics and reporting.
- `data/synthetic/`: generated synthetic CSV tables.
- `data/data_dictionary.md`: table and field dictionary.
- `notebooks/relational_data_practice.py`: joins, aggregations, date-window checks, query ageing, missingness and interpretation.
- `outputs/`: validation reports, metric CSVs, build manifest and example figures.
- `app/streamlit_app.py`: Streamlit trial-operations dashboard.
- `tests/`: basic checks for generation, validation and metrics.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m clinical_informatics.build_project
python notebooks/relational_data_practice.py
pytest
streamlit run app/streamlit_app.py
```

## Dashboard Views

The dashboard includes:

- overview metrics
- site-level enrollment and operational indicators
- visit adherence and window misses
- query burden and query ageing
- missingness and validation flags
- adverse-event summaries
- visible validation and limitations notes

## Synthetic Data Boundary

All data are synthetic. The project does not contain real patient data, real site data, EDC exports, sponsor data or identifiable information.

## Background

I am a First Class Biomedical Science graduate with governed hospital-data experience, Python/scikit-learn workflows, ICD-coded feature engineering, health-data governance exposure, scientific communication experience with this clinical informatics preparation in progress. This project extends that foundation into a public, synthetic trial-operations workflow.

## Limitations

This is a portfolio artifact for workflow demonstration. It is not a validated clinical data-management system, does not claim compliance with GCP, is not a CDISC submission package, is not a real EDC, and must not be used for patient care or operational trial decisions.

