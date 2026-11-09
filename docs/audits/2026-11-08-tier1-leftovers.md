# Tier 1 leftovers at the freeze

Date: 2026-11-08.

What was read: every error that FW-REQ-002 reports from `uv run rmf validate --profile p13 --format json` on branch `wip/central`. The branch is feat/rmf-complete 576565f0 plus the central judge fixes C1 to C4, listed at the end. There are 249 errors: 59 tier 1 candidates and 190 tier 1 partials with no strong evidence item. Open work items and candidates outside tier 1 are only warnings at p13, so they are not listed here.

Method: each entry was grouped by the `reason` its stream wrote in `conformance/requirements/<REF>.yaml`. That reason is the stream's own classification. Keywords set the group first, and every group was then read through. When the keywords picked a weaker fit, the entry was moved by hand (31 entries, five of them on review; for example, free-text fields from "describes" to B, and the duties of DoD Component heads from C to D). An entry whose reason names several causes goes into the group of the cause that blocks it first. The order is A, F, E, D, B, then C.

## Summary

| Group | What blocks the entry | Count | Candidates | Partials without a strong item |
|---|---|---|---|---|
| A | Rule at its fan-out cap, fixture ready | 3 | 3 | 0 |
| B | Presence-only duty on a prose kind | 87 | 0 | 87 |
| C | No run record can fail it | 84 | 38 | 46 |
| D | Duty of an office a run never performs | 39 | 0 | 39 |
| E | Permission, applicability or descriptive | 12 | 3 | 9 |
| F | A rule build or mark that waits on the user's ruling | 9 | 0 | 9 |
| U | Not yet triaged (no reason recorded) | 15 | 15 | 0 |
| | Total | 249 | 59 | 190 |

## A. Rule at its fan-out cap, fixture ready (3)

**Your decision for the whole group:** Approve a split of each capped rule (RCP-004, TSTRAT-002, OCTX-001), or a fan-out exception for each, so the ready fixture can be cited. Each entry then judges strong on the named fixture.

Entries per document:

- DODCIO-RECIPROCITY (1): 0128
- DODI8510.01 (2): 0068, 0262

What each entry's reason names (the rule and fixture for A; the record that is missing for C):

| Entry | Status | Reason (shortened) |
|---|---|---|
| REQ-DODCIO-RECIPROCITY-0128 | candidate | RCP-004 fails a received system whose unchanged built-in control is re-tested (tests/fixtures/negative/RCP-004.builtin.yaml), the additional testing this forbids, but RCP-004 is at its fan-out cap of 25; ready to cite once a split or a fan-out exception frees it (WI-29). |
| REQ-DODI8510.01-0068 | candidate | TSTRAT-002 fails a test strategy whose DT or OT events have no developmental or operational evaluation framework, the frameworks that carry the DT&E and OT&E evaluation metrics (TSTRAT-002.def, TSTRAT-002.oef), but TSTRAT-002 is at its fan-out cap of 25 after T2/T3's 0168 and 0232; ready to cite once a split or exception frees it. Continuous monitoring metrics at the beginning of development are unheld (WI-15). |
| REQ-DODI8510.01-0262 | candidate | OCTX-001 fails a Component CISO designated by anyone but the Component CIO, or the Component head where no CIO exists (tests/fixtures/negative/OCTX-001.ciso.yaml), but OCTX-001 is at its fan-out cap of 25; ready to cite once a split or a fan-out exception frees it (WI-441). |

## B. Presence-only duty on a prose kind (87)

**Your decision for the whole group:** Decide whether a presence-only item counts toward the freeze for a tier 1 duty whose held part is a required field. Yes: FW-REQ-002 passes such a partial, the content remains tier 1 debt, and the gap is reported. No: each entry waits for a constraint rule (an enum, a reference to a record, or a cross-check) on its field.

One entry here is weak for another reason as well. SP800-53AR5-0274 sits under the optional `penetration_test` parent of `sap.yaml`, which is required only where ca-8 is in the baseline. So its item is weak because of that optional parent, not only because it is presence. The 53AR5-0278 to 0289 pen-test entries share that parent.

Entries per document:

