# Relational data practice interpretation

This script runs joins and aggregations across the synthetic study tables.

## Checks

- Site enrolment uses `participants` joined to `sites`.
- Visit adherence uses `visits` joined to participant status.
- Lab missingness is limited to performed visits and grouped by visit name and test.
- Query ageing groups unresolved Open and Answered queries by site and severity.
- AE summary groups events by site, seriousness, severity, and follow-up status.

## Why these checks matter

Clinical operations dashboards need traceable data products. A summary metric should be explainable through its record-level source tables.
