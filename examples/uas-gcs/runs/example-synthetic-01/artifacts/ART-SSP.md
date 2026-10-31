---
artifact_id: ART-SSP
run_id: example-synthetic-01
produced_by_task: S-4
touched_by: [S-4, S-6, I-2, A-5]
sources: [INT-096.A1, INT-096.A2, INT-097.A1, INT-060.A2, INT-060.A3, INT-061.A1, INT-063.A1, INT-063.A2, INT-063.A3, INT-064.A1, ART-STIG, INT-053.A1, INT-053.A2, INT-054.A1, INT-054.A2, INT-055.A1, INT-056.A1, INT-059.A1, INT-059.A2, INT-059.A3, ART-CONMON, product/architecture.md#boundary, product/architecture.md#leveraged, product/architecture.md#configuration, product/architecture.md#updates, product/conops.md#limitations, product/test-results.md#dt-1, product/test-results.md#vuln-scan]
---
# System security plan

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

## Approach to control implementation

Every control in `baseline.json` has one statement in `artifacts/ssp/controls/<family>.yaml`,
written against the components that `artifacts/data/allocation.yaml` assigns to it. All
stations share one configuration baseline and are planned as one type-authorized system
[[product/architecture.md#boundary]]. The controls rest on four mechanisms: the hardened
workstation image and router configuration checked at every start-up and before each mission
upload [[product/architecture.md#configuration]]; the integrator's signed quarterly update
bundle, the only path for code and firmware [[product/architecture.md#updates]]
[[INT-055.A1]]; CAC sign-in against the brigade directory with ISSO-approved role groups; and
a router that denies everything except four named brigade services [[INT-053.A1]]. Each
statement records the honest state today: a disclosed limitation makes the control `partial`,
and work that has not started is `planned` [[product/conops.md#limitations]].

## Inheritance and shared responsibility

**Brigade Tactical Network Enclave.** Under its ATO the enclave provides boundary protection
and intrusion detection, the brigade directory for CAC account management, central log
collection reviewed by the S6, and incident response support through its CSSP
[[product/architecture.md#leveraged]]. The station's part is to forward workstation and router
logs when connected, keep its own deny-by-default router rules and host firewall, and report
incidents to the ISSO and the CSSP [[INT-054.A2]] [[INT-053.A1]]. These controls (si-4, au-6,
ir-4 and others) are hybrid, and the planner and GDT logs are outside what the enclave sees.

**Component cybersecurity program.** The Component issues and reviews the policy and
procedure controls of every family (`-1` controls) and the program management (pm) controls,
with the privacy parts from the Component privacy program; the station follows them and the
ISSO applies them [[INT-054.A1]] [[INT-056.A1]].

## Open items

These statements are `partial` or `planned`; each names its gap and plan in the family file.

- **Shared maintenance account `gcsmaint` and the GDT vendor administrator account**
  (ac-2, ac-2.7, ac-2.9, ac-6.9, au-10, cm-5.1, cm-5.5, ia-2, ia-2.1, ia-2.5, ia-2.6, ia-4,
  ia-5, ia-5.1, ia-5.6, ia-5.8, ir-4.6, ma-2, ma-3.5, sa-8.22): maintenance actions cannot be
  tied to a person; per-maintainer accounts with offline CAC sign-in come in release 2.4,
  planned 2027-02 [[product/conops.md#limitations]] [[product/test-results.md#account-review]].
- **Mission planner and GDT logs not forwarded** (ac-2.4, ac-2.12, au-6, au-6.3, ca-7, ir-4.1,
  ir-4.4, ra-10, si-4, si-4.14, si-4.16): these components are not monitored or correlated
  centrally; forwarding is an open engineering item, and the weekly station review moves from
  test events to operational use under S-5 [[product/test-results.md#dt-1]] [[INT-054.A2]].
- **Pending fixes** (si-2, ra-5): GDT firmware 5.2.1 is scheduled for the 2026-12 bundle;
  the planner's two medium library findings have no vendor fix date
  [[product/test-results.md#vuln-scan]] [[INT-054.A1]].
- **Mission planner without a STIG or assessed hardening** (cm-6, sa-3.3, sa-5, sa-11, si-10,
  sr-3): the hand hardening is assessed in A-3; version 7 support ends 2027-06 and a
  replacement is evaluated for release 3.0 [[product/conops.md#limitations]] [[INT-056.A1]].
- **Plans and agreements not finished** (cm-9, cp-2, cp-3, cp-4, cp-4.1, ir-2, ir-2.3, ir-3,
  ir-3.2, ir-4, ir-8, ir-8.1, ir-9.2, ca-3, pl-2, pl-8.2): the CM, contingency and incident
  response plans exist as summaries, training and tests are planned before fielding, IC-1's
  interconnection agreement is unsigned, and the plan is approved in S-6
  [[product/architecture.md#interconnections]].
- **Privacy threshold analysis not approved** (pt-2, pt-3, ra-8): the privacy officer obtains
  approval before S-6 [[INT-050.A1]].
- **Authorization and monitoring not started** (ca-5, ca-6, ca-7.1, ca-7.3, ca-7.4, ca-7.5,
  ca-7.6, ra-7): planned in A-6, R-4 and the S-5 strategy. (ca-2 and ca-2.1 were assessed in
  A-3; see the A-5 section.)

## Plan Review and Approval (S-6)

**Review.** The AODR reviewed this plan, the continuous monitoring strategy (ART-CONMON) and the
system risk assessment (ART-RA). Every baseline control has a statement, the partial and planned
statements name their gaps, and the open items above map to the top risks TE-5, TE-6, TE-3 and
TE-8 [[INT-059.A1]] [[ART-CONMON]]. No residual risk in the plan is outside the AO's tolerance at
this stage [[INT-059.A3]].

**Decision.** Under the AO's written delegation, the AODR approved the security plan and the
continuous monitoring strategy for implementation and assessment, **with conditions**. This is
plan approval only; the authorization decision stays with the AO in R-4 [[INT-059.A2]].

**Conditions** [[INT-059.A2]]:

1. The privacy officer approves the privacy threshold analysis (pt-2, pt-3, ra-8) before the
   assessment plan is approved in A-2; it is still not approved.
2. The IC-1 interconnection agreement (ca-3) is signed before the station connects to the
   enclave outside test events.
3. The configuration management, contingency and incident response plans (cm-9, cp-2, ir-8) are
   completed from their summaries, and the contingency and incident response tests (cp-4, ir-3)
   are scheduled, before A-2.
4. The program sets a target date for forwarding planner and GDT logs (au-6, si-4, ca-7), so it
   becomes a dated POA&M milestone.

The AODR will watch per-maintainer accounts (release 2.4, planned 2027-02) and GDT firmware
5.2.1 (2026-12 bundle) through assessment; a slip past either date returns to the AODR
[[INT-059.A3]]. The control statements are unchanged by this review: the conditions are the open
items already recorded there.

## Update Control Implementation Information (I-2)

**As implemented.** Release 2.3.0 on the six test stations follows the approved plan; no planned
control changed during implementation, so the family statements stand as the as-implemented
description [[INT-061.A1]] [[INT-063.A1]]. The inventory matches the built stations, with GDT
firmware still at 5.1.8 [[INT-064.A1]].

**New evidence.** The STIG summary (ART-STIG) records the Windows and Network Device STIG scan of
2026-09-15 with no open CAT I rules, open CAT II findings STG-001 and STG-002 for the shared
`gcsmaint` account (ia-2, already partial), the unassessed SRG hardening of the planner and the
integrator applications (STG-003 to STG-005, cm-6, already partial), and one approved deviation,
7-day cached CAC sign-in [[ART-STIG]] [[INT-060.A2]] [[INT-060.A3]].

**Statement changed.** pl-2 moves from `partial` to `implemented`: the plan is complete, approved
with conditions in S-6 and kept current by the ISSM and ISSO [[INT-063.A1]] [[INT-059.A2]].

**S-6 conditions.** Condition 3: the CM, contingency and incident response plans are drafted and
under ISSM review, and the cp-4 and ir-3 tabletops are scheduled for the week of 2026-11-16; they
stay `partial` until signed and run [[INT-063.A2]]. Condition 4 is still open: no date is set for
planner and GDT log forwarding [[INT-063.A3]]. Conditions 1 and 2 had no new information in I-2.

## Changes from remediation (A-5)

No finding was remediated during the assessment period, so no implementation changed
[[INT-096.A1]] [[INT-097.A1]]. Four statements were corrected to match the A-3 determinations:
ca-2 and ca-2.1 moved from `planned` to `implemented` (the independent SCA team assessed the
baseline under the approved plan) [[INT-076.A2]]; pl-9 and si-4.19 moved from `implemented` to
`partial` (planner and GDT logs are not forwarded, FND-050; the privileged-activity review runs
only in test weeks, FND-067) [[INT-080.A3]] [[INT-091.A2]]. The plans and tabletops behind
condition 3 are still drafts and scheduled exercises [[INT-096.A2]]. All 69 findings go to the
POA&M at A-6.
