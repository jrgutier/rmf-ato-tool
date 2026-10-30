---
artifact_id: ART-REQ
run_id: esg-c1-s4
produced_by_task: P-15
touched_by: [P-15]
sources: [product/conops.md#mission, product/architecture.md#boundary]
---
# Security requirements and allocation — ESG

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Seeded for the walking-skeleton scenario (P-15 and P-17 are out of scope). -->

## Security requirements

| ID | Requirement | Allocated to |
|---|---|---|
| REQ-01 | Every privileged action on a gateway is attributable to one individual. | CMP-WEBUI, CMP-GW-OS, CMP-ICAM |
| REQ-02 | Remote administrators authenticate with DoD PKI through the installation identity service. | CMP-WEBUI, CMP-ICAM |
| REQ-03 | Security-relevant events are logged and forwarded to the CSSP within one minute. | CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI, CMP-CSSP |
| REQ-04 | Gateways run the approved hardened baseline and report drift. | CMP-GW-OS |
| REQ-05 | Only documented flows cross the boundary; everything else is denied. | CMP-GW-OS, CMP-ENCLAVE |
| REQ-06 | Security-relevant updates are installed within the organizational remediation period. | CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI, CMP-STORE |
| REQ-07 | Telemetry is protected in transit and accepted only from paired sensor nodes. | CMP-SENSOR-NET, CMP-COLLECTOR |

Derived from the mission need and the boundary design [[product/conops.md#mission]]
[[product/architecture.md#boundary]].

## Known gaps against the requirements

REQ-01 is not met on site while the shared `fieldtech` account exists, and REQ-06 is not met
on units between quarterly visits [[product/conops.md#limitations]].
