---
artifact_id: ART-AODM
run_id: agent-cold-start-resume
produced_by_task: R-4
touched_by: [R-4]
sources: [ART-RAR, ART-POAM, ART-PKG, ART-ORG-CONTEXT, INT-026.A3, INT-027.A1, INT-027.A2]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Decision

On 2026-10-30 the AO (PER-AO) issued an authorization to operate with conditions (AD-ATOC),
after consulting the AODR on the risk analysis [[INT-027.A1]] [[INT-026.A3]]. This is a
simulated draft decision; it does not replace a real AO's decision. The record is
`artifacts/data/decision.yaml`.

## Terms and conditions

The authorization holds only while these conditions are met [[INT-027.A2]] [[ART-POAM]]:

- COND-01 (due 2026-11-30): the November vulnerability rescan reaches the AO and shows no unit
  past the 30-day update period (POAM-003).
- COND-02 (due 2026-12-31): POAM-003 closed with release 2.2 remote update fielded.
- COND-03 (due 2026-11-15): the site-visit sign-in log and password change on departure in force.
- COND-04 (due 2027-03-31): POAM-001 and POAM-002 closed with release 2.3.

A missed condition or an unapproved POA&M slip leads the AO to reconsider the authorization, up
to denial [[INT-027.A2]].

## Authorization termination date

The authorization terminates on 2027-10-30, one year after the decision and well within the
3-year maximum, so that it is reviewed once the remediations are in place [[INT-027.A2]]
[[ART-ORG-CONTEXT]].

## Basis for the decision

The AODR determined the overall risk as moderate from two moderate risks: RSK-001 (update latency
on fielded units) and RSK-002 (the shared `fieldtech` account) [[ART-RAR]]. The AO relied on the
funded, dated remediation in POAM-001, POAM-002 and POAM-003 and on the mission need for the
system [[ART-POAM]] [[INT-027.A1]].

## Residual risk accepted

The AO accepts moderate residual risk on behalf of the Component, which allows an AO to accept
moderate risk without Component CIO concurrence [[INT-027.A1]] [[ART-ORG-CONTEXT]].

## Disclosures

No degraded references are reported for this run, so there is nothing to disclose; the si-2
rating rests on the 2026-09-30 scan pending the rescan required by COND-01 [[ART-RAR]].
