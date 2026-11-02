---
artifact_id: ART-RA
run_id: hybrid-minimal
produced_by_task: P-14
touched_by: [P-14, R-2]
sources: [product/architecture.md]
---
# System risk assessment

## Method and scope

The assessment covers the relay appliance and uses the SP 800-30 qualitative scales
[[product/architecture.md#network]].

## Threat sources and events

An outsider who steals an administrator password logs in to the appliance (TE-1) [[product/architecture.md#network]].

## Vulnerabilities and predisposing conditions

Direct root SSH login and stale accounts make that event more likely [[product/architecture.md#network]].

## Threats

The main threats are spoofed field reports and compromise of the relay appliance from the
radio-side network [[product/architecture.md#network]].

## Update at R-2

The open account-review weakness (FND-001) raises the likelihood of misuse of stale
accounts until the POA&M closes it [[INT-011.A1]].
