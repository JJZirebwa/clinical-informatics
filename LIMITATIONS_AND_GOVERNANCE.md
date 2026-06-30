# Limitations and Governance

## Intended Use

This repository is a public portfolio project for clinical informatics workflow demonstration. It is intended to show structured thinking, reproducible Python, relational data checks, validation awareness, and dashboard communication.

## Explicit Non-Use

This project is not:

- a clinical tool
- a patient-care system
- a sponsor oversight system
- an electronic data capture system
- a validated clinical data-management platform
- a regulatory submission package
- a CDISC-conformant submission dataset
- evidence of GCP certification
- evidence of production trial data ownership

## Data Boundary

All records are synthetic. The repository contains no real participant data, real site data, sponsor data, EDC exports, restricted TRE outputs, direct identifiers, pseudonymous IDs from a source project, or rare-disease cohort metrics.

## Data Integrity Framing

The project uses ALCOA+ as an awareness-level design lens:

- attributable: records have table and record identifiers
- legible: outputs are CSV and Markdown
- contemporaneous: synthetic dates are explicit
- original: each row is generated in the synthetic source table
- accurate: checks flag implausible or inconsistent records
- complete: missingness is measured
- consistent: linked table rules are checked
- enduring: outputs are written as files
- available: reports and dashboard views are generated for review

This is a demonstration of data integrity thinking, not a claim of regulatory inspection readiness.

## Human Review Needed

Before linking publicly, a human should review:

- whether the README tone fits the target portfolio page
- whether screenshots should be added after manually running the dashboard
- whether any source links need local institutional preference updates
- whether the synthetic study scenario should be narrowed for a specific role

## Extension Ideas

Useful next steps would be:

- add SQL examples using SQLite
- add a small test data factory for validation edge cases
- add dashboard screenshots
- add a lightweight ER diagram
- add an optional CDASH-to-SDTM awareness mapping appendix
