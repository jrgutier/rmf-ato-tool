---
artifact_id: ART-POAM
run_id: example-synthetic-01
produced_by_task: A-6
touched_by: [A-6, R-3, M-3]
sources: [ART-SAR, ART-STIG, INT-098.A1, INT-098.A2, INT-098.A3, INT-099.A1, INT-099.A2, INT-099.A3, INT-102.A1, INT-103.A1, INT-112.A2, INT-112.A3, INT-113.A1, INT-113.A3]
---
# Plan of action and milestones

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## How items were derived

Every open SAR finding has one item: POAM-001 to POAM-069 remediate FND-001 to FND-069 in
order, 38 moderate and 31 low, none high or very high [[ART-SAR]]. The STIG summary has two
open CAT II findings, STG-001 and STG-002, on the shared `gcsmaint` account under ia-2; they are
the same control and weakness as FND-027, so POAM-027 names them instead of adding items. There
are no open CAT I findings; STG-003 to STG-005 are not reviewed rather than open and are covered
by POAM-021, the SRG check item [[ART-STIG]]. The records live in `artifacts/poam/items.yaml`.

## Remediation approach and resources

- **Release 2.4** (funded, existing contract staff, fielded by 2027-03-31) closes the
  shared-account items POAM-001, POAM-003, POAM-004, POAM-006, POAM-009, POAM-019, POAM-020,
  POAM-027 to POAM-035, POAM-043, POAM-047, POAM-048 and POAM-060, and the log items POAM-002,
  POAM-005, POAM-007, POAM-008, POAM-013, POAM-041, POAM-042, POAM-050, POAM-057 and POAM-064 to
  POAM-066. Interim measures: a named custodian and a new GDT administrator password by
  2026-11-30, and log export and review at each reconnect from 2026-11-16 [[INT-098.A1]].
- **2026-12 bundle** with GDT firmware 5.2.1 and a rescan by 2027-01-15 closes POAM-054,
  POAM-062 and POAM-063; the planner library findings with no vendor fix go to AO risk
  acceptance at R-3 [[INT-098.A2]].
- **Developer SRG checks and planner security guide** by 2027-01-29: POAM-021, POAM-059,
  POAM-061, POAM-068 [[INT-098.A2]].
- **ISSM-owned plans, training and exercises**: tabletops the week of 2026-11-16, plans signed by
  2026-12-18, training by 2027-01-29 (POAM-022 to POAM-026, POAM-036 to POAM-040, POAM-044 to
  POAM-046) [[INT-099.A1]].
- **Agreements, privacy and monitoring start-up**: IC-1 and the privacy threshold analysis
  signed by 2026-12-15 (POAM-010, POAM-051 to POAM-053, POAM-056); this POA&M and the decision
  answer POAM-011, POAM-012 and POAM-055; the first monitoring cycle by 2027-02-26 closes
  POAM-014 to POAM-018; the weekly privileged review starts 2026-11-16 (POAM-067). The ISSM
  tracks every item monthly and reports open counts to the AO [[INT-099.A2]]. POAM-049 is
  documentation by the ISSE by 2027-06-30, inside the 365-day period for low items
  [[INT-099.A3]].

## Items beyond the organizational remediation period

POAM-058 and POAM-069 (moderate, planner end of support) are scheduled for 2027-06-30, about
two months past the 180-day period for moderate items. The PM requests a milestone extension: a
replacement planner cannot be selected (2027-01-29), integrated and tested faster, and release
3.0 needs funding requested in the 2027 budget review [[INT-098.A3]]. Every other item is within
its period [[INT-098.A1]] [[INT-099.A1]].

## Risk Response (R-3)

Every risk in `artifacts/data/rar.yaml` (RSK-001 to RSK-009) has the response `mitigate`, and
each of its findings already has an item here with dated milestones and resources, so no item
in `artifacts/poam/items.yaml` changed [[INT-102.A1]]. The PM commits to the items and to the
interim measures: named custodian and new GDT administrator password by 2026-11-30, log export
and review at each reconnect from 2026-11-16, the GDT management service kept on the isolated
station segment, and planner data loaded only through signed bundles with the planner on the
station segment only [[INT-103.A1]]. The planner library flaws without a vendor fix (part of
POAM-054 and POAM-063) cannot be mitigated before the planner is replaced; that residual risk
goes to the AO for explicit acceptance with the decision [[INT-102.A1]].

## Ongoing Risk Response (M-3)

Updates from the first monitoring cycle (M-2), written into `artifacts/poam/items.yaml`
[[ART-SAR]] [[INT-112.A2]]:

- **Completed:** POAM-055, because the SCA closed FND-055 (ra-7). POAM-011 (ca-5, same
  weakness) stays ongoing until the SCA closes FND-011 [[INT-112.A2]].
- **Progress noted, still open:** POAM-007 and POAM-064 (the interim weekly hand review of
  planner and GDT logs ran every week, on test-range stations only); POAM-067 (four
  consecutive weekly reviews, fielded stations not covered); POAM-054, POAM-062 and POAM-063
  (descriptions narrowed to the GDT firmware and planner library flaws after the 2026-10-24
  rescan confirmed the workstation and router fixes) [[INT-112.A2]].
- **Recurrence noted:** POAM-019, the unattributable 2026-10-14 change under `gcsmaint`; POAM-032
  notes that GDT administrator passwords are unique per station, which limits reach but does
  not close the finding [[INT-112.A2]] [[INT-112.A3]].
- **Delayed remediation:** the GDT firmware fix stays in the 2026-12 bundle; the PM coordinated
  that delay with the requirements sponsor's representative, the AODR and the CSSP, and the
  internal-network-only restriction stays [[INT-113.A1]].

No new item, no new finding and no date change: no milestone fell due in the cycle, release 2.4
is still fielded by 2027-03-31, and the extension request for POAM-058 and POAM-069 stands
[[INT-113.A3]]. Open items: 68 (POAM-055 completed).
