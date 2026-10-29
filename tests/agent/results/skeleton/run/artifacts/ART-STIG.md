---
artifact_id: ART-STIG
run_id: agent-skeleton
produced_by_task: I-1
touched_by: [I-1, A-3]
sources: [product/test-results.md#config-scan, product/hw-sw-inventory.md#items, INT-023.A5, INT-025.A1, INT-026.A1, INT-026.A3]
---
# STIG/SRG summary — ESG

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

<!-- Seeded for the walking-skeleton scenario (I-1 is out of scope). The structured results
     are in `artifacts/data/stig-summary.yaml`. Benchmark versions and rule IDs are
     FICTIONAL. -->

## Applicability

| Benchmark | Applies to |
|---|---|
| BM-01 General Purpose Operating System SRG | INV-002 gateway OS image |
| BM-02 Web Server SRG | INV-004 admin web console |
| BM-03 Application Security and Development STIG | INV-003 collector, INV-004 console |
| BM-04 Database SRG | INV-005 buffer database |

Firmware items INV-006 and INV-008 have no applicable SRG or STIG; the rationale is recorded
per item in the data file [[product/hw-sw-inventory.md#items]].

## Scan results (2026-09-30)

The assessor-witnessed scan of 12 units found the approved baseline in place
[[product/test-results.md#config-scan]]. Open findings:

| ID | Category | Item | Finding | Control |
|---|---|---|---|---|
| STG-001 | CAT II | INV-002 | security-relevant updates not installed within the organization-defined period (2 of 12 units) | si-2 |
| STG-004 | CAT II | INV-004 | shared account permitted for privileged local access (`fieldtech`) | ia-2 |

No CAT I finding is open [[product/test-results.md#vuln-scan]].

## Assessor verification (A-3)

The assessment team accepted the assessor-witnessed 2026-09-30 SRG/STIG scan of 12 units as
evidence for cm-6, together with the nightly drift check, which showed no drift in August or
September 2026 [[INT-023.A5]] [[INT-025.A1]]. The not-a-finding results were confirmed:
STG-002 (TLS settings, cm-6) against the board-approved baseline, and STG-003 (database
audit records, au-2) against the weekly SIEM reports and the DT-2 event delivery results
[[INT-023.A4]] [[INT-025.A2]].

Both open findings were confirmed by the team's own work. STG-001 (si-2) stands: at the
2026-09-30 scan two fielded units ran the 63-day-old 2026-07 bundle, and fielded units are
updated only at quarterly visits; it is carried as FND-004 [[INT-026.A3]] [[INT-027.A3]]
[[product/test-results.md#vuln-scan]]. STG-004 (ia-2) stands: a maintenance-port sign-in
test as `fieldtech` on two pre-production units (simulated) produced audit records naming
only the shared account; it is carried as FND-003 [[INT-026.A1]] [[INT-027.A1]]. No finding
changed status, so `artifacts/data/stig-summary.yaml` is unchanged.
