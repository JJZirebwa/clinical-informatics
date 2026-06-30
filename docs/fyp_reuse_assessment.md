# FYP Reuse Assessment

## What Was Inspected

The private final-year project folder was inspected for reusable structure and public-safety boundaries. High-signal areas included:

- project map and status documents
- governance and non-use language
- feature catalogue and data dictionary style
- methods and workflow notes
- TRE artefact inventory
- feature-engineering scripts and configuration patterns
- export-safety and audit-reporting practices

## What Was Reused

Only public-safe structural ideas were reused:

- layered documentation: summary, methodology, governance, mapping, relational design, and dashboard notes
- dictionary style: field, type, source, definition, notes
- audit-style validation reports
- explicit assumption and limitation logs
- reproducible build entrypoint
- cautious interpretation language
- separation between generated data, reports, source code, and dashboard

## What Was Not Reused

The project does not reuse:

- row-level clinical data
- restricted exports
- rare-disease cohort details
- pseudonymous participant identifiers from the source project
- exact clinical-code groupings
- exact metrics, small counts, split sizes, or model outputs
- dissertation submission artefacts
- internal TRE paths or storage conventions

## Public-Safety Decision

The safest public route was to build a fully synthetic trial-operations dataset. Where the private source project used sensitive clinical concepts, this repository substitutes generic feature names, synthetic identifiers, invented site names, and non-identifiable operational examples.

## Governance Note

This repository is a portfolio artifact for informatics workflow demonstration only. It is not a clinical tool, not a validated diagnostic model, and not suitable for patient care or real trial operations.