- DODCIO-CATO-EVAL (10): 0040, 0065, 0124, 0126, 0128, 0137, 0138, 0142, 0004, 0056
- DODCIO-RECIPROCITY (2): 0022, 0098
- DODI5000.83 (4): 0133, 0134, 0154, 0196
- DODI8500.01 (2): 0313, 0365
- DODI8510.01 (2): 0249, 0056
- DODI8530.01 (1): 0276
- SP800-137A (1): 0052
- SP800-161R1 (46): 0011, 0081, 0082, 0210, 0262, 0264, 0273, 0285, 0286, 0287, 0325, 0569, 0679, 0682, 0691, 0696, 0704, 0713, 0721, 0723, 0731, 0903, 0980, 0996, 0997, 1082, 1083, 1090, 1123, 1163, 1238, 1298, 1313, 1315, 1320, 1321, 1322, 1330, 1544, 1554, 0107, 0151, 0199, 0261, 0333, 1393
- SP800-37R2 (3): 0504, 0505, 0533
- SP800-53AR5 (16): 0184, 0274, 0276, 0278, 0279, 0280, 0281, 0282, 0283, 0284, 0285, 0286, 0288, 0289, 0320, 0341

## C. No run record can fail it (84)

**Your decision for the whole group:** Decide whether a tier 1 partial whose reason names the missing run record may pass the freeze as tier 1 debt. Yes: the record stays on the backlog. No: approve building the records the reasons name (examples: a per-role responsibility record for the Appendix D duties, P-4/P-6 fields in org-context.yaml instead of prose, an implementation record checked against its SSP statement).

Entries per document:

- CNSSI1253 (1): 0076
- DODCIO-CATO-EVAL (4): 0021, 0066, 0106, 0144
- DODCIO-CSRMC-TENETS (1): 0003
- DODCIO-RECIPROCITY (1): 0035
- DODI8500.01 (4): 0296, 0322, 0333, 0281
- DODI8510.01 (3): 0066, 0067, 0223
- DODI8530.01 (1): 0302
- DODI8531.01 (1): 0140
- SP800-137A (2): 0075, 0354
- SP800-161R1 (9): 0078, 0269, 0281, 0624, 0709, 0913, 0914, 1265, 0947
- SP800-37R2 (44): 0313, 0326, 0329, 0120, 0172, 0177, 0178, 0190, 0205, 0207, 0215, 0242, 0250, 0254, 0314, 0325, 0371, 0376, 0406, 0458, 0465, 0471, 0482, 0484, 0485, 0487, 0499, 0514, 0515, 0527, 0535, 0537, 0539, 0550, 0558, 0656, 0691, 0692, 0693, 0694, 0697, 0720, 0244, 0730
- SP800-53AR5 (3): 0191, 0217, 0277
- SP800-53B (5): 0012, 0083, 0085, 0082, 0106
- SP800-53R5 (5): 0023, 0025, 0030, 0060, 0065

What each entry's reason names (the rule and fixture for A; the record that is missing for C):

