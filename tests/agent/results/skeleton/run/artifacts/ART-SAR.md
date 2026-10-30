---
artifact_id: ART-SAR
run_id: agent-skeleton
produced_by_task: A-3
touched_by: [A-3]
sources: [ART-SAP, ART-SSP, ART-STIG, INT-020.A1, INT-020.A2, INT-020.A3, INT-021.A1, INT-021.A2, INT-021.A3, INT-022.A1, product/test-results.md#dt-2, product/test-results.md#config-scan, product/test-results.md#vuln-scan, product/test-results.md#account-review]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Assessment summary

The independent assessor (PER-SCA) assessed all six controls of the tailored baseline as the
approved plan sets out, examining records and configuration, interviewing the control owners
and testing every technical control [[ART-SAP]]. Interviews covered the ISSO for operations
[[INT-020.A1]], the developer for built-in mechanisms [[INT-021.A1]] and the common control
provider for the inherited parts [[INT-022.A1]]. The result mix is 3 satisfied (au-2, cm-6,
sc-7) and 3 other-than-satisfied (ac-2, ia-2, si-2), with 3 open findings; the determinations
are recorded per family in `artifacts/sar/results/`. Each other-than-satisfied control matches
a gap the SSP already marked as partial [[ART-SSP]]. The vulnerability scan rerun that the plan
foresees for November 2026 is not yet in the evidence, so the patch determination rests on the
2026-09-30 scan [[ART-SAP]] [[product/test-results.md#vuln-scan]].

## Test results reused

- DT-2 (2026-08-18 to 2026-08-29): PKI sign-in and refusal of unapproved users, local lockout,
  session lock, audit delivery to the SIEM on 12 of 12 units, and port scans showing only the
  documented ports with no routing between ports; reused for ac-2, ia-2, au-2 and sc-7
  [[product/test-results.md#dt-2]] [[INT-021.A2]].
- The assessor-witnessed 2026-09-30 SRG/STIG scan: approved baseline on all 12 units, no drift in
  August and September 2026; reused for cm-6 and sc-7, and to confirm STG-001 and STG-004 open
  [[product/test-results.md#config-scan]] [[INT-020.A3]] [[ART-STIG]].
- The 2026-09-30 vulnerability scan: 10 units current and clean, 2 units behind; reused for si-2
  [[product/test-results.md#vuln-scan]].
- The 2026-09-12 quarterly account review; reused for ac-2 [[product/test-results.md#account-review]].

## Findings overview

- **FND-003 (high, si-2):** esg-north-01 and esg-ridge-01 ran a 63-day-old update bundle against
  the 30-day installation period, with 4 high and 9 medium vulnerabilities that later bundles fix;
  STG-001 is open [[INT-021.A3]] [[product/test-results.md#vuln-scan]].
- **FND-001 (moderate, ac-2):** the shared `fieldtech` account used by 10 technicians cannot be
  attributed to a person and its password is not changed when a technician leaves the team
  [[INT-020.A1]] [[product/test-results.md#account-review]].
- **FND-002 (moderate, ia-2):** for the same reason, technicians on the maintenance port are not
  uniquely identified; STG-004 is open [[INT-021.A1]].

As the AO required when approving the plan, the shared `fieldtech` account and update latency
are both named here with the latest scan results [[ART-SAP]].

## Recommendations

- FND-003: deliver remote update over the uplink in release 2.2 (planned 2026-12); until then,
  make out-of-cycle site visits so no unit runs a bundle older than 30 days, starting with the
  two lagging units [[INT-021.A3]].
- FND-001 and FND-002: deliver per-technician accounts with smart-card login in release 2.3
  (planned 2027-03); until then, keep a site-visit log tying each `fieldtech` session to a named
  technician and change the password whenever a technician leaves the team [[INT-020.A1]]
  [[INT-021.A1]].
- All three findings need POA&M items (A-6) and should be rescanned once the fixes ship
  [[ART-SAP]].
