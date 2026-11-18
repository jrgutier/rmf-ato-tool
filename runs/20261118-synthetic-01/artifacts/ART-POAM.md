---
artifact_id: ART-POAM
run_id: 20261118-synthetic-01
produced_by_task: A-6
touched_by: [A-6, R-3]
sources: [ART-SAR, ART-STIG, ART-RA, ART-ORG-CONTEXT, INT-180.A1, INT-180.A2, INT-180.A4, INT-180.A5, INT-181.A1, INT-181.A3, INT-182.A1, ASM-024]
handling: CUI  # at a minimum CUI, or the classification level of the system (DoDI 8530.01)
---
# Plan of action and milestones

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

## How items were derived

Every finding the assessment left open became one item: FND-001 to FND-024 from the family
results, none closed at remediation and none triaged inconsequential or a false positive, so 24
items, POAM-001 to POAM-024, in `artifacts/poam/items.yaml` [[ART-SAR]]. The STIG summary has no
CAT I finding; its two open CAT II items are the same control and weakness as two SAR findings, so
they are named in those items' comments rather than given items of their own: STG-001 in POAM-006
(cm-6) and STG-002 in POAM-007 (ia-5). STG-003 to STG-006 are the cloud provider's settings, not
open program findings [[ART-STIG]]. FND-012 is carried as an item whose action is the AO's risk
acceptance of the break-glass deviation, since no fix is planned [[INT-181.A4]]. The ISSM enters
the items in eMASS by 2026-12-18 and updates them monthly; a missed milestone keeps its date and
gets a recorded change [[INT-181.A1]].

## Prioritization

Items are ranked by risk level first, then by the order of the risk assessment's summary, which
puts harm to individuals ahead of integrity and future harm [[ART-RA]]. The nine moderate items
come first: the re-identifiable exports (POAM-001, under the top risk TE-02), the image library
vulnerabilities that set the system risk (POAM-002, POAM-003), the leaver access to PII (POAM-004,
POAM-005), the two STIG settings (POAM-006, POAM-007), the container configuration (POAM-008) and
the untested failover (POAM-009). The 15 low items follow, privacy and agreements first (POAM-010,
POAM-011), then plans, verification, retention, the deviation, the inventory and the monitoring
items that can only start after the decision (POAM-012 to POAM-024). Each item's risk level is its
finding's severity until R-2 links it to a risk in the risk assessment report [[ART-RA]]
[[ART-SAR]]. No item is high, so none needs the Component CIO's concurrence before an
authorization [[ART-ORG-CONTEXT]].

## Remediation approach and resources

- **Release 1.5.2** (planned 2026-12-10) carries POAM-002, POAM-003, POAM-006 and POAM-007 and the
  rescan in POAM-017. It did not ship: the software factory's hardened base image is late, an open
  item on the factory's own POA&M with no committed date. The five items are `delayed` with the
  dependency named; their original dates stay and each records a new date of 2027-01-15, when the
  fixes ride with release 1.6 at the latest. The factory can supply a patched intermediate image
  if the program asks [[INT-180.A1]] [[INT-182.A1]] [[ASM-024]].
- **Release 1.6** (2027-01-15) carries the salted pseudonyms (POAM-001, retested 2027-01-20), the
  archive tier (POAM-019), the container baseline (POAM-008) and the DT checks for REQ-11 and
  REQ-12 (POAM-018); ERST builds it under the current contract [[INT-180.A2]].
- **Approvals and agreements**: the PM approves the three plans on 2026-12-15 (POAM-012 to
  POAM-014), the EMIS agreement is signed by 2026-12-31 (POAM-011), and the PIA is approved on
  2027-01-25 after release 1.6 (POAM-010) [[INT-180.A4]] [[INT-181.A3]].
- **Exercises**: the tabletop on 2027-02-12 and the failover test on 2027-02-26, funded in the
  sustainment line (POAM-009, POAM-015) [[INT-180.A4]].
- **Procedures** owned by the ISSM and ISSO with staff time only: the leaver step (POAM-004,
  POAM-005), the inventory (POAM-021) and the monitoring items (POAM-022 to POAM-024)
  [[INT-181.A3]].

Seventeen items are recommended for completion before the authorization decision, all dated by
2027-01-25, ahead of the decision the PM needs before the 2027-02-01 deployment; the seven others
(POAM-009, POAM-015, POAM-019 and POAM-021 to POAM-024) follow it [[INT-180.A5]].

## Items beyond the organizational remediation period

None. The Component's periods are 90 days for a moderate finding and 180 days for a low one,
counted from the finding [[ART-ORG-CONTEXT]]. The latest moderate item, POAM-009, completes on
2027-03-01, within 90 days of its finding on 2026-12-02, and the latest low item, POAM-024, on
2027-04-30, within 180 days of 2026-11-20. The delayed release 1.5.2 items keep within the
period even at their new date of 2027-01-15. Their image library vulnerabilities are, however,
already past the 30-day flaw remediation time for high vulnerabilities, which is why FND-024 exists
[[INT-180.A1]] [[ART-SAR]].

## Risk Response (R-3)

R-3 linked every item to its risk in ART-RAR and took the risk level from the RAR: POAM-009 is
now low (RSK-005, availability impact low) and POAM-010, POAM-017 and POAM-021 moderate (RSK-001,
RSK-002, RSK-004); priorities were re-ranked so the eleven moderate items come first
[[ART-RAR]] [[INT-192.A1]]. The progress to the decision day, 2027-01-25, is recorded milestone
by milestone under one stated rule (ASM-025): milestones were met on their planned dates except
where an outside obstacle was named [[ASM-025]] [[INT-193.A1]] [[INT-194.A1]].

- Met: release 1.6 on 2027-01-15 with the pseudonyms, the archive tier, the container baseline
  and the two PostgreSQL settings (POAM-001, -006, -007, -008, -019, -021); the re-identification
  retest of 2027-01-20 and the PIA approval of 2027-01-25 (POAM-001, POAM-010); the plan
  approvals of 2026-12-15 (POAM-012 to POAM-014); the leaver step and its first sample
  (POAM-004, POAM-005); the egress retest and probe (POAM-016, POAM-017's egress ticket); REQ-11
  and REQ-12 (POAM-018); eMASS entry and the first monthly update (POAM-023); the break-glass
  deviation submitted in the package (POAM-020) [[INT-193.A1]] [[INT-194.A1]].
- Slipped: the rebuilt report container, still waiting on the software factory, to 2027-02-15
  (POAM-002, POAM-003, POAM-017), and the EMIS memorandum, in the EMIS program's legal review, to
  2027-02-26 (POAM-011, now delayed) [[INT-193.A1]].

No item is completed or closed: the SCA has verified none of the fixes, so the findings stay
open until the first ongoing assessment [[INT-193.A1]]. POAM-020 stays open for the AO's decision
on accepting RSK-007 [[INT-192.A2]].
