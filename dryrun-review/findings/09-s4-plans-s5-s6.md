# Dry-run findings 09: finishing S-4 (plans and plan records), S-5 and S-6

Run: `runs/20261118-synthetic-01` (synthetic, EFRAS). This session unit had two parts:

1. Finish S-4. That meant:
   - ART-SSP, with `ssp-records.yaml`, `scrm-plan.yaml` and `plan-reviews.yaml`;
   - ART-CMP and `cm-plan.yaml`, ART-CP and `contingency.yaml`, ART-IRP and `incident-response.yaml`;
   - `software.yaml`;
   - the S-4 CHECKPOINT.
2. Do S-5 (system continuous monitoring strategy) and S-6 (plan review and approval) in the
   order `rmf status` gives.

All three tasks are done. Every answer is SIMULATED, including the AODR's and the privacy
officer's approvals at S-6.

S-4 and S-6 passed on the first cycle. S-5 needed a second cycle (F-09-4). Writing
`software.yaml` at S-4 sent the run back to P-15 (F-09-1).

Findings 00 to 08 are not repeated here. New evidence for some of them is in F-09-7.

### F-09-1: Writing `software.yaml` at S-4 broke P-15 (REQS-002), and `--task S-4` did not show it
- Where:
  - REQS-002 in the requirements rules;
  - `artifacts/data/requirements.yaml` and ART-REQ, which P-15 wrote;
  - `artifacts/data/software.yaml`, which S-4 writes;
  - `rmf check --task`.
- Kind: defect
- Severity: major
- What happened:
  - Once S-4 wrote `software.yaml` with `covered_software: true`, `rmf check --task S-4` reported 0 errors.
  - `rmf status` then sent the run back to P-15. REQS-002 now required the software safety policy statement (`DP-SW-SAFETY`) to apply and to be carried by a requirement.
  - P-15 had passed earlier only because `software.yaml` did not exist yet. The rule took the missing file as "no covered software".
  - So a task finished long ago fails because of a file that a later task writes. The later task's own check does not show this.
  - This is new evidence for F-02-3: a scoped check can hide errors.
- Workaround used:
  - Made `DP-SW-SAFETY` apply in `requirements.yaml`, carried by REQ-04, whose `policy` became `[DP-SW-INPUT-VALIDATION, DP-SW-SAFETY]`. The file has a correction comment.
  - Corrected ART-REQ to twenty-one statements applying and seven not, with an explanation.
  - Journaled a NOTE (04:56Z).
  - P-15, P-17, S-2, S-3 and S-4 then reported 0.
- Recommendation:
  - When an input file is missing, a rule should report it as "unknown", not as "false". Either P-15 asks the software question itself, or REQS-002 waits until `software.yaml` exists.
  - `rmf check --task T` should also run the rules of earlier, completed tasks whose inputs T writes. Failing that, `rmf status` should name the regression next to the task that caused it.

### F-09-2: No data template for `conmon.yaml`, so S-5 needs the schema and the rule source
- Where: `templates/data/` (no `conmon.yaml`); `playbooks/S/S-5.md`; `framework/schema/conmon.schema.json`; ISCM-001..006, METR-001/002 (`iscm.py`), CONMON-001, OCTX-009, VULN-007, SWLC-001, DETC-001
- Kind: gap
- Severity: minor
- What happened:
  - `conmon.yaml` is one of the largest run-data files, about 550 lines. Eleven rules in five rule files judge it.
  - The other S-4 records have a template, but this one does not.
  - To learn which sections the rules need, I had to read the schema and the rule source. Examples: `measurement`, `minimum_review`, `detection_coverage`, `vulnerability_management`, the `privacy` strategy, `lifecycle_approach`, `ongoing_authorization`, `reporting.dodin`.
  - Several of these sections are owed to other controls or to the Component's policy. The S-5 playbook names them only through the rule IDs.
- Workaround used: Wrote the file from the schema and rule messages.
- Recommendation: Add `templates/data/conmon.yaml` with every section and a comment naming the rule and requirement behind it, as the other S-4 records have.

### F-09-3: The `ssp-records` and `scrm-plan` schemas require approval fields at S-4, before S-6 reviews the plans
- Where: `framework/schema/scrm-plan.schema.json` (approval with date); `framework/schema/ssp-records.schema.json` (`approvals` required, may be empty)
- Kind: friction
- Severity: minor
- What happened:
  - `ssp-records.yaml` handles this well: `approvals: []` is valid at S-4, and S-6 fills it.
  - `scrm-plan.yaml` handles it badly. It requires an approval with a date at S-4, so the C-SCRM plan cannot be recorded as a draft awaiting approval.
  - In the run, the PM approves the C-SCRM plan on 2026-11-18. That is before the AODR's review at S-6, and before the CP, IRP and CMP, which stay drafts until 2026-12-15.
  - The run's timeline now looks more finished than the conversation behind it was.
