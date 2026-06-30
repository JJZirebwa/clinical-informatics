# Project Summary

## One-Line Description

Synthetic clinical informatics project showing how a study-style protocol can be translated into relational trial operations data, validation checks, operational metrics and a Streamlit dashboard.

## Workflow

1. Define a protocol-style question and schedule of assessments.
2. Map each protocol element to expected data fields and quality risks.
3. Generate linked synthetic tables for sites, participants, visits, labs, adverse events, queries, deviations, and milestones.
4. Run reproducible validation checks.
5. Produce dashboard-ready metrics and short reports.
6. Present results with visible assumptions, limitations and governance boundaries.

## Main Outputs

- `data/synthetic/*.csv`: linked synthetic study tables.
- `data/data_dictionary.md`: table/field dictionary.
- `outputs/validation_report.md`: issue-oriented validation summary.
- `outputs/metrics_summary.md`: top operational metrics.
- `outputs/figures/*.png`: static example figures.
- `app/streamlit_app.py`: interactive dashboard.

