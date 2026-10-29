---
artifact_id: ART-AODM
run_id: agent-skeleton
produced_by_task: R-4
touched_by: [R-4]
sources: [ART-RAR, ART-POAM, ART-ORG-CONTEXT, INT-033.A1, INT-033.A2, INT-033.A3, INT-033.A4]
---
# Authorization decision

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

## Decision

On 2026-10-29 the Authorizing Official (PER-AO) issued an **Authorization to Operate with
Conditions** (AD-ATOC), recorded in `artifacts/data/decision.yaml`; the decision was not
delegated [[INT-033.A1]] [[INT-033.A2]]. This is a draft produced in a synthetic run, not a
real authorization.

## Terms and conditions

The authorization holds only while these conditions are met by their due dates
[[INT-033.A2]]:

- **COND-01** (due 2026-11-20): the two overdue units updated and rescanned (POAM-005,
  POAM-006); no unit past 30 days without its own POA&M item.
- **COND-02** (due 2027-01-31): remote update in use on all units and STG-001 closed
  (POAM-004); the new update flow is approved by the AO before it is enabled [[INT-004.A3]].
- **COND-03** (due 2026-11-30): interim controls for the shared fieldtech account, the
  monthly site-visit log reconciliation and the out-of-cycle password change (POAM-001,
  POAM-002).
- **COND-04** (due 2027-03-31): per-technician accounts in release 2.3 on all units,
  fieldtech disabled and STG-004 closed (POAM-001, POAM-003).

The ISSM reports POA&M status to the AO monthly [[INT-033.A3]].

## Authorization termination date

The authorization terminates on 2027-10-29, one year after the decision and within the
Component's 3-year maximum. The AO chose the shorter term because the system is in
development with three partially implemented controls, and wants a new look once the
conditions are closed and a broader assessment is done [[INT-033.A3]] [[ART-ORG-CONTEXT]].

## Basis for the decision

The AODR determined the overall risk as moderate: RSK-001 (unattributable on-site use of the
shared account) and RSK-003 (fielded units behind on updates) are moderate, RSK-002 is low
[[ART-RAR]]. The AO relied on the independent assessment and on the POA&M, which funds and
schedules a fix for every open finding, FND-001 to FND-004 and STIG findings STG-001 and
STG-004 (both CAT II; no CAT I is open) [[ART-POAM]] [[INT-033.A1]]. The mission needs the
alarm feed to installation security operations [[INT-033.A1]].

## Residual risk accepted

The AO accepts **moderate** residual risk on behalf of the Component's installation
security mission, within the Component's tolerance; no Component CIO concurrence is needed
[[INT-033.A1]] [[ART-ORG-CONTEXT]]. The AO will downgrade or revoke the authorization if the
per-unit updates miss 2026-11-20, the remote-update date slips without an accepted plan, or a
CAT I STIG finding opens without a POA&M item, because the patching risk would then be high
and need CIO concurrence [[INT-033.A4]].

## Disclosures

No reference is degraded for this run. The categorization still rests on assumption ASM-002
(no PII in scope pending the privacy office); if the privacy office finds otherwise, this
decision is reopened [[INT-033.A4]] [[ASM-002]].