- Workaround used: Recorded the PM's approval of the C-SCRM plan, dated 2026-11-18, in INT-123.A4 and INT-126.A2 (edited), both SIMULATED.
- Recommendation: Let the C-SCRM approval be empty, or `status: draft`, until S-6, as `ssp-records.approvals` already allows. Then judge it at S-6.

### F-09-4: PRIV-006 needs every privacy-selected control listed one by one (42 of 50)
- Where: PRIV-006 (`privacy.py`); `conmon.yaml` `privacy`
- Kind: friction
- Severity: minor
- What happened:
  - On the first cycle, the privacy monitoring strategy listed the five controls specific to PII. It added guidance that every other privacy-selected control follows its family's frequency.
  - PRIV-006 returned 37 errors. It counts every control that the NSS privacy baseline or the Privacy Overlay selects, 42 of the run's 50, and wants each one listed with a frequency.
  - The list therefore repeats most of `frequencies` with no new information. Two lists that must be kept in step will drift.
- Workaround used:
  - Listed the 37 other controls one by one at their family or override frequency. Second cycle: 0.
  - Journaled a RETRY (05:02Z). `docs/LESSONS.md` is frozen for the dry run, so there was no lesson.
- Recommendation: Let the privacy strategy point to `frequencies` for controls with no privacy-specific frequency, and list only the exceptions. Or let it take a family shorthand.

### F-09-5: Some plan rules force entries the run cannot truthfully make yet, or that do not fit this system
- Where:
  - CPLAN-001 `rto_gaps` and CPLAN-003 `dynamic_allocation.proved_by` (`plans.py`);
  - CRYP-001 `policy_basis` and `acquisition_basis`;
  - IRPT-001, the reporting paths.
- Kind: gap
- Severity: minor
- What happened:
  - `rto_gaps` (CPLAN-001): a gap can only point to a POA&M item, and A-6 writes those much later. The cold rebuild is estimated at 18 h against a 24 h RTO, but nobody has proven it (`product/conops.md#limitations` item 4). The honest answer is "unproven". The file cannot record that, so `rto_gaps` stays empty, and the plan text and ART-CP have to carry the caveat.
  - `proved_by` (CPLAN-003): accepts EX-02, an exercise planned for 2027-02 that has not been held. A plan can therefore claim proof from an exercise that has not happened.
  - CRYP-001: wants "CNSSP 15" as the policy and acquisition basis on a system that is not a national security system (`space_nss: false`, unclassified CUI). This is new evidence for F-04-5.
  - IRPT-001: requires the paths for compromise of classified information, classified spillage and loss by a cleared contractor. It does so on a system with no classified information. The paths are now recorded, but they describe events that cannot happen here.
- Workaround used:
  - Filled each field as the schema requires.
  - Said in ART-CP that the failover is unproven, and in ART-IRP that the classified paths are there to meet the rule.
  - Recorded the gap as the cp-4 open item, which S-6 carries into the AODR's conditions.
- Recommendation:
  - Add an "unproven pending exercise" state to `rto_gaps` that does not need a POA&M ID before A-6.
  - Make CPLAN-003 require that the proving exercise has a held date, not just a planned one.
  - Scope CRYP-001 and IRPT-001 to NSS or classified systems, using `space_nss`, classification and the categorization facts.

### F-09-6: The measurement IDs in `conmon.yaml` reuse the NEED-xx prefix from the requirements records, and a family minimum forces a control override
- Where: `conmon.yaml` `measurement` (NEED-01/02, MSR-01/02); `requirements.yaml` NEED-xx; `org-context.yaml` minimum frequencies; ISCM-001
- Kind: friction
- Severity: note
- What happened:
  - The schema's ID pattern for measurement needs is `NEED-nn`, the same prefix `requirements.yaml` uses for stakeholder needs. Two different things carry the same token across the run, and a trace reader cannot tell them apart.
  - Separately, the Component's weekly minimum for the `ra` family is meant for vulnerability scanning. Applied at family level, it makes ra-3 (the risk assessment) weekly unless the run adds an override.
- Workaround used: Kept NEED-01/02 as the schema requires. Added an ra-3 override (annually) and explained it in ART-CONMON.
- Recommendation: Rename the measurement prefix (for example `MNEED-`). Let `org-context.yaml` set minimum frequencies per control as well as per family.

