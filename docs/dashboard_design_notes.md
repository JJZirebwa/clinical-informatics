# Dashboard Design Notes

## Audience

The dashboard is designed for a clinical operations or clinical data analyst reviewer who wants to inspect site progress, data-cleaning workload, visit adherence, and validation flags quickly.

## Design Direction

The interface is deliberately quiet and operational:

- compact overview metrics
- filters in the sidebar
- charts paired with data tables
- restrained color use
- validation and limitation notes visible in the app
- no hero section, marketing copy, or decorative layout

## Pages / Tabs

- `Overview`: study-wide status and site table
- `Sites`: enrollment, query burden, visit-window misses, and deviations
- `Visits`: schedule adherence by visit and site
- `Queries`: open query burden and query ageing
- `Safety`: adverse-event counts and follow-up visibility
- `Validation`: validation summary, issue table, missingness, and limitations

## Usability Choices

- Filters use site, participant status, and visit name.
- Metrics remain visible even when filters narrow the tables.
- The app reads generated CSVs, so it is reproducible after `python -m clinical_informatics.build_project`.
- The app does not hide validation issues. It shows them as part of the product.

