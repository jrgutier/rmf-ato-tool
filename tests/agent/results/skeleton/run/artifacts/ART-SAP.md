---
artifact_id: ART-SAP
run_id: agent-skeleton
produced_by_task: A-2
touched_by: [A-2]
sources: [INT-020.A1, INT-020.A2, INT-020.A3, INT-020.A4, INT-020.A5, INT-020.A6, INT-021.A1, INT-021.A2, INT-021.A3, INT-022.A1, INT-022.A2, ART-SSP, ART-BASELINE, product/test-results.md#dt-2]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Scope and objectives

The whole tailored baseline in the facts block is in scope, six controls (ac-2, au-2, cm-6,
ia-2, sc-7, si-2), with no exclusion (`artifacts/data/sap.yaml`) [[INT-020.A1]]
[[ART-BASELINE]]. Each control is assessed against every SP 800-53A objective, including the
tailored parameter values, to determine whether the SSP statements are implemented as described
[[INT-020.A1]] [[ART-SSP]]. For the hybrid controls au-2, ia-2 and sc-7 the team assesses the ESG
part and examines the provider's current authorization and agreement for the inherited part;
the providers themselves are not reassessed [[INT-020.A1]] [[INT-021.A1]]. All ESG components
are assessment subjects.

## Approach and methods

Every control is examined; ac-2, au-2, ia-2 and si-2 also get interviews, and every control gets
at least one test: sign-in with the shared and break-glass accounts (ac-2), event generation to
the SIEM (au-2), a witnessed SRG/STIG scan (cm-6), PKI and maintenance-port sign-in (ia-2), port
scans from both interfaces (sc-7) and a credentialed vulnerability scan (si-2) [[INT-020.A2]].
Depth is focused and coverage representative: all twelve pre-production units for scans, two
units for manual tests [[INT-020.A2]]. The partial controls ac-2, ia-2 and si-2 each get the
team's own test, not only program records [[INT-021.A2]].

## Reuse of test results

The DT-2 results (2026-08-18 to 2026-08-29) are reused for ia-2 sign-in, au-2 event delivery and
sc-7 port scans because they ran on the same units with documented test cases; the team re-runs
one PKI sign-in and one port scan to confirm them [[INT-020.A3]]
[[product/test-results.md#dt-2]]. The assessor-witnessed 2026-09-30 configuration scan is
accepted for cm-6 [[product/test-results.md#config-scan]]. The 2026-09-30 vulnerability scan and
the 2026-09-12 account review are examined as program records, and the vulnerability scan is
repeated because si-2 rests on it [[INT-020.A3]]. The SAR states for each determination which
evidence was reused and which the team produced [[INT-021.A2]].

## Team and independence

The Component assessment team performs the assessment under the CISO's delegation of the SCA
role: a lead assessor and a second assessor who runs the scans [[INT-020.A4]]. Neither reports to
the program office or the developer, and neither designed or operates an ESG control, so the
team is independent of the program [[INT-020.A4]].

## Schedule

The assessment runs from kickoff to out-brief over three weeks in November 2026: document
examination and interviews in the first week, scans and manual tests in the second, and the
out-brief with the draft SAR at the end; the dates are in `artifacts/data/sap.yaml`
[[INT-020.A5]]. This leaves time for the POA&M and the risk analysis before the authorization
decision [[INT-021.A3]].

## Rules of engagement

Testing happens only on the pre-production units at the test sites, which feed the test instance
of IODS; there is no testing on live networks without the AO's prior approval, and no
denial-of-service or exploit testing [[INT-020.A6]] [[INT-022.A2]]. Scans run from the
enclave-assigned switch port, and from the maintenance port only with a field technician present;
the ISSO and the enclave operations desk are notified 48 hours ahead, and the ISSO may stop any
test [[INT-020.A6]]. Findings are reported to the ISSM and the AODR, not fixed during the
assessment [[INT-020.A6]].

## Review and approval

The AODR reviewed the plan for the AO: no exclusions, methods deep enough for the partial
controls, reuse of DT-2 acceptable, schedule consistent with the decision; the AODR recommended
approval with one condition, that the SAR separates reused from team-produced evidence
[[INT-021.A1]] [[INT-021.A2]] [[INT-021.A3]]. The AO approved the plan personally with that
condition and with no testing on live networks [[INT-022.A1]] [[INT-022.A2]].
