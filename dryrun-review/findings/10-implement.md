# Findings 10: Implement step (I-1, I-2)

Session unit: I-1 and I-2 of `runs/20261118-synthetic-01`, in the order `rmf status` gave.
Both tasks are done; `rmf status` names A-1 next. Earlier findings (00 to 09) are not repeated;
where this session met them again, the evidence is added below.

### F-10-1: The STIG summary schema needs rule IDs, categories and benchmark versions that the product template never asks for
- Where: I-1, `framework/schema/stig-summary.schema.json`, `templates/workspace/product/` (test results), `product/test-results.md#stig-scan`
- Kind: gap
- Severity: major
- What happened: The product gives the scan as percentages (Kubernetes STIG 94%, PostgreSQL STIG 88%) and names the six open PostgreSQL items by subject only. The schema requires `version` for every benchmark, and `rule_id` (pattern `^S?V-\d+`) and `category` for every finding. The product gives none of these. The schema also has nowhere to put a compliance percentage or a count of open items that are not listed one by one. Because of that, the Kubernetes control plane items (an unknown number) cannot be recorded except as one record per rule.
- Workaround used: Benchmark versions are written as "release current on 2026-10-22 (number not in the product material, ASM-018)". The six PostgreSQL records have fictional placeholder rule IDs SV-900201 to SV-900206 under ASM-018, and their CAT II category comes from a simulated developer answer (INT-135.A2). The Kubernetes control plane items are described only in ART-STIG prose. No scan was invented.
- Recommendation: Have the product template's test-results section ask, for each STIG/SRG scan, for the benchmark title and release, the scan tool, and each open or inherited rule with its V-/SV- ID and CAT. Add optional `compliance_percent` and `open_unitemized` (count plus reason) to each benchmark, so a summary-level scan can be recorded honestly.

### F-10-2: MPLAN-001 is charged to M-4, so `--task I-2` hides an error in the record I-2 writes; nothing tells I-2 who may approve a plan update
- Where: I-2, `artifacts/data/plan-reviews.yaml` `changes[].approved_by`, `src/rmf_tool/check/rules/monitor.py` (MPLAN-001, `applies_after: M-4`), playbook `playbooks/I/I-2.md`
- Kind: defect
- Severity: major
- What happened: PRIV-010 requires I-2 to log its update in `plan-reviews.yaml changes`. I logged it with `approved_by: PER-PM`, because the PM is accountable (A) for I-2. `rmf check --task I-2`, plain `rmf check` and `--task S-4/S-6` all reported 0 errors. Only `rmf check --final` showed `MPLAN-001: 1.1: the update to the system plan is approved under change management, by PER-AO or PER-AODR or PER-CCB, not PER-PM`. The schema title ("Who approved the update to the system plan") and the PRIV-010 hint do not name the allowed approvers. Neither does the I-2 playbook. The rule's owner is M-4, which this run defers. Fix attempts: 2 (PER-PM, then PER-CCB).
- Workaround used: Added a simulated board interview (INT-141, PER-CCB) approving version 1.1. Set `approved_by: PER-CCB` and recorded a RETRY in the journal.
- Recommendation: Run MPLAN-001's per-change approver check for every task that writes a `changes` entry (the task named in the entry), not only after M-4. Add `"enum"`-like guidance or a description listing PER-AO, PER-AODR and PER-CCB to the schema's `approved_by`. Name them in the generated I-2, A-5, R-3 and M-1 playbook steps that say "log the update". This is more evidence for F-02-3 and F-09-1: a rule charged to a later task hides an error in an earlier task's record.

