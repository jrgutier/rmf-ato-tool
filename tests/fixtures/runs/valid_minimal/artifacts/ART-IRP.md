---
artifact_id: ART-IRP
run_id: valid-minimal
produced_by_task: S-4
touched_by: [S-4, I-2]
sources: [INT-007.A1, INT-033.A1]
---
# Incident response plan

## Detection

Audit records go to the enclave SIEM, which the CSSP monitors [[product/security.md#audit]].

## Reporting

The ISSO reports incidents to the ISSM and the CSSP [[INT-007.A1]].

## As built

The developers confirmed SIEM forwarding on the build [[INT-033.A1]].
