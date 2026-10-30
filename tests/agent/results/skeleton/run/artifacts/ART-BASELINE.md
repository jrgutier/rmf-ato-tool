---
artifact_id: ART-BASELINE
run_id: agent-skeleton
produced_by_task: S-1
touched_by: [S-1]
sources: [INT-011.A1, INT-011.A2, INT-011.A3, INT-012.A1, INT-012.A2, ART-ORG-CONTEXT, ART-REQ]
---
# Control baseline, tailoring and allocation

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Selection basis

The baseline was selected with CNSSI 1253 per-objective selection (`method: cnssi1253` in
`baseline.json`): the union of the Appendix D controls selected at the confidentiality,
integrity and availability levels of the approved categorization in the facts block, plus the
NSS privacy control baseline, then the overlays listed in the facts block, the tailoring
actions and the run's six-control subset (ac-2, au-2, cm-6, ia-2, sc-7, si-2) [[INT-011.A1]].
The only overlay is the account-record privacy set approved at C-3; the Component adds no
controls of its own, and its standards enter as parameter values [[INT-011.A2]].

## Common controls available for inheritance

| Provider | Offered to ESG | Inheritance | Authorization |
|---|---|---|---|
| Installation Network Enclave | sc-7 boundary protection at the enclave edge | partial: ESG keeps its host firewall | current enclave ATO |
| Installation ICAM Service | ia-2 DoD PKI authentication for remote administrators | partial: ESG federates its console | covered by the enclave ATO |
| Installation CSSP | au-2 event collection and correlation in the SIEM | partial: ESG generates and forwards events | current CSSP authorization |

Offers and status per the common control provider [[INT-012.A1]] [[INT-012.A2]] and the
organizational context [[ART-ORG-CONTEXT]].

## Tailoring and allocation

Both data files were seeded for this run in place of S-2 and S-3, which are out of scope.
`artifacts/data/tailoring.yaml` sets four organization-defined parameters: the ac-2 account
review frequency, the au-2 event-list review frequency, the si-2 remediation period and the
cm-6 configuration settings [[product/architecture.md#identity]] [[product/architecture.md#logging]]
[[ART-ORG-CONTEXT]]. `artifacts/data/allocation.yaml` makes ac-2, cm-6 and si-2
system-specific, and au-2, ia-2 and sc-7 hybrid with the three providers above
[[product/architecture.md#configuration]] [[product/architecture.md#network]].

## Requirements to address in tailoring

REQ-01 to REQ-06 map onto the six selected controls; REQ-07 (telemetry protected in transit and
accepted only from paired sensors) needs controls such as sc-8 and ia-3 that the six-control
subset leaves out, so S-2 should record it as a known scope gap [[INT-011.A3]] [[ART-REQ]].
