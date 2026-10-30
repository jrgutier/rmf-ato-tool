---
artifact_id: ART-CMP
run_id: agent-c1-s4-one-family
produced_by_task: S-4
touched_by: [S-4]
sources: [product/architecture.md#configuration, product/architecture.md#updates, product/test-results.md#config-scan]
---
# Configuration management plan

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-55 | S-1 |
<!-- END rmf:facts -->

## Plan summary

The plan covers every ESG unit, all of which run one signed OS image built from the General
Purpose Operating System SRG and the applicable application and web server guidance
[[product/architecture.md#configuration]]. Changes to that baseline go through the RSSPO
configuration control board, and the build pipeline records each approved deviation
[[product/architecture.md#configuration]]. A nightly configuration check on each unit reports
drift from the approved baseline to the SIEM; no unit drifted in August and September 2026
[[product/test-results.md#config-scan]]. Signed monthly update bundles are verified before
installation and are installed during quarterly site visits until remote update arrives in
release 2.2 [[product/architecture.md#updates]].
