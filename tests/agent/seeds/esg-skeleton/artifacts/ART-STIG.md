---
artifact_id: ART-STIG
run_id: esg-skeleton
produced_by_task: I-1
touched_by: [I-1]
sources: [product/test-results.md#config-scan, product/hw-sw-inventory.md#items]
---
# STIG/SRG summary — ESG

<!-- BEGIN rmf:facts -->
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
