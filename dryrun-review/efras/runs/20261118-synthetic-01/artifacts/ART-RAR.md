---
artifact_id: ART-RAR
run_id: 20261118-synthetic-01
produced_by_task: R-2
touched_by: [R-2, R-3, M-3]
sources: [ART-SAR, ART-POAM, ART-RA, ART-PKG, ART-ORG-CONTEXT, INT-186.A1, INT-186.A2, INT-187.A1, INT-188.A1, INT-189.A1, INT-190.A1, INT-191.A1, INT-191.A2, INT-192.A1, INT-192.A2, INT-193.A2]
---
# Risk assessment report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
<!-- END rmf:facts -->

## Method

The AODR analyzed the package as submitted on 2026-12-14 for the AO [[ART-PKG]]. The 24 open
assessment findings and the two open CAT II STIG findings were grouped by the threat event they
share in the updated risk assessment, as the ISSM advised [[INT-187.A1]] [[ART-RA]]. Each risk's
likelihood and impact were taken from the threat events of `ra.yaml`, adjusted by the SCA's
account of exploitability and the compensating factors seen in the assessment [[INT-186.A1]]
[[INT-186.A2]], and the level read from SP 800-30 Table I-2 [[INT-191.A1]]. Residual levels are
those expected once the POA&M mitigations are in place. The records are in
`artifacts/data/rar.yaml` (RSK-001 to RSK-010) [[ART-POAM]].

## Risks

Four risks are moderate (moderate likelihood, moderate impact) and six are low; none is high
[[INT-191.A1]].

- **RSK-001, re-identification of maintainers** (FND-018, FND-020; POAM-001, POAM-010). The
  unsalted DoD ID hash in exports and the training extract was exploited in the penetration test
  with 50 ID numbers; with real data the harm to about 30,000 maintainers would be certain once an
  export and a roster meet. The PIA is not approved [[INT-186.A1]] [[INT-189.A1]].
- **RSK-002, exploitation of the unpatched report container** (FND-019, FND-024, FND-021;
  POAM-002, POAM-003, POAM-017). Two public high vulnerabilities, past the 30-day remediation
  time, reachable by any signed-in user; the fix has slipped twice on the software factory's base
  image. The renderer's lack of outbound access limits the effect [[INT-186.A1]] [[INT-187.A1]].
- **RSK-003, leavers keep access** (FND-001, FND-017; POAM-004, POAM-005). No leaver notice
  reaches the account manager, so a departed maintainer can read readiness data and maintainer
  records for up to 35 days [[INT-186.A2]].
- **RSK-004, insecure or drifting configuration** (FND-007, FND-013, FND-008, FND-009, STG-001,
  STG-002; POAM-006, POAM-007, POAM-008, POAM-021). Two database STIG settings are open, the
  containers have no documented configuration and the inventory missed a release; signed images
  limit what runs, not how it is set [[INT-186.A2]] [[INT-187.A1]].

The low risks are RSK-005 (regional outage with untested recovery plans; availability impact is
low), RSK-006 (EMIS on an interim approval), RSK-007 (break-glass without CAC), RSK-008 (sandbox
egress unretested), RSK-009 (90-day audit retention) and RSK-010 (monitoring and recurring
assessment not started) [[INT-191.A1]].

## Risk determination

The AODR determined on 2026-12-21 that the overall risk is **moderate**, the highest level of any
risk; no combined mitigation lowers it today [[INT-191.A2]]. The determination was finalized with
the CISO and the Component privacy officer, on the ISSM's technical advice [[INT-188.A1]]
[[INT-189.A1]] [[INT-187.A1]]. Against the organizational risk tolerance: moderate is within the
tolerance for mission operations and organizational assets, but RSK-001 and RSK-003 are moderate
harm to individuals, whose tolerance is low, so they are acceptable only while no production
maintainer data is in the system [[ART-ORG-CONTEXT]] [[INT-189.A1]]. The risk executive
(function) added that the software factory dependency is a shared portfolio risk and that it
prefers a conditioned authorization to a slipped fielding [[INT-190.A1]].

## Recommended responses

