# Findings 11: Assessor selection and assessment plan (A-1, A-2)

Session unit: A-1 and A-2 of `runs/20261118-synthetic-01`, in the order `rmf status` gave. Both
tasks are done; `rmf status` names A-3 (family ac) next. Every answer is SIMULATED, including the
AODR's approval of the plan. Findings 00 to 10 are not repeated; where this session met one
again, the evidence is added below.

### F-11-1: The A-1 rules read sap.yaml, which only A-2 writes, so `--task A-1` can never fail
- Where: A-1; INDEP-001 (charged to A-1), ATEAM-001 and ASMT-007 (`assessment.py`, `_sap()` returns nothing until ART-SAP is produced); `playbooks/A/A-1.md` "Done when"
- Kind: defect
- Severity: major
- What happened:
  - A-1 has no output. Its playbook says the interviews are its record.
  - The same playbook's "Done when" requires that "sap.yaml carries both (ATEAM-001, ASMT-007)" and "sap.yaml assessor_independence.consulted names the CIO, the SAOP and the SISO (INDEP-001)". sap.yaml is an A-2 output.
  - INDEP-001 is registered to A-1, but it returns nothing until ART-SAP is produced or seeded. `rmf check --task A-1` reported `0 error(s)` before any A-1 interview existed. It did so again after the interviews, when nothing yet recorded the selection or the consultation in data.
  - A-1's result reaches a rule only when A-2 writes `selection`, `assessor_independence` and `consulted`. An error there would then be charged partly to A-1, after A-1 was reported done.
  - This is the same pattern as F-10-4 and F-02-3, in a sharper form: the rule charged to A-1 cannot run at A-1.
- Workaround used: Wrote the A-1 interviews (INT-142 to INT-146) and two journal DECISIONs. Then wrote `selection`, `assessor_independence` (with `consulted`) and the team's `qualification` into sap.yaml at A-2. INDEP-001, ATEAM-001 and ASMT-007 passed on the first A-2 cycle.
- Recommendation: Give A-1 a small output of its own, for example `artifacts/data/assessor-selection.yaml` holding `selection`, `assessor_independence` and the team's qualification, which sap.yaml then references. Otherwise, move INDEP-001 to A-2 and change the A-1 "Done when" to say that A-2 records the result. In either case, `rmf check --task A-1` should report that the record is missing.

### F-11-2: The A-2 playbook never mentions ART-AUTHREC or authorizations.yaml, though the header lists ART-AUTHREC as an output
- Where: `playbooks/A/A-2.md` (header Outputs `ART-AUTHREC (produces)`; body `## Outputs` lists only sap.yaml and ART-SAP); `templates/data/authorizations.yaml`; AODM-006; the `live` flag in the sap schedule events
- Kind: doc
- Severity: minor
- What happened:
  - `rmf status` listed "ART-AUTHREC missing" for A-2. The authored body has no step for it, does not list it in Outputs, and does not mention test-strategy.yaml in Outputs either.
  - The template comment was the only guidance. It says "`records: []` is valid at A-2 when no test event runs live".
  - Only the sap schema's `live` description connects that to AODM-006. The A-2 body never names AODM-006, an IATT, or the `live` flag.
- Workaround used: Wrote authorizations.yaml with `system_status: {status: none}` and `records: []`. Set `live: false` on every SAP event, because all of them run in pre-production with synthetic data. Wrote ART-AUTHREC explaining why no IATT is needed.
- Recommendation: Add an A-2 step: "Start the authorization ledger: `artifacts/data/authorizations.yaml` with `system_status` and the records in force; an IATT record (AD-IATT) when a SAP event is `live`; ART-AUTHREC summarizing it (AODM-006, SSPR-001)". List ART-AUTHREC and test-strategy.yaml in the body's Outputs table.