### F-09-7: S-4 and S-6 write files that belong to other tasks (new evidence for F-06-8)
- Where:
  - `requirements.yaml` and ART-REQ, P-15's files, edited at S-4 (F-09-1);
  - `conmon.yaml`, S-5's file, rewritten at S-6;
  - `playbooks/S/S-6.md`, its Outputs table and its "Done when" list.
- Kind: doc
- Severity: minor
- What happened:
  - S-4 had to correct P-15's files.
  - The S-6 "Done when" list requires conmon.yaml to record the approval (ISCM-004) and to be rewritten whole, but the S-6 Outputs table does not list `conmon.yaml`, and ART-CONMON's `touched_by` gets no S-6 entry. As a result, provenance does not show that S-6 changed the strategy's data.
- Workaround used: Rewrote `conmon.yaml` with the `approval` block (PER-AODR, 2026-11-18, INT-134.A2). Recorded the approval in ART-SSP's S-6 section and in the journal.
- Recommendation: Either list ART-CONMON among the S-6 outputs, with `touched_by`, or have S-5 hold the approval and its interview. Record cross-task edits explicitly, as F-06-8 asks.

### F-09-8: The journal format error names the pattern but not the bad part
- Where: JOURNAL-001
- Kind: friction
- Severity: note
- What happened:
  - The closing NOTE header was `· NOTE · session end`.
  - JOURNAL-001 reported "malformed entry" with the whole pattern. It did not say that the scope part (`task T`, `artifact A` or `run`) was missing, or which line was wrong.
  - Earlier NOTE entries in this run used the right form, so the error was mine, and it was quick to fix.
- Workaround used: Changed the header to `· NOTE · run`. The next check was clean.
- Recommendation: Have JOURNAL-001 report the line number and the part that failed to match.

### F-09-9: Positive: the plan rules gave clear messages, and S-6 was simple
- Where: CMPL, CPLAN, IRPT, BYP, FUND, CRYP, TELE (`plans.py`); SCRM-009..032; PRIV-012; ISCM-004
- Kind: positive
- Severity: note
- What happened:
  - The S-4 plan records passed on the first cycle.
  - Each rule message names the requirement and the missing element, so the schema and the messages were enough to write the records.
  - PRIV-012 states its order clearly: the privacy officer's approval on or before the AO's or AODR's approval, and before the first authorization decision. Same-day approvals are accepted.
  - The S-6 playbook's "Done when" list matched the rules exactly.
- Workaround used: None needed.
- Recommendation: Use the "Done when" list of the S-6 playbook as the model for the S-4 and S-5 playbooks.

### Deviations from the brief
- Bash was used only for `uv run rmf ...`. Its JSON output was piped into short `python3 -c` filters to count and list findings.
- Some rule source and schemas were read to learn what the records need (F-09-2).
- Run files were changed with Edit, not rewritten in one Write: `ssp-records.yaml`, `conmon.yaml`, ART-SSP, the interviews INT-122 and INT-126, and the P-15 files. The resulting files are complete and consistent, but strictly this is a partial patch under INV-8.

## Session summary

- Tasks completed:
  - S-4: plans and plan records, CHECKPOINT 04:56Z.
  - S-5: CHECKPOINT 05:02Z, after a RETRY for PRIV-006.
  - S-6: CHECKPOINT 05:06Z.
  - P-15 was also corrected (F-09-1).
- Interviews written: INT-122..INT-128 (S-4), INT-129..INT-132 (S-5), INT-133 and INT-134 (S-6). All are SIMULATED.
- Build and check cycles:
  - S-4: 1 cycle, then 1 more after the P-15 correction.
  - S-5: 2 cycles (37 PRIV-006 errors, then 0).
  - S-6: 1 cycle with 0 errors, then 1 more to fix a JOURNAL-001 header in the closing NOTE.
- Last results:
  - Plain `rmf check`: 0 errors, 0 warnings.
  - `--task S-4`, `--task S-5` and `--task S-6`: 0 errors each.
  - `rmf check --final`: 155 errors, all owed by later tasks (I, A, R and M): SAR-COV-001, DEL-001, SAREL-001, RUN-ART-001, RCP-001, SVCA-002 (M-2), TSTRAT-001..003, PENT-002, SAP-COV-001, AUTHRPT-001, MCHG-001, MRPT-001, XSUM-001 and PKG-001.
- What is left: `rmf status` names I-1 (Control Implementation) next. Nothing blocks it. The open conditions from S-6 go to I-1 and to A-6:
  - the CP, IRP and CMP approved by 2026-12-15;
  - the POA&M for the 18 open items, including the untested regional failover;
  - the PIA signed before production data.
