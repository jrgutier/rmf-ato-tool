---
artifact_id: ART-SAR
run_id: agent-skeleton
produced_by_task: A-3
touched_by: [A-3]
sources: [ART-SAP, ART-SSP, ART-STIG, INT-023.A1, INT-023.A2, INT-026.A1, INT-026.A3, INT-027.A3, product/test-results.md#dt-2, product/test-results.md#vuln-scan, product/conops.md#limitations]
---
# Security assessment report

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

## Assessment summary

The team assessed the whole baseline (ac-2, au-2, cm-6, ia-2, sc-7, si-2) against every
SP 800-53A objective, as the approved plan sets, using examine, interview and test for each
control [[ART-SAP]] [[ART-SSP]]. For the hybrid controls au-2, ia-2 and sc-7 the ESG part was
assessed and the provider parts were evidenced by the common control provider and current
provider ATOs [[INT-024.A1]] [[INT-028.A1]] [[INT-028.A2]]. Result mix: satisfied 3 (au-2,
cm-6, sc-7), other-than-satisfied 3 (ac-2, ia-2, si-2), not-applicable 0. Four findings are
open: FND-001, FND-002 and FND-003 (moderate) and FND-004 (high). The determinations live in
`artifacts/sar/results/<fam>.yaml`. Every other-than-satisfied result matches a gap the SSP
already discloses as `partial`, so no SSP correction is needed [[ART-SSP]]
[[product/conops.md#limitations]].

## Test results reused

As the AODR required, each determination states which evidence was reused and which the team
produced [[ART-SAP]]. Reused: the DT-2 developmental test results (PKI sign-in through the
identity service on 12 of 12 units, event delivery to the SIEM within one minute, port scans
from both interfaces) for ia-2, au-2 and sc-7 [[product/test-results.md#dt-2]]
[[INT-025.A2]]; the assessor-witnessed 2026-09-30 SRG/STIG scan for cm-6 [[ART-STIG]]
[[INT-025.A1]]; the 2026-09-12 account review record for ac-2
[[product/test-results.md#account-review]]; and the program's 2026-09-30 vulnerability scan
for si-2 [[product/test-results.md#vuln-scan]]. Team-produced (simulated, on two
pre-production units, no testing on live networks): a sample PKI sign-in and port scan
re-test, which matched DT-2; a maintenance-port sign-in as `fieldtech`, whose audit records
named only the shared account; and a repeated credentialed vulnerability scan, clean on the
current bundle [[INT-026.A1]] [[INT-026.A2]] [[INT-026.A3]].

## Findings overview

- **FND-004 (si-2, high, open).** Fielded units are patched only at quarterly site visits,
  so security-relevant updates are not installed within the 30 days the SSP sets. At the
  2026-09-30 scan two units ran the 63-day-old 2026-07 bundle with 4 high and 9 medium
  vulnerabilities, and STIG finding STG-001 is open [[INT-026.A3]] [[INT-027.A3]]
  [[product/test-results.md#vuln-scan]].
- **FND-003 (ia-2, moderate, open).** About 10 field technicians share the local account
  `fieldtech` on the maintenance port, so they are not uniquely identified; STIG finding
  STG-004 is open [[INT-026.A1]] [[INT-027.A1]] [[ART-STIG]].
- **FND-001 (ac-2, moderate, open).** For the same reason, privileged use of `fieldtech`
  cannot be attributed to a person in the audit records [[INT-023.A2]]
  [[product/test-results.md#account-review]].
- **FND-002 (ac-2, moderate, open).** The `fieldtech` password changes only on a 90-day
  rotation, not when a technician leaves the group [[INT-023.A2]]
  [[product/conops.md#limitations]].

FND-001, FND-002 and FND-003 share one root cause, the shared maintenance account; each
needs its own POA&M item in A-6 [[INT-023.A2]] [[INT-026.A1]].

## Recommendations

- FND-004: update the two overdue units at an unscheduled site visit now, deliver remote
  update over the uplink (release 2.2, planned 2026-12) and close STG-001; until then track
  each unit past 30 days as its own POA&M item and report monthly to the ISSM
  [[INT-026.A3]] [[INT-027.A3]].
- FND-001 and FND-003: replace `fieldtech` with per-technician local accounts with
  smart-card login (release 2.3, planned 2027-03) and close STG-004; until then keep a
  site-visit log naming the technician for each maintenance session and reconcile it with
  the audit records [[INT-023.A2]] [[INT-027.A1]].
- FND-002: change the `fieldtech` password whenever a technician leaves, with a record of
  each change, until release 2.3 removes the account [[INT-023.A2]].