| Entry | Status | Reason (shortened) |
|---|---|---|
| REQ-DODCIO-CATO-EVAL-0021 | nostrong | Built: the PER-DODCISO persona (consulted at M-6) and AODM-007, which refuses a cATO without dod_ciso_approval (a presence clause, which caps at partial). Unheld: who issues the cATO; AD-CATO keeps decided_by PER-AO and ... |
| REQ-SP800-37R2-0313 | nostrong | S-4 documents the implementations in ART-SSP with the privacy plan (PRIV-008); best practice and the privacy risks of security controls are prose. |
| REQ-SP800-37R2-0326 | nostrong | I-1 implements the controls of ART-SSP; nothing checks an implementation against its statement, and the engineering methodologies are prose. |
| REQ-SP800-37R2-0329 | nostrong | I-1 implements the controls of ART-SSP; nothing checks an implementation against its statement, and the engineering methodologies are prose. |
| REQ-CNSSI1253-0076 | nostrong | A removed control needs its basis in tailoring.yaml (TLR-002) and SSP-COV-001 asks a statement for each baseline control; nothing ties a control that will not be implemented to a POA&M item. |
| REQ-DODCIO-CATO-EVAL-0066 | nostrong | DASH-001 fails a dashboard that is not near real time and records no feasibility_limit; 'as near real time as feasible' lets a recorded limit pass, so the clause tests that a reason is present, not that it is true. ... |
| REQ-DODCIO-CATO-EVAL-0106 | nostrong | The assessment template submitted with the package is WI-24 |
| REQ-DODCIO-CATO-EVAL-0144 | nostrong | CATO-010 requires the additional documentation to be listed; which documents the guidebook lists is not knowable, as the Activities and Tools Guidebook is not in references/. |
| REQ-DODCIO-CSRMC-TENETS-0003 | nostrong | Qualification of RMF practitioners is held: ATEAM-001 fails an assessor with no qualification on record. 'Enhance' a role-based training program is a Component direction with no end state a run can miss. Tier 1 debt: ... |
| REQ-DODCIO-RECIPROCITY-0035 | nostrong | Tier 1, left partial: PPSM-001 refuses an Enterprise system's PPSM registration that leaves out a boundary connection, but it reads the decision's deployment scope, a field the decision types require, so covered needs ... |
| REQ-DODI8500.01-0296 | nostrong | Whether an application warrants special management oversight is judgment; the IT type fact records the result and its rationale. |
| REQ-DODI8500.01-0322 | nostrong | Whether an enterprise-level agreement is recorded per service; whether one was possible is judgment no rule can test. |
| REQ-DODI8500.01-0333 | nostrong | Tier 1, left partial: an Enterprise system registers its ports, protocols and services (PPSM-001); management under DoDI 8551.01 for every other system is not held, because DoDI 8551.01 is not in the library. |
| REQ-DODI8510.01-0066 | nostrong | PENT-002 fails an AO not provided the penetration test results; developmental, operational and sustainment T&E results reaching the AO are not tested. |
| REQ-DODI8510.01-0067 | nostrong | PENT-002 fails an AO not provided the penetration test results; other cybersecurity T&E results submitted by the program are not tested. |
| REQ-DODI8510.01-0223 | nostrong | The AO's course of action to the CIO or CISO for FISMA reporting is not recorded; downgrade and revocation are types with no test of the review |
| REQ-DODI8530.01-0302 | nostrong | boundary.yaml records the status of the sponsor's connection request fulfillment actions for a mission partner interconnection; the source sets no point by which they must be complete, so no state of the run is wrong ... |
| REQ-DODI8531.01-0140 | nostrong | Tier 1, left partial: a request for more information is recorded in details_requested when made; 'as required' leaves when to the team, so no record can fail. |
| REQ-SP800-137A-0075 | nostrong | Each metric states its objective, baseline, threshold and the baseline controls it reads (METR-001, METR-002); whether the metrics are sufficiently stable and robust to inform ongoing authorization decisions is a ... |
| REQ-SP800-137A-0354 | nostrong | the governance structures are recorded once P-7 writes the section; that policies are followed and senior leaders recognize risk is not judged |
| REQ-SP800-161R1-0078 | nostrong | SCRM-007 asks the contract's C-SCRM terms; weighing what integrators and providers implement against cost and risk is a judgment the record does not hold, and the other sentences describe. |
| REQ-SP800-161R1-0269 | nostrong | An executive-level lead (SCRM-021) shows leadership's role, not that its support was obtained; support is not something a record can show. |
| REQ-SP800-161R1-0281 | nostrong | governance.cleared names the key C-SCRM roles cleared for classified information (optional); sufficiency is a judgment. |
| REQ-SP800-161R1-0624 | nostrong | policy.informed_by lists the Level 1 policies and plans that inform a Level 2 policy (optional); no rule asks it of a Level 2 policy. |
| REQ-SP800-161R1-0709 | nostrong | Tier 1, partial: no record holds the contact details (role, name, department, phones, email) of key supply chain personnel or designated contacts; plan.relationships names each critical supplier's relationship to the ... |
| REQ-SP800-161R1-0913 | nostrong | Acting prudently and objectively, with reasonable care, is a duty of conduct on the people who assess; the record shows its trace (methodology, sources, confidence, review and clearance), but no rule can tell care from ... |
| REQ-SP800-161R1-0914 | nostrong | scrm.yaml records each Table 28 factor with the agency factor it maps to (factors.agency_factor) and any additional factors, but whether an additional factor is relevant to a use case is a judgment no rule can make, so ... |
| REQ-SP800-161R1-1265 | nostrong | The record states how results are aggregated (aggregation.method), but MECE outputs and discretion in aggregating are judgments; the other sentences describe or permit. |
| REQ-SP800-37R2-0120 | candidate | P-11 has PER-CIO, PER-SPONSOR, PER-CISO, PER-PRIV and others consulted; no record of the coordination exists for a rule to fail. |
| REQ-SP800-37R2-0172 | candidate | P-4 is optional and appends its ART-ORG-CONTEXT section in prose; no rule reads whether tailored baselines or profiles are established and made available. |
| REQ-SP800-37R2-0177 | candidate | P-6 is optional and appends its prioritization to ART-ORG-CONTEXT in prose; no rule reads the prioritization of systems within an impact level. |
| REQ-SP800-37R2-0178 | candidate | P-6 is optional and appends its prioritization to ART-ORG-CONTEXT in prose; no rule reads the prioritization of systems within an impact level. |
| REQ-SP800-37R2-0190 | candidate | P-4 is optional and appends its ART-ORG-CONTEXT section in prose; no rule reads whether tailored baselines are established, documented and published. |
| REQ-SP800-37R2-0205 | candidate | P-6 is optional and appends its prioritization to ART-ORG-CONTEXT in prose; no rule reads the prioritization of systems with the same impact level. |
| REQ-SP800-37R2-0207 | candidate | P-6 runs after categorization by its entry criteria, which no rule reads; P-6 is optional, and for NSS the high-water mark gives way to CNSSI 1253 per objective (footnote 62, 0211). |
| REQ-SP800-37R2-0215 | candidate | P-7 has PER-RE accountable, and the approval of the strategy with its minimum frequencies is asked in interview; no field records the approval, so no rule can fail its absence. |
| REQ-SP800-37R2-0242 | candidate | P-11 has PER-AO accountable and the playbook journals the AO's confirmation; no field records who determined the boundary, so no rule fails one set without the AO or the system owner's input. |
| REQ-SP800-37R2-0250 | candidate | A data map enables understanding, and system elements are identified with sufficient granularity; no rule judges granularity. |
| REQ-SP800-37R2-0254 | candidate | ART-RA '## Privacy risk' holds the privacy risk assessment in prose; no rule reads likelihood and impact on individuals or contextual factors. |
| REQ-SP800-37R2-0314 | candidate | S-4 interviews the developer, engineer and providers and every SSP record carries sources; no rule refuses one without functional specifications or implementation information. |
| REQ-SP800-37R2-0325 | candidate | I-1 implements the controls of ART-SSP; nothing in a run records an implementation against its statement for a rule to fail. |
| REQ-SP800-37R2-0371 | nostrong | PRIV-010 holds the A-5 plan update; reassessment and the report updates are the assessment cluster's (ASMT). |
| REQ-SP800-37R2-0376 | candidate | ART-RA is updated at R-2, M-3 and M-4 by the tasks' outputs; no rule fails a run whose risk assessment is not conducted as needed. |
| REQ-SP800-37R2-0406 | nostrong | PRIV-010 holds the A-5 plan update; risk response and reassessment are other items'. |
| REQ-SP800-37R2-0458 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0465 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0471 | nostrong | efficiency, cost and timeliness of security activities are outcomes no record can fail |
| REQ-SP800-37R2-0482 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0484 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0485 | candidate | PER-LSE is C on P-11 for the boundary; it is not in the S-3 raci for the allocation of controls (WI-413). |
| REQ-SP800-37R2-0487 | nostrong | the enterprise architect's assistance is conduct; integration with budgeting is recorded |
| REQ-SP800-37R2-0499 | nostrong | PER-RE is R on P-2 and OCTX-004 fails a strategy without its frame, assessment guidance or response strategy; the risk executive's part in developing it is the RACI only. |
| REQ-SP800-37R2-0514 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0515 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0527 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0535 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0537 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0539 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0550 | nostrong | scrm-plan.yaml is part of ART-SSP and so of the package manifest; what more the AO asks for is the AO's call, which no rule can foresee. |
| REQ-SP800-37R2-0558 | candidate | M-4 outputs ART-SAR and M-2 updates it; no rule fails an assessment report left unchanged after a control change. |
| REQ-SP800-37R2-0656 | nostrong | PRIV-005 has M-1 test each change for new privacy risk, so privacy risk is among the factors of significance; no record holds the organization's criteria for significant change, which other clusters own (MCHG). |
| REQ-SP800-37R2-0691 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0692 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0693 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0694 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0697 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-37R2-0720 | candidate | An Appendix D responsibility held by the persona card and the RACI; no rule fails a run whose role does not carry it. |
| REQ-SP800-53AR5-0191 | nostrong | hybrid controls and the tailoring of the contingency plan are not recorded here |
| REQ-SP800-53AR5-0217 | nostrong | PASM-002 fails the report of a system processing PII with no privacy assessment results, so the privacy assessment report is in ART-SAR in the package; the package manifest (ART-PKG) does not name the privacy plan and ... |
| REQ-SP800-53AR5-0277 | nostrong | The threat sources and attack surface frame the adversary's approach; nothing tests it. |
| REQ-SP800-53B-0012 | candidate | A run takes the baseline approach fixed by DoDI 8510.01 and CNSSI 1253: rmf baseline resolve selects the security and privacy baselines and S-2 tailors them, held by tool code FW-REQ-003 cannot cite |
| REQ-SP800-53B-0083 | nostrong | Parameter values sit in the SSP statements S-4 writes; nothing checks a statement records each assignment. |
| REQ-SP800-53B-0085 | nostrong | Specification information goes to a selected control and names its placement; whether existing control information was sufficient is judgment, and three sentences explain why specification is needed |
| REQ-SP800-53R5-0023 | nostrong | ra.yaml components records each third-party component's developer practices and any third-party validation; the run declares its components, and 'state-of-the-practice' is judgment. |
| REQ-SP800-53R5-0025 | nostrong | S-4 to S-6 plan security and privacy in ART-SSP (PRIV-008); rigor is not testable. |
| REQ-SP800-53R5-0030 | candidate | The marked sentence, a risk management process applied to manage risk on an ongoing basis, is not broken by ISCM-004's AO approval of the continuous monitoring strategy (a T5 candidate item). The cost, schedule, ... |
| REQ-SP800-53R5-0060 | candidate | Parameter values become part of the control in the OSCAL SSP (rmf build set-parameters) and A-3 assesses against the SSP as stated; tool code and prose FW-REQ-003 cannot cite |
| REQ-SP800-53R5-0065 | nostrong | how hybrid controls divide between provider and system is not recorded here; the provider's controls are |
| REQ-DODI8500.01-0281 | candidate | Tier 1, left candidate: ac-22 (publicly accessible content) carries the duty, but it binds only DoD information proposed for public Internet media; a system that publishes nothing may record ac-22 not-applicable, and no ... |
| REQ-SP800-161R1-0947 | nostrong | Analyzing what combination of factors gives rise to risk is analysis no rule can check; the second sentence is a permission. |
| REQ-SP800-37R2-0244 | candidate | Agreements with external providers are listed in ART-SD; no rule reads whether an agreement describes the authorization boundary. |
| REQ-SP800-37R2-0730 | nostrong | Privacy is among the C-SCRM policy's purpose and roles (PER-PRIV may hold one), but nothing ties SCRM practices to privacy risk when elements process PII. |
| REQ-SP800-53B-0082 | candidate | tailoring.yaml parameter actions, applied by rmf build into the OSCAL SSP, and PVAL-001 for the CNSSI 1253 minimums; the review of every assignment and selection operation is tool code and prose, and the second sentence ... |
| REQ-SP800-53B-0106 | nostrong | Built: an overlay the organization develops at P-4 is recorded in org-context.yaml developed_overlays (schema org-context; playbooks/P/P-org-context.md Task P-4). Unheld: developed_overlays is optional, since only an ... |

