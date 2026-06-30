# Relational Data Practice Interpretation

This script demonstrates joins and aggregations across synthetic study tables.

## Checks Demonstrated

- Site enrollment uses `participants` joined to `sites`.
- Visit adherence uses `visits` joined to participant status.
- Lab missingness groups lab results by visit and test.
- Query ageing groups open and answered queries by site and severity.
- AE summary groups events by site, seriousness, severity, and follow-up status.

## Why These Checks Matter

Clinical operations dashboards need traceable data products: a high-level metric should be explainable by record-level tables.