# Methodology

## Scenario Selection

The project uses a synthetic multicentre Phase II metabolic outcomes study. It supports eligibility review, visit scheduling, labs, adverse events, protocol deviations, EDC-style queries, and site milestones without relying on any real protocol, sponsor document or patient data.

## Protocol-to-Data Logic

The protocol mapping defines:

- population and eligibility requirements
- visit schedule and windows
- endpoint and safety concepts
- expected tables and fields
- quality risks
- validation questions
- dashboard questions

This creates a traceable route from study design to data structure.

## Synthetic Data Design

The generator creates deterministic synthetic data using a fixed seed. Tables are linked through synthetic identifiers:

- `sites.site_id`
- `participants.participant_id`
- `visits.visit_id`
- `labs.lab_id`
- `adverse_events.ae_id`
- `queries.query_id`
- `protocol_deviations.deviation_id`
- `milestones.milestone_id`

The data include a realistic number of missing fields, visit-window misses, open queries, delayed milestones, abnormal labs, and open adverse-event follow-up items.

## Validation Checks

Validation checks cover:

- participant-to-site referential integrity
- visit-to-participant referential integrity
- lab-to-visit referential integrity
- duplicate identifiers and duplicate participant visits
- randomization after screening
- critical field completeness
- visit-window adherence
- lab plausibility
- open query ageing
- serious or ongoing AE follow-up visibility
- milestone timeliness

The checks are demonstrations of data-quality thinking. They are not sponsor SOPs and do not replace clinical data management review.

## Metrics

Metrics are chosen for clinical operations visibility:

- enrollment progress
- completion and screen-failure counts
- visit completion and window-miss rates
- open and aged query burden
- AE and serious AE counts
- missingness by table and field
- validation issues by check and severity

The dashboard keeps interpretation close to the data.