## D. Duty of an office a run never performs (39)

**Your decision for the whole group:** Apply decision (2) of the 2026-11-08 "Tier 1 decisions" to these entries: not-applicable with a reason naming the office. Approve the retirements records for every document whose retired share then passes 25%; the lead shows you the per-document shares before writing the records.

Entries per document:

- CNSSP12 (1): 0045
- DODCIO-CATO-EVAL (1): 0031
- DODI5000.83 (4): 0032, 0051, 0055, 0067
- DODI8500.01 (5): 0087, 0210, 0300, 0375, 0403
- DODI8510.01 (6): 0019, 0070, 0080, 0087, 0183, 0188
- DODI8530.01 (2): 0208, 0143
- DODI8531.01 (8): 0073, 0076, 0079, 0081, 0015, 0018, 0021, 0030
- SP800-161R1 (10): 0008, 0154, 0732, 0742, 0851, 0858, 0864, 0886, 0975, 0982
- SP800-37R2 (2): 0488, 0493

## E. Permission, applicability or descriptive (12)

**Your decision for the whole group:** Apply decision (3) of 2026-11-08: not-a-requirement with a reason that answers the duty words. A permission sentence gets ruling_sought, which you then approve. Approve noise records for every document that passes 50%.

Entries per document:

- CNSSI1254 (1): 0003
- DODI8500.01 (1): 0332
- DODI8510.01 (1): 0084
- SP800-161R1 (4): 0123, 0121, 0910, 1264
- SP800-37R2 (1): 0657
- SP800-53AR5 (3): 0275, 0292, 0355
- SP800-53B (1): 0062

