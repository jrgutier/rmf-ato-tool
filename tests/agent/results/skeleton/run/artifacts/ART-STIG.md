---
artifact_id: ART-STIG
run_id: agent-skeleton
produced_by_task: I-1
touched_by: [I-1, A-3]
sources: [product/test-results.md#config-scan, product/hw-sw-inventory.md#items, INT-020.A2, INT-020.A3, INT-021.A1, INT-021.A3]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
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

The assessor relied on the 2026-09-30 SRG/STIG scan, which the assessor witnessed on all 12
units, and on the nightly configuration check showing no drift in August and September 2026
[[INT-020.A3]] [[product/test-results.md#config-scan]]. No result was re-run and no finding's
status changed, so the data file is unchanged. The two not-a-finding results were confirmed
against other evidence: STG-002 (web server TLS) under cm-6 and STG-003 (database privileged
audit records) under au-2 [[INT-020.A2]] [[INT-020.A3]]. Both open findings were confirmed:
STG-004, because all field technicians still sign in as the shared `fieldtech` account
(SAR finding FND-002) [[INT-021.A1]], and STG-001, because two units ran a 63-day-old update
bundle at the 2026-09-30 vulnerability scan (SAR finding FND-003) [[INT-021.A3]]
[[product/test-results.md#vuln-scan]].
