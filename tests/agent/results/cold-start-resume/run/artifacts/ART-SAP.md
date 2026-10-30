---
artifact_id: ART-SAP
run_id: agent-cold-start-resume
produced_by_task: A-2
touched_by: [A-2]
sources: [INT-017.A1, INT-017.A2, INT-017.A3, INT-017.A4, INT-018.A1, INT-019.A1, ART-SSP, ART-BASELINE]
---
# Security assessment plan

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

## Scope and objectives

The whole tailored baseline is in scope, all six controls, with no exclusions; the objective is
to determine for each control whether the implementation described in the SSP is in place,
operating as intended and producing the desired outcome [[INT-017.A1]] [[ART-BASELINE]]. For the
three partially inherited controls (au-2, ia-2, sc-7) only the ESG side is assessed; the
providers' parts rest on their current authorizations [[INT-017.A1]] [[ART-SSP]]. Scope, team and
schedule are recorded in `artifacts/data/sap.yaml`.

## Approach and methods

Every control is examined (SSP statement, configuration and records) and its owner interviewed.
Test is added for each technical control: sign-in and lockout for ac-2 and ia-2, event delivery to
the SIEM for au-2, the configuration scan for cm-6, a port scan for sc-7 and the vulnerability
scan for si-2. Depth is focused, and the scans cover all twelve units [[INT-017.A1]].

## Reuse of test results

DT-2 results (sign-in, lockout, session lock, audit delivery, port scan) are reused because the
event ran on the production configuration and the raw logs are available; the assessor-witnessed
2026-09-30 configuration scan is reused for cm-6. The 2026-09-30 vulnerability scan and the
2026-09-12 account review are reused as evidence, and the vulnerability scan is rerun during the
assessment to establish the current patch state [[INT-017.A2]].

## Team and independence

The lead assessor (PER-SCA) comes from the SCA organization, which reports outside the program
office, so the team is independent of the program; a second assessor from that office runs the
scans [[INT-017.A3]].

## Schedule

Kickoff, interviews, scans and the out-brief fall in November 2026, after the reused DT-2 event;
the dates are in `artifacts/data/sap.yaml` [[INT-017.A4]].

## Rules of engagement

Scans and tests run only on the pre-production units at the test sites, in a window agreed with
the ISSO, who is notified 48 hours ahead and may stop any test. There is no testing on
installation networks or provider systems and no change to unit configuration [[INT-017.A4]].

## Review and approval

The AODR reviewed the plan and accepted its scope (no exclusions), the sufficiency of test for the
technical controls and the schedule against the authorization milestone [[INT-018.A1]]. The AO
approved the plan with one constraint: the assessment report must name the shared `fieldtech`
account and the update-latency findings, with the current scan results [[INT-019.A1]].