## F. A rule build or mark that waits on the user's ruling (9)

**Your decision for the whole group:** Rule on the named sentences one by one. Each reason names the sentence that waits (a permission, an example, or whether a named path is enough). Then the lead marks the entry or builds the rule.

Entries per document:

- CNSSP12 (1): 0062
- DODCIO-CATO-IG (1): 0016
- DODCIO-RECIPROCITY (1): 0153
- SP800-137A (1): 0177
- SP800-37R2 (3): 0358, 0368, 0689
- SP800-53AR5 (1): 0272
- SP800-53B (1): 0086

## U. Not yet triaged (no reason recorded) (15)

**Your decision for the whole group:** No decision is needed from you yet. These are tier 1 candidates with no reason recorded at this commit: a stream has to triage them (or has triaged them on a branch not yet merged) before they can be grouped.

Entries per document:

- DODI8500.01 (4): 0346, 0399, 0429, 0430
- DODI8510.01 (5): 0054, 0074, 0242, 0256, 0257
- SP800-137A (2): 0065, 0090
- SP800-161R1 (1): 0236
- SP800-53AR5 (3): 0148, 0178, 0303

## The central fixes behind these counts

- **C1 (FW-REQ-002).** A tier 1 partial passes the freeze when the user has ruled out every one of its marked sentences (`ruling_sought` with `approved_by: user`). This follows FW-REQ-003, which already treats such an entry as having nothing left to prove and refuses it only as `covered`. The entries were not re-marked as `not-a-requirement`. This status choice is the lead's default, and it waits for your confirmation (ADR-0005, 2026-11-08 note). A re-mark would change noise shares that you have already approved records for, and it would leave strong evidence on noise entries. It would also undo your rulings, which say "needs no evidence", not "is noise". The fix clears 14 tier 1 partials: DODI5000.83-0203, 0208; DODI8530.01-0267; SP800-161R1-0157, 0973, 0994; SP800-37R2-0202; SP800-53AR5-0024, 0037, 0195, 0220, 0226, 0270, 0328. One fully ruled entry is still a candidate and still blocks: SP800-37R2-0657 (group E). It has no evidence item, so it cannot be marked partial, and the duty in its unmarked sentence remains unheld (WI-08).
- **C2 (judge).** A decision type's `requires` field counts only when the rule item's fixture mutates the authorization ledger (`artifacts/data/authorizations.yaml`). Before the fix, a SAP's `assessor_independence.review` was asked for the cATO pin, rule and schema triple. Eight items became strong: DODCIO-CATO-EVAL-0030#1, 0101#1; DODCIO-CSRMC-TENETS-0005#0; DODCIO-RECIPROCITY-0091#1; DTM-24-001-0127#0; SP800-37R2-0583#2; SP800-53AR5-0160#1; SP800-53R5-0068#0. Five METR-001 items lost a `review` field that they never broke, and their verdict did not change. SP800-53AR5-0160 stays partial, and its reason now names what is unheld.
- **C3 (judge).** `not any(...)` over a computed iterable is now read as a comparison. Only `not any(<plain field read>)` is still read as absence. Ten items changed from presence to constraint and now judge strong. Two fixtures had emptied a value and were rewritten to write a wrong value: ACQLC-001.coordinated now names a non-framework persona, and PRIV-001.nss now sets only the Classified overlay. The ten items are CNSSP12-0054, 0058; DODI5000.02-0050#2; DODI5000.89-0099, 0100, 0112; DODI5400.11-0141; DODI5400.16-0051, 0058, 0059. Their `claim` was updated to match. GATE-001, DISP-001 and CATG-005 judge exactly as before. AODM-001's "recorded no decision" clause now reads as a constraint, and its unit test moved.
- **C4 (judge, for your p13 question).** Removing one member of a list (`delete_list_item`) is kept as a wrong value, that is, a constraint. The test is that it leaves the same list as `set_field` to the remainder does, and the two must judge alike. Emptying a list is still presence. 74 evidence items rest on a `delete_list_item` fixture (71 constraint, 3 presence). If you rule that removing a member is presence, the 71 become presence. Most of them are on lettered, modal, table or promoted entries, so they would cap at partial on prose kinds. The items are listed below.