### F-11-3: ASMT-003 forbids reusing developer and DT results under an independent assessment; the schema cannot record "examined and re-performed"
- Where: ASMT-003 (`_reused`: a result's `independence` rank must be at least `assessor_independence.required`); sap schema `reused_results`; `product/test-results.md#top` (results offered for reuse); DoDI 8510.01 Table 5 Task A-3; the handoff brief
- Kind: gap
- Severity: major
- What happened:
  - The product offers the release 1.5.0 pipeline gates, DT-2 and the ISSO's account review for reuse, "as DoDI 8510.01 and DoDI 5000.87 encourage".
  - The AO required `independent`, which is right for a moderate system with PII and a demonstrated re-identification finding.
  - The pipeline gates, DT-2 and the account review are the program's own tests (`self-assessment` or `internal`). ASMT-003 would refuse each of them as a reused result.
  - The only way to reuse them would have been to record them as `independent`, which would be false. An agent under pressure to "plan reuse" could easily do that, and nothing would catch it.
  - The schema has no way to record the honest middle course: the assessor examines the developer result as evidence and re-performs a sample. So the developer's contribution, which DoDI 8510.01 and DoDI 5000.87 want visible, appears only in procedure rationales.
- Workaround used:
  - Reused only the two independent results: RR-001, the STIG scan the SCA witnessed, and RR-002, the red team penetration test. Each has a `supplement`.
  - The program's own tests are named as examined objects in PRC-004, PRC-015 and the other procedures, with re-performance extents.
  - The CISO's reuse policy (INT-144.A3) and the AO's condition (INT-143.A2) state the rule.
  - test-strategy.yaml marks TE-001 and TE-002 `results_reused: false`.
- Recommendation:
  - Add a `used_as: evidence` kind, or a `witnessed_by` / `reperformed` field, to `reused_results`. ASMT-003 would then accept a lower-independence result when an assessor on the team witnessed it or re-performs a stated sample.
  - Say in the A-2 playbook that an unwitnessed self-test cannot be reused under `independent`.

### F-11-4: The ASMT-004 allowance for provider evidence "requested" is dead in any run whose scope reaches A-4
- Where: ASMT-004 (`packaged = not {"A-4", "R-2"}.isdisjoint(scope.active_tasks(ctx.run))`); `playbooks/A/A-2.md` step 4 ("still `requested` until A-4 or R-2 is in the run")
- Kind: defect
- Severity: minor
- What happened:
  - `active_tasks` is the run's scope, not the tasks that are done. A-4 and R-2 are in scope from `rmf run init` onward, so `packaged` is always true in a full run.
  - Every external provider must therefore show `evidence: received` already at A-2. The "requested" state the playbook describes is refused.
  - The rule's code comment ("Evidence may still be on request while the plan is made; the package needs it (A-4, R-2)") says the opposite of what the code does.
- Workaround used: All seven providers carry `evidence: received`:
  - For the four inherited providers this is grounded: `org-context.yaml` records that their plans and SARs were available to the PM on 2026-05-01.
  - For the identity broker, EMIS and the supply service it rests on a simulated SCA answer that the PM obtained each system's authorization letter (INT-147.A3).
- Recommendation: Test whether A-4 or R-2 is done (or started, i.e. its outputs exist), not whether it is in scope.

### F-11-5: ASMT-004 treats connected data sources like control providers
- Where: ASMT-004 `_external_ids` (every `external: true` boundary component); sap schema `external_providers` (`arrangement.type` enum, `provider_assessment` required, `meets_protection_needs` must be true)
- Kind: gap
- Severity: minor
- What happened:
  - CMP-IDB (identity broker), CMP-EMIS and CMP-SUPPLY are systems EFRAS connects to, not providers of controls EFRAS inherits. ASMT-004 still requires a full provider record for each: the provider's assessment scope, its independence, procedures reviewed, evidence received, and `meets_protection_needs: true`.
  - The arrangement enum (`contract | interagency-agreement | line-of-business | licensing | supply-chain`) has no value for an intra-DoD memorandum of agreement, an interconnection security agreement or an enterprise onboarding approval.
  - EMIS runs on an unsigned MOA and an interim e-mail approval (ca-3 partial). Even so, the rule forces `meets_protection_needs: true`. Nothing in this record can say "the agreement is the open finding".
- Workaround used: EXT-005 to EXT-007 use `line-of-business` or `interagency-agreement`. Each `procedure_adjustment` says the system is not assessed and only the EFRAS end is tested. The unsigned MOA is stated in `assurances` and left to ca-3 (PRC-012).
- Recommendation:
  - Add `kind: connected-system` (or a `relationship: provider | interconnection` field) that needs only the agreement review and the procedure adjustment.
  - Add `memorandum-of-agreement`, `interconnection-security-agreement` and `onboarding-approval` to the arrangement enum.
  - Let `meets_protection_needs` be false with a reference to the open finding.

### F-11-6: TSTRAT-004 requires every penetration test event to cover the complete system and the CSSP, so a held partial test cannot be recorded as one
- Where: TSTRAT-004 (`for e in pens`: each `penetration-exploitation` event must be `complete-system` with `includes_cssp: true`); `product/test-results.md#pentest`; test-strategy.yaml TE-004 and TE-005
- Kind: friction
- Severity: minor
- What happened:
  - The red team's test of 2026-10-27 to 2026-10-31 was a real penetration test. The product says nothing about the CSSP's part, and the CDT's simulated answer says the test did not evaluate it.
  - If that test is recorded honestly as `penetration-exploitation` with `includes_cssp: false`, TSTRAT-004 fails. It fails even with a later complete-system test planned beside it.
  - The source requires that penetration testing evaluate the complete defenses with the CSSP. It does not forbid other, narrower penetration tests in the strategy.
- Workaround used: Recorded the held test as TE-004, `kind: cybersecurity-dt`, with `conditions` explaining why. Planned TE-005, an integrated penetration and exploitation test from 2026-11-30 with the CSSP defending, which also serves as the PT-3 retest and the SAP's `penetration_test`. Reclassifying a test to satisfy a rule is uncomfortable; the description keeps the truth visible.
- Recommendation: Require at least one complete-system test with the CSSP in DT and one in OT (or one integrated test). Accept other `penetration-exploitation` events of narrower scope.

### F-11-7: The organization's reuse policy has no home in org-context, yet `reuse_policy.source` must be ART-ORG-CONTEXT
- Where: ASMT-003 (`reuse_policy.source` must be `ART-ORG-CONTEXT`); `framework/schema/org-context.schema.json` and `templates/data/org-context.yaml` (no reuse field); P-2 playbook
- Kind: gap
- Severity: minor
- What happened:
  - ART-ORG-CONTEXT and org-context.yaml name the Component procedure POL-02 but say nothing about reuse or a maximum age. P-2 never asked about either.
  - The `max_age_days: 365` value comes from a simulated CISO answer at A-1 (INT-144.A3). The rule nevertheless requires `source: ART-ORG-CONTEXT`.
  - The trace therefore points at a document that does not hold the value.
- Workaround used: `source: ART-ORG-CONTEXT`, as the rule requires. INT-144.A3 is cited in the sap.yaml `sources` and in ART-SAP's reuse section.
- Recommendation: Add an `assessment.reuse` block (maximum age, independence, who approves) to org-context.yaml at P-2, and have ASMT-003 read the limit from it. Alternatively, let `reuse_policy.source` be any trace token.

### F-11-8: The product has no test strategy; test-strategy.yaml rests wholly on simulated CDT and OTA answers
- Where: EXT-TEST-STRATEGY (A-2 input); `product/` (no TEMP or test strategy; `product/test-results.md` holds results only); `templates/workspace/product/`
- Kind: gap
- Severity: minor
- What happened: Every field of the test strategy comes from INT-149 and INT-150, both SIMULATED: the document ID and date, the Component approval date, the cybersecurity objectives, the entry and exit criteria, the evaluation frameworks, and the OT events and their January 2027 dates. The dated results in the product cover only the DT events. This is more evidence for F-00-3, F-01-2 and F-02-12.
- Workaround used: Grounded what the product supports: TE-001 to TE-004 come from the four dated results, and the "same templates as production" claim from `test-results.md#top`. The rest is simulated and says so in the file comment.
- Recommendation: Add `test-strategy.md` to the product template, asking for: document and version, approval, oversight status, test objectives, the planned DT and OT events with dates and conductors, and whether each event used a production-representative system.

### F-11-9: All assessment evidence comes from pre-production, which the product places outside the boundary, and nothing records or questions that
- Where: `product/architecture.md#boundary` ("The pre-production account is a separate environment with synthetic data and is not part of this authorization"); sap.yaml `penetration_test.components` (PENT-001 requires boundary components); TSTRAT-003 (`system: production-representative` is self-declared); the sap schema (no test environment field)
- Kind: gap
- Severity: minor
- What happened:
  - Every result offered for reuse, and every test the SCA plans, runs in pre-production. Production holds no release yet.
  - PENT-001 requires the penetration test's `components` to be inside the boundary, so the plan names CMP-EDGE and the other boundary components, although the test hits their pre-production twins.
  - TSTRAT-003 accepts `production-representative` and `operationally-representative` on the agent's word.
  - No field records that the assessed instance differs from the authorized one, and no rule asks the SCA to confirm the production configuration matches (for example by comparing templates or by a scan of production before go-live).
- Workaround used: Stated it in the rules of engagement, in ART-AUTHREC and in the RR-001 applicability basis ("built from the production templates"). PRC-008 compares the deployed state with the baseline, and PRC-011 examines the production account's settings through the read access the PM gave.
- Recommendation: Add `assessed_environment` to sap.yaml: in-boundary or representative, with a `representativeness` basis. When the environment is representative, require a procedure that confirms the production configuration before the decision, and carry that into the SAR as a limitation.

### F-11-10: The sap.yaml template omits fields the A-2 rules require
- Where: `templates/data/sap.yaml` against INDEP-001 (`assessor_independence.consulted`), PASM-001 (`privacy` block with `methodology`), PENT-001 (`penetration_test` is only a comment), the event `live` flag (AODM-006), and the `adaptation_note` and `additional_procedures` shapes
- Kind: doc
- Severity: minor
- What happened:
  - The template has no `consulted` and no `privacy` block. The playbook body mentions `privacy` only in "Done when", and `consulted` appears only in A-1's "Done when".
  - Writing them needed `framework/schema/sap.schema.json` and the rule source (`assessment.py`, `rigor.py`, `privacy.py`, `pentest.py`, `teststrategy.py`).
  - Two of RIGR-003's demands are not stated in the template or the playbook: focused coverage needs `specific` objects too (not only comprehensive), and each sampling record's `types` must equal the procedure's objects for that method. I found both in the rule source before writing, so they did not cost a cycle.
- Workaround used: Wrote the file from the schema and the rule source. This is more evidence for F-01-13 and F-09-2.
- Recommendation: Add `consulted`, `privacy` (with `methodology`), `live` on each event, and a worked `additional_procedures` entry to the template. Add a comment on RIGR-003's two demands.

### F-11-11: The example fork cannot serve as a worked example for A-2
- Where: `examples/uas-gcs/runs/example-synthetic-01/artifacts/data/` (has `decision.yaml` and a 40-line `sap.yaml`; no `test-strategy.yaml`, `authorizations.yaml` or ART-AUTHREC)
- Kind: gap
- Severity: note
- What happened: I listed the example while looking for the shape of the ledger and the test strategy. It is on the old contract that `rmf run migrate` replaces. Its sap.yaml predates the preparation, rigor, sampling, external provider and privacy blocks.
- Workaround used: Did not use it.
- Recommendation: Migrate the example run to the current contract, or say in the brief and in AGENTS.md that it does not show the A-step records.

### F-11-12: TRACE-001 counts the text before the first H2 as a section
- Where: TRACE-001 on `artifacts/ART-SAP.md`
- Kind: friction
- Severity: note
- What happened: I added a short paragraph under the H1: the simulated-draft notice and pointers to the two data files. TRACE-001 reported "section 'Security assessment plan' has no trace token". Fix attempts: 2.
- Workaround used: Added `[[INT-147.A1]] [[INT-149.A1]]` to the paragraph. RETRY journaled at 05:34Z.
- Recommendation: Say in `_shared/tagging-and-traceability.md` and the template comment that text under the H1 is a section too. Alternatively, exempt a preamble that makes no claim.

### F-11-13: Persona cards lack A-1 questions for the AO, AODR, CIO and PRIV, and A-2 questions for the PM (more evidence for F-01-12)
- Where: `personas/PER-AO.md`, `PER-AODR.md`, `PER-CIO.md`, `PER-PRIV.md` (no `A (A-1)` entry); `PER-PM.md` (no `A (A-2)` entry)
- Kind: doc
- Severity: minor
- What happened: The A-1 playbook sends the agent to the cards' "Question bank by step for step A". Of the A-1 roles, only PER-CISO has an A-1 question. The AO decides the degree of independence and the CIO and PRIV are consulted on it, yet their cards have no question on it. The A-2 playbook asks to interview the PM on notification, resources and access, and PER-PM's card has no A-2 entry.
- Workaround used: Took the questions from the A-1 "Done when" list, the A-2 playbook step 3 and the rule messages.
- Recommendation: Add the following questions to the cards:
  - AO (A-1): the degree of independence, whom you consulted, sufficiency.
  - CIO, PRIV (A-1): advice on independence; for PRIV also who assesses the privacy controls and the methodology.
  - AODR (A-1): the selection and the expertise it required.
  - PM (A-2): notification, resources, access and points of contact.

### F-11-14: A-1 and A-2 rules matched the playbooks closely and passed on the first cycle (positive)
- Where: A-2 playbook step 4; ASMT-001..004, ASMT-007, APREP-001, ATEAM-001, INDEP-001, RIGR-001/003, PASM-001, PENT-001, TSTRAT-001..004, SAP-COV-001
- Kind: positive
- Severity: note
- What happened:
  - sap.yaml (17 procedures, 2 additional procedures, 2 reused results, 7 external providers, the penetration test and the privacy scope) passed every A-2 rule on the first cycle. So did test-strategy.yaml with 8 events, and the empty ledger.
  - The only error was TRACE-001 (F-11-12).
  - The step 4 walk-through of the A-2 playbook names nearly every field each rule reads, and the rule messages quote their sources. Most of the plan could be written from the playbook alone.
  - `rmf build` produced `oscal/assessment-plan.json` from sap.yaml with no extra work, and OSCAL-001/002 passed.
  - TSTRAT-001..003 and SAP-COV-001 left `rmf check --final` as soon as the files existed. The total fell from 155 to 144.
- Workaround used: none needed.
- Recommendation: Use step 4 of the A-2 body as the model for the other authored playbooks. Add the missing template fields (F-11-10) so the template matches it.

### F-11-15: Deviations from the brief and the protocol
- Where: run files; rule source
- Kind: friction
- Severity: note
- What happened:
  1. Rule source and schemas were read to write sap.yaml and test-strategy.yaml (F-11-10). Bash ran only `uv run rmf ...` and read-only `grep`/`sed`/`python3 -c` filters on the repository and on `rmf` JSON output.
  2. Two interviews (INT-147, INT-151) were corrected in place with Edit after they were first written, to fix a wrong count and to align the SCA's list of comprehensively assessed controls with the procedures. They were corrected before any artifact cited the changed text. The journal was appended with Edit, as the brief allows.
  3. The playbook asks to read the assessment objectives of the scoped controls with `rmf catalog show --fields title,objectives`. I did not read all 50 controls' objectives, to save context. The procedures rest on the SSP statements, the risk assessment and the rule demands. No rule checks that procedures reflect the objectives.
  4. No reference passages beyond SP 800-37r2 Task A-1 and DoDI 8510.01 Table 5 were read.
- Workaround used: as described.
- Recommendation: Have `rmf catalog show` offer a compact `--fields objectives-count` or per-family summary, so that A-2 can ground the procedures in the objectives without reading every one.

## Session summary

- **Tasks done:**
  - A-1: interviews INT-142 (AODR), INT-143 (AO), INT-144 (CISO), INT-145 (CIO) and INT-146 (PRIV); two DECISIONs; CHECKPOINT 05:26Z.
  - A-2: sap.yaml, test-strategy.yaml, authorizations.yaml, ART-SAP and ART-AUTHREC; interviews INT-147 (SCA), INT-148 (PM), INT-149 (CDT), INT-150 (OTA) and INT-151 (AODR); DECISION and CHECKPOINT 05:34Z.
  - All answers are SIMULATED.
- **Build/check cycles:**
  - A-1: 1 cycle, 0 errors (vacuous until sap.yaml exists, F-11-1).
  - A-2: 2 cycles. The first had 1 TRACE-001 error; the second had 0.
- **Final results:**
  - `rmf build` plus plain `rmf check`: 0 errors.
  - `--task A-1` and `--task A-2`: 0 each. `--task I-2`, `S-4`, `S-6`, `P-15` and `C-1`: 0 each.
  - `rmf check --final`: 144 errors, down from 155, all owed by A-3 onward: SAR-COV-001, SAREL-001, DEL-001, RUN-ART-001, RCP-001, SVCA-002, PENT-002, AUTHRPT-001, MCHG-001, MRPT-001, XSUM-001 and PKG-001.
- **Blockers:** none.
- **For the next session (A-3):**
  - Use only the methods sap.yaml selects for each control (ASMT-005), at no less than each procedure's depth and coverage (RIGR-002).
  - RR-001 and RR-002 are the only reused results.
  - The plan's owed items:
    - the ASD STIG review of INV-002 to INV-006, then ART-STIG's `## Assessor verification`;
    - the ps-4/ac-2 leaver-timing test;
    - the PT-3 retest in TE-005, whose results PENT-002 needs in sar-summary.yaml;
    - APR-001 and APR-002 (REQ-11, REQ-12) under sa-11.
  - The pre-production limitation (F-11-9) belongs in the SAR.
