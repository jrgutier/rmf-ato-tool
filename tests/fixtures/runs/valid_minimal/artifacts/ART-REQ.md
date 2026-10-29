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

## Definition

The program manager confirmed the requirements set [[INT-024.A1]].

## Allocation

Authentication is allocated to the identity provider, transport protection to the relay
service and hardening to every host [[INT-026.A1]].