| Entry#item | Status | Kind | Rule | Fixture | Claim | Verdict |
|---|---|---|---|---|---|---|
| REQ-CNSSI1253-0013#0 | covered | lettered | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSI1253-0018#0 | covered | modal | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSI1253-0019#0 | partial | modal | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSI1253-0020#1 | partial | modal | TLR-003 | TLR-003.yaml | constraint | strong |
| REQ-CNSSI1253-0030#2 | covered | modal | TLR-003 | TLR-003.yaml | constraint | strong |
| REQ-CNSSI1253-0059#0 | covered | lettered | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSI1253-0081#0 | covered | lettered | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSI1253F-ATT6-PRIVACY-0298#0 | partial | modal | PIC-001 | PIC-001.yaml | constraint | strong |
| REQ-CNSSP12-0017#0 | partial | modal | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-CNSSP12-0024#1 | covered | lettered | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-CNSSP12-0027#0 | partial | lettered | REQS-002 | REQS-002.missing.yaml | constraint | strong |
| REQ-CNSSP12-0030#0 | partial | lettered | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-CNSSP12-0031#0 | partial | lettered | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-CNSSP12-0032#0 | covered | lettered | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-CNSSP12-0036#0 | partial | lettered | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-CNSSP12-0053#0 | partial | lettered | SPCOV-002 | SPCOV-002.yaml | constraint | strong |
| REQ-DODCIO-CATO-EVAL-0051#0 | covered | lettered | CONMON-001 | CONMON-001.yaml | constraint | strong |
| REQ-DODCIO-CATO-EVAL-0123#1 | partial | lettered | PENT-001 | PENT-001.event.yaml | constraint | strong |
| REQ-DODCIO-CATO-EVAL-0161#0 | covered | lettered | CATO-009 | CATO-009.member.yaml | constraint | strong |
| REQ-DODCIO-CATO-EVAL-0178#0 | covered | lettered | CATO-009 | CATO-009.member.yaml | constraint | strong |
| REQ-DODCIO-CATO-IG-0034#1 | covered | lettered | CATO-001 | CATO-001.demonstration.yaml | constraint | strong |
| REQ-DODCIO-CATO-IG-0036#1 | covered | lettered | CATO-015 | CATO-015.unscored.yaml | constraint | strong |
| REQ-DODCIO-CATO-IG-0039#0 | covered | lettered | CATO-001 | CATO-001.documentation.yaml | constraint | strong |
| REQ-DODCIO-CSRMC-TENETS-0009#0 | partial | promoted | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-DODCIO-RECIPROCITY-0096#1 | covered | lettered | RCP-002 | RCP-002.inforce.yaml | constraint | strong |
| REQ-DODCIO-RECIPROCITY-0150#0 | partial | modal | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DODI5400.11-0164#0 | partial | lettered | PRIV-007 | PRIV-007.privacy-act.yaml | constraint | strong |
| REQ-DODI5400.16-0034#0 | partial | lettered | PRIV-003 | PRIV-003.yaml | constraint | strong |
| REQ-DODI5400.16-0057#0 | partial | lettered | PRIV-003 | PRIV-003.yaml | constraint | strong |
| REQ-DODI8500.01-0173#0 | covered | lettered | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DODI8500.01-0419#0 | partial | lettered | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-DODI8510.01-0048#0 | covered | lettered | SAR-POAM-001 | SAR-POAM-001.plan.yaml | constraint | strong |
| REQ-DODI8510.01-0118#0 | covered | table | PRIV-010 | PRIV-010.yaml | presence | strong |
| REQ-DODI8510.01-0125#0 | partial | table | SAR-POAM-001 | SAR-POAM-001.plan.yaml | constraint | strong |
| REQ-DODI8510.01-0132#0 | partial | lettered | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-DODI8530.01-0221#1 | partial | lettered | PENT-001 | PENT-001.event.yaml | constraint | strong |
| REQ-DODI8530.01-0227#1 | partial | lettered | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DODI8531.01-0051#0 | partial | lettered | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DODI8531.01-0078#0 | partial | lettered | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DODI8531.01-0126#1 | partial | lettered | PENT-001 | PENT-001.event.yaml | constraint | strong |
| REQ-DODI8531.01-0178#0 | covered | lettered | STIG-001 | STIG-001.benchmark.yaml | constraint | strong |
| REQ-DOWI8430.01-0006#0 | partial | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0007#0 | partial | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0090#0 | partial | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0175#0 | partial | modal | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0176#0 | covered | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0178#0 | covered | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0181#0 | covered | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-DOWI8430.01-0182#0 | covered | lettered | REQS-002 | REQS-002.software.yaml | constraint | strong |
| REQ-SP800-137A-0009#0 | partial | lettered | CONMON-001 | CONMON-001.yaml | constraint | strong |
| REQ-SP800-137A-0074#0 | partial | lettered | CONMON-001 | CONMON-001.yaml | constraint | strong |
| REQ-SP800-137A-0076#0 | partial | lettered | CONMON-001 | CONMON-001.yaml | constraint | strong |
| REQ-SP800-160V1R1-0006#0 | partial | modal | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-160V1R1-0574#0 | covered | lettered | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-160V1R1-0598#0 | covered | lettered | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-18R2-0303#0 | partial | indicative | PRIV-010 | PRIV-010.yaml | presence | weak |
| REQ-SP800-37R2-0221#0 | partial | table | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-37R2-0239#0 | covered | modal | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-37R2-0240#0 | partial | modal | ASSET-001 | ASSET-001.yaml | constraint | strong |
| REQ-SP800-37R2-0240#1 | partial | modal | ASSET-001 | ASSET-001.privacy.yaml | constraint | strong |
| REQ-SP800-37R2-0327#0 | covered | table | PRIV-010 | PRIV-010.yaml | presence | strong |
| REQ-SP800-37R2-0335#0 | partial | imperative | PRIV-010 | PRIV-010.yaml | presence | weak |
| REQ-SP800-37R2-0377#0 | covered | modal | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-SP800-37R2-0377#1 | covered | modal | SAR-POAM-001 | SAR-POAM-001.plan.yaml | constraint | strong |
| REQ-SP800-37R2-0380#0 | covered | table | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-SP800-37R2-0392#0 | partial | indicative | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-SP800-37R2-0507#0 | covered | lettered | RISKX-001 | RISKX-001.autonomy.yaml | constraint | strong |
| REQ-SP800-37R2-0547#2 | partial | modal | PKG-001 | PKG-001.poam.yaml | constraint | strong |
| REQ-SP800-61R3-0191#0 | covered | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-SP800-61R3-0193#0 | partial | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-SP800-61R3-0194#0 | covered | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-SP800-61R3-0195#0 | partial | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-SP800-61R3-0196#0 | partial | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
| REQ-SP800-61R3-0197#0 | partial | table | DETC-001 | DETC-001.coverage.yaml | constraint | strong |
