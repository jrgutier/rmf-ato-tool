---
artifact_id: ART-BASELINE
run_id: agent-skeleton
produced_by_task: S-1
touched_by: [S-1]
sources: [INT-011.A1, INT-011.A2, INT-011.A3, INT-011.A4, INT-012.A1, INT-012.A2, INT-012.A3, INT-012.A4, ART-CAT, ART-ORG-CONTEXT, ART-REQ, ASM-002]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Selection basis

The baseline in the facts block is the SP 800-53B baseline at the high-water mark of the
approved categorization (`method: high-water-mark` in `baseline.json`), restricted to the six
controls in this run's control subset: ac-2, au-2, cm-6, ia-2, sc-7 and si-2 [[INT-011.A1]]
[[ART-CAT]]. CNSSI 1253 per-objective selection is pending (Phase 6), so this is not a CNSSI
1253 baseline [[INT-011.A1]]. No overlay is applied: the classified and space overlays do not
apply, and the privacy overlay is excluded only under ASM-002; if the privacy office finds PII,
the categorization returns to the AODR and selection is repeated with the privacy overlay
[[INT-011.A2]] [[ASM-002]].

## Common controls available for inheritance

| Provider | Offered to ESG | Inheritance | Authorization |
|---|---|---|---|
| Installation Network Enclave | sc-7 at the enclave edge (enclave firewall, network access control) | hybrid: ESG runs its own host firewall [[INT-012.A1]] | ATO 2025-11-20, current [[INT-012.A1]] |
| Installation ICAM Service | ia-2 DoD PKI authentication for remote organizational users | hybrid: ESG federates its console and owns its local accounts [[INT-012.A2]] | covered by the enclave ATO [[INT-012.A2]] |
| Installation CSSP | au-2 event list agreement and review, SIEM collection | hybrid: ESG generates and forwards the events [[INT-012.A3]] | ATO 2026-01-30, current [[INT-012.A3]] |

No provider offers ac-2, cm-6 or si-2; they are system-specific [[INT-012.A4]]
[[ART-ORG-CONTEXT]].

## Tailoring and allocation

`artifacts/data/tailoring.yaml` was seeded for S-2 and holds four parameter actions and no
add or remove action: quarterly account review (ac-2), annual event-list review (au-2), the
applicable DISA SRGs and STIGs as configuration settings (cm-6), and a 30-day flaw remediation
period (si-2) [[INT-011.A3]] [[ART-ORG-CONTEXT]]. `artifacts/data/allocation.yaml` was seeded
for S-3: ac-2, cm-6 and si-2 are system-specific, and au-2, ia-2 and sc-7 are hybrid with the
providers above, which matches the provider answers [[INT-012.A1]] [[INT-012.A2]]
[[INT-012.A3]] [[INT-012.A4]].

## Requirements to address in tailoring

- REQ-07 (telemetry protected in transit, accepted only from paired sensor nodes) has no control
  in the six-control subset; S-2 should consider sc-8 and device identification controls
  [[INT-011.A4]] [[ART-REQ]].
- REQ-01 and REQ-06 are covered by ac-2 and si-2 but are known gaps today (shared `fieldtech`
  account, updates only at quarterly visits); S-4 and A-3 must record them [[INT-011.A4]]
  [[ART-REQ]].