### F-10-3: stig-summary has no "inherited" status, and the approved plan's "ISSM approves inherited deviations" passed every rule
- Where: I-1, stig-summary `findings[].status`, SCFG-001; S-4's `ssp/controls/cm.yaml` cm-6 and `cm-plan.yaml` tools/baselines
- Kind: gap
- Severity: minor
- What happened: The scan marks provider-managed settings "inherited". The status enum is `open | not-a-finding | not-applicable | not-reviewed | exception`, and an `exception` must be approved by PER-AO or PER-AODR (SCFG-001). S-4 had written cm-6 and the CM plan saying that these items are "inherited deviations the ISSM approves in the STIG summary". That is a claim SCFG-001 would refuse, but no rule compared it with anything before the STIG summary existed, and no rule compares the SSP's wording with it afterwards either.
- Workaround used: The four PostgreSQL engine items are `not-applicable`, with titles naming the provider and LA-01 (STG-003 to STG-006). The ISSE and the provider confirmed this in INT-136.A1 and INT-137.A1. I-2 corrected cm-6, the CM plan's scanner entry and two CI baselines, and ART-CMP's Baseline configurations section.
- Recommendation: Add `inherited` to the status enum with a required `provider` (an LA-## or common control provider), and have STIG-001 or a new rule accept it only when that provider's allocation covers cm-6. Tell S-4 (cm-6 guidance) that program deviations from a STIG are exceptions for the AO or AODR, not the ISSM.

### F-10-4: `rmf check --task I-2` reports 0 errors before I-2 has done anything
- Where: I-2, `rmf check --task I-2` against `rmf status`
- Kind: friction
- Severity: minor
- What happened: Before any I-2 output existed, `rmf check --task I-2` reported `0 error(s), 0 warning(s)`. At the same time, `rmf status` listed I-2 as todo: six `touched_by does not list I-2` items and `0/1 interview(s)`. The playbook's done criterion "`rmf check --task I-2` reports 0 errors" was therefore met before I-2 started. The same holds for every update-only task whose rules apply only after it is done.
- Workaround used: Used `rmf status` as the test of done, alongside the check.
- Recommendation: Have `rmf check --task T` also report T's status gaps (missing touched_by, interview count, missing output files) as findings, or have the playbooks' "Done when" say that `rmf status` must list the task as done.

### F-10-5: The I-2 "Inputs: only these" list leaves out the files I-2 must rewrite and the records that show which statements are stale
- Where: `playbooks/I/I-2.md` `## Inputs` against `## Outputs` and `## Steps` 4
- Kind: doc
- Severity: minor
- What happened: Inputs names ART-SSP (and its data files), ART-STIG and the product, and says "Only these: do not open other run files". Step 4 requires reading ART-SD, ART-INV, ART-CMP, ART-CP and ART-IRP and their data files in order to rewrite them. The stale SSP statements were in ca-7, which still described the S-5 strategy as "to be written", with reporting that differed from `conmon.yaml`, and in pl-2, which still said the plans "await approval at S-6". They could be found only by opening `conmon.yaml` and `cm-plan.yaml`, which are outside the list.
- Workaround used: Read the output artifacts and `conmon.yaml`'s reporting block. Corrected ca-7 (reporting now as approved: monthly roll-up to PM/ISSM/AODR, quarterly posture report to the AO) and pl-2, keeping their status.
- Recommendation: List every output artifact and its data files under Inputs in the generated body. Add a step: "check each statement S-5/S-6 made stale (ca-7 against conmon.yaml, pl-2 against the S-6 approvals, cm-6 against stig-summary.yaml)". A rule comparing ca-7's reporting parameters with `conmon.yaml reporting` would catch the drift; this is more evidence for F-07-1.

### F-10-6: Playbook and templates name different I-2 headings; the template front-matter has a sixth key the protocol forbids
- Where: `playbooks/I/I-2.md` step 4 ("## Update Control Implementation Information (I-2)") against the comments in `templates/artifacts/ART-CMP.md`, `ART-CP.md` and `ART-IRP.md` ("## Implementation updates"); `templates/artifacts/ART-STIG.md` `handling: CUI` against `00-run-protocol.md` "exactly these 5 keys"
- Kind: doc
- Severity: note
- What happened: The two sources disagree on the heading, and no rule checks either one. ART-STIG's template carries `handling: CUI` as a sixth front-matter key, while the protocol says every artifact has exactly five and RUN-FM-001 checks it. RUN-FM-001 accepted the key, as it did for ART-CMP at S-4.
- Workaround used: Used the template heading for ART-CMP, ART-CP and ART-IRP, and the playbook heading for ART-SSP, ART-SD and ART-INV, which have no template comment. Kept `handling: CUI` in ART-STIG.
- Recommendation: Pick one heading and render it into both places. Update the protocol's front-matter section to list `handling` as an allowed key for the artifacts whose templates carry it. This is more evidence for F-03-5.

### F-10-7: Nothing ties a STIG finding's control to that control's SSP status; my first mapping would have contradicted the SSP silently
- Where: I-1, stig-summary `findings[].control_id`; SSP au-2
- Kind: gap
- Severity: minor
- What happened: I first mapped STG-001 (connection logging verbosity) to au-2, which the SSP records as `implemented` with no mention of it. Every rule passed. At I-2 I remapped it to cm-6, where the product and the SSP place both program-fixable items. Fix attempts: 2.
- Workaround used: Remapped to cm-6 in stig-summary.yaml and ART-STIG, and wrote a journal NOTE.
- Recommendation: Add a rule that warns when an `open` STIG finding names a control whose SSP status is `implemented` or `inherited` and whose statement does not name the finding.

### F-10-8: Nothing in the product says which benchmark covers the application containers
- Where: I-1 step 5, STIG-001; `product/test-results.md`, `product/architecture.md#configuration`
- Kind: gap
- Severity: minor
- What happened: STIG-001 needs every `software` item mapped to a benchmark or given a not-applicable reason. The product names only the Kubernetes and PostgreSQL STIGs and the factory's hardened base image. For the five program-built containers, the applicable checklist (the Application Security and Development STIG) and whether a review was ever done had to come from a simulated ISSE answer. The I-1 playbook gives no hint for application software.
- Workaround used: BM-04 (ASD STIG) has no scan date and is described as not reviewed, under ASM-019 and INT-136.A2. It is owed by the assessor at A-3 and recorded as a cm-6 gap at I-2. The two open-source libraries are not-applicable, covered through their containers.
- Recommendation: Have the product template's configuration section ask which STIG/SRG each inventory item is held to, and the date of its last checklist review. Add to the I-1 playbook: "program-built application software: the Application Security and Development STIG, or a stated reason".

### F-10-9: The product inventory cannot show a release fielded only to pre-production
- Where: I-2, `product/hw-sw-inventory.md#items`, `inventory.yaml`, `cm-plan.yaml` CI versions
- Kind: gap
- Severity: note
- What happened: The product says release 1.5.1 (2026-11-07) fixed PT-1 and the server header, but the inventory still lists the containers at 1.5.0. Nothing says whether 1.5.1 replaced every image or only some. Updating versions would have cascaded into cm-plan CI versions and baselines without evidence.
- Workaround used: Kept 1.5.0, with the reason (the inventory follows the production release; nothing is in production yet) given in ART-INV's I-2 section under INT-139.A1.
- Recommendation: Add a release history to the product template (release, date, environments, changed components).

### F-10-10: Persona cards have no Implement-step questions (more evidence for F-01-12)
- Where: `personas/PER-DEV.md`, `PER-ISSE.md`, `PER-CCP.md`, `PER-ISSM.md`
- Kind: doc
- Severity: minor
- What happened: None of the four cards has an `I (I-1)` or `I (I-2)` entry, though each is R in one or both tasks. The I-1 playbook's interview table supplied the question focus. I-2's generated body points to the cards' "Question bank by step for step I", which does not exist.
- Workaround used: Used the I-1 interview table and the I-2 done-when list.
- Recommendation: Add I-1/I-2 questions: DEV (scan tool, benchmark releases, open rule IDs, what changed since the plan), ISSE (deviations from the plan, application checklist), CCP (how inherited settings reach this tenant, what evidence), ISSM (which statements are stale, plan update approval).

### F-10-11: The I-1 playbook and the rules worked well (positive)
- Where: I-1, I-2
- Kind: positive
- Severity: note
- What happened: The I-1 playbook's step 5 schema walk-through and example made stig-summary.yaml quick to write. STIG-001, STIG-002 and SCFG-001 passed on the first cycle. The `rmf status` touched_by messages listed exactly the six artifacts I-2 owed. Step 8 ("leave the SSP alone, journal a NOTE for I-2") made the hand-over between the two tasks clean. I-2 passed `--task I-2` on the first cycle; the only retry was MPLAN-001 (F-10-2).
- Workaround used: none needed.
- Recommendation: Use I-1's authored body as the model for the generated I-2 body.

### F-10-12: Deviations from the brief and the protocol
- Where: run files
- Kind: friction
- Severity: note
- What happened: (1) Several run files were changed with targeted edits instead of whole-file writes (INV-8): assumptions.yaml (ASM-018, ASM-019 added), the SSP family files cm.yaml, pl.yaml and ca.yaml, cm-plan.yaml, and the ART-* updates. Each file was left whole and valid, and the schema checks pass. plan-reviews.yaml and the new files were written whole. (2) I-2 edited stig-summary.yaml and ART-STIG, which are I-1's files (the STG-001 remap). This is recorded in a journal NOTE; `--task I-1` stays at 0. (3) S-4's sections of ART-SSP (open items for ca-7, cm-6 and pl-2) and of ART-CMP (Baseline configurations) were corrected in place at I-2, with the correction named in each I-2 section.
- Workaround used: as described.
- Recommendation: none beyond F-06-8 (record which task edited another task's data file).

## Session summary

- Tasks done: I-1 (stig-summary.yaml, ART-STIG; INT-135 to INT-137; ASM-018, ASM-019) and I-2 (plan set version 1.1: cm-6, pl-2 and ca-7 statements, cm-plan.yaml, plan-reviews.yaml; I-2 sections in ART-SSP, ART-SD, ART-INV, ART-CMP, ART-CP and ART-IRP; INT-138 to INT-141). No control status changed.
- Build/check cycles: I-1, 1 (0 errors). I-2, 3: first cycle 0 errors; `--final` then showed MPLAN-001, fixed on the second; a third run confirmed. Final: `rmf build` plus plain `rmf check` 0 errors; `--task I-1`, `I-2`, `S-4`, `S-5`, `S-6`, `P-10` and `C-1` 0 errors. `rmf check --final` 155 errors (156 before this session), all owed by A-, R- and M-tasks.
- For the next session (A-1 onward): STG-001 and STG-002 (CAT II, cm-6 and ia-5, release 1.5.2 on 2026-12-10) need POA&M items. No CAT I is open. The ASD STIG checklist review of INV-002 to INV-006 (BM-04) is owed by the assessor at A-3. ART-STIG gets its `## Assessor verification` section at A-3.
