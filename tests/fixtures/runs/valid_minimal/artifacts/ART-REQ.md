---
artifact_id: ART-REQ
run_id: valid-minimal
produced_by_task: P-15
touched_by: [P-15, P-17]
sources: [product/security.md]
---
# Security requirements

## Requirements

FDR must authenticate every interactive user with multi-factor authentication and protect
reports in transit [[product/security.md#authentication]].

| ID | Requirement | Source |
|---|---|---|
| REQ-01 | Every interactive user authenticates with multi-factor authentication | product/security.md |
| REQ-02 | Reports are protected in transit | product/security.md |
| REQ-03 | Every host runs a hardened configuration | product/security.md |

## Definition

The program manager confirmed the requirements set [[INT-024.A1]].

## Allocation

Authentication is allocated to the identity provider, transport protection to the relay
service and hardening to every host [[INT-026.A1]].