Mitigate RSK-001 to RSK-006 and RSK-008 to RSK-010 through their POA&M items; accept RSK-007,
which has no fix, with its compensating measures [[INT-191.A2]]. Any authorization should carry
conditions that keep production maintainer data out until RSK-001 and RSK-003 are mitigated and
the PIA approved [[INT-191.A2]] [[INT-189.A1]]. No risk reaches high, so no Component CIO
concurrence is needed, and no very high privacy risk needs the privacy officer's acceptance
[[ART-ORG-CONTEXT]] [[INT-188.A1]].

## Risk Response (R-3)

On 2026-12-22 the AODR weighed courses of action under the Component's risk response strategy,
comparing each with the tolerance and the cost [[INT-192.A1]] [[ART-ORG-CONTEXT]]. For the four
moderate risks two courses were weighed and mitigation selected: avoiding RSK-001 by dropping the
DoD ID from exports would break the mission's qualification joins; accepting RSK-001 or RSK-003 is
outside the low tolerance for individuals; avoiding RSK-002 by switching off PDF and slide exports
is kept as the fallback if the report container misses its date; accepting RSK-004 leaves drift
invisible [[INT-192.A1]]. Each low risk has one course evaluated as adequate; RSK-007
(break-glass) is accepted with its compensating measures, the decision being the AO's
[[INT-192.A2]]. Each risk's `selected_response` in `rar.yaml` names who is responsible, the
effectiveness criteria, dependencies, timeline, monitoring, triggers (a missed milestone, a new
finding on the weakness, a change in threat), interim measures and who is told [[INT-192.A2]].
The squadron maintenance officers and the information owner receive a notice of the risks not
fully mitigated at the decision: the unpatched report container, the EMIS feed held back until
the agreement is signed, and untested regional recovery [[INT-193.A2]]. The decision authority's
determination fixes only the deployment date and accepts no security risk [[INT-193.A2]].

## Ongoing Risk Response (M-3)

On 2027-02-01, after the first monitoring cycle, the PM and the ISSM made these changes
[[INT-210.A1]] [[INT-211.A1]]:

- **FND-025 joins RSK-004.** The console role that let a security group change bypass change
  control is a configuration-drift weakness. RSK-004's selected course of action, mitigate (COA-01),
  now also covers a read-only network console role with a break-glass path (POAM-025). The
  alternative stays as weighed at R-3: accepting the weakness leaves drift to detection alone.
  RSK-004 keeps its moderate level, and POAM-025 takes that level [[INT-209.A1]] [[INT-211.A1]].
- **The medium vulnerability on INV-016 is not a risk of its own.** It is analysed and tracked as
  VUL-001 and POAM-026 [[INT-210.A1]] [[INT-210.A2]].
- **Three timelines are past.** RSK-001 (2027-01-25), RSK-003 (2027-01-22) and RSK-004
  (2027-02-01) have their milestones recorded as met under ASM-025, but no record shows their
  effectiveness criteria met, and the SCA has verified none. The responses go back to R-3's
  implementation, and the residual levels are not claimed. The timelines move to COND-01
  (2027-02-26) and COND-05 (2027-03-31) [[INT-211.A3]].
- **RSK-002 is not yet carried out.** It is due 2027-02-15 under COND-02. If that date is missed,
  the fallback weighed at R-3 applies: exports are switched off [[INT-211.A3]].
- **No new risk is accepted** [[INT-211.A3]].

The PM reports the state of each of the AO's six conditions in the monthly status report (M-5)
[[INT-211.A2]]:

| Condition | Due | State on 2027-02-01 |
|---|---|---|
| COND-01 | 2027-02-26 | Privacy review of release 1.6 done. Pseudonyms, the approved PIA and the leaver step are not yet verified by the SCA |
| COND-02 | 2027-02-15 | Report container not rebuilt; waits on the factory's intermediate image |
| COND-03 | 2027-03-05 | Memorandum with EMIS in legal review; no real EMIS records flow |
| COND-04 | 2027-03-01 | Tabletop (2027-02-12) and failover test (2027-02-26) planned |
| COND-05 | 2027-03-31 | Fixes said to be in release 1.6; no rescan yet |
| COND-06 | 2027-02-28 | First monthly roll-up not yet compiled (M-5) |

None of the conditions is met or overdue.
