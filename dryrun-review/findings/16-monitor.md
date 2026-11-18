# Findings 16: Monitor step (M-1, M-2, M-3, M-5) and the final check

Session unit: the simulated first continuous monitoring cycle of `runs/20261118-synthetic-01`
(M-1, M-2, M-3, M-5 in the order `rmf status` gave). It ended with `rmf build`,
`rmf check --final` and `rmf oscal validate`. M-4, M-6 and M-7 are deferred in this run. The session
was interrupted once by a context reset during M-3 and resumed from the files on disk.

### F-16-1: The only monitoring data predates the authorization and covers an environment outside the boundary
- Where: `product/monitoring/cycle-2026-11.md` (EXT-MONITORING); M-1, M-2, M-3 and M-5 inputs; `run.yaml as_of`; AUTH-001 (2027-01-25)
- Kind: gap
- Severity: major
- What happened: The program's monitoring records cover 2026-11-01 to 2026-11-15, in the pre-production account and the pilot squadrons. The simulated decision is dated 2027-01-25 (F-15-1), so the first cycle after it (2026-11-01 to 2027-01-31, recorded on 2027-02-01) has data for only its first two weeks, ten weeks before the authorization. The data is also from an environment outside the boundary, and nothing is in production. The framework has no simulated clock, so nothing flags the mismatch. Every Monitor rule passed on records that, read literally, describe a pre-authorization environment.
- Workaround used: Treated the file as the cycle's latest data, as the handoff directed. ASM-026 states that nothing is asserted for 2026-11-16 to 2027-01-31, that determinations are not refreshed on that data alone, and that no finding is closed. Each M-record repeats the limitation: changes.yaml, the SAR M-2 section, the conmon results, the service-agreement effectiveness records, the RA/RAR/POA&M M-3 sections and SPR-001. Interviews are dated 2027-02-01, after the run's clock (F-12-2). The gap is reported to the AO as a matter for ongoing authorization in ART-SECRPT.
- Recommendation: Give a synthetic run a simulated clock (F-15-1). Have the scenario supply monitoring records dated after the authorization date its own rules force, from the authorized environment. Alternatively, add a rule that warns when an M-task's EXT-MONITORING period ends before the authorization in force.

### F-16-2: MRPT-001 needs DODIN awareness areas that no M-5 output owns and the product cannot support
- Where: MRPT-001 `_awareness` (monitor.py); `conmon.yaml reporting.dodin.awareness` (S-5's file); playbooks/M/M-5.md
- Kind: gap
- Severity: major
- What happened: For a GENSER system, MRPT-001 requires conmon.yaml `reporting.dodin.awareness` to list all eight areas of DoDI 8530.01 Encl. 3, 5.b: threats, traffic, fault, performance, bandwidth, route, network-management and employee-use. The field belongs to S-5's monitoring strategy. M-5 does not output it, the M-5 playbook never mentions it, and S-5 never asked for it, so the error first appears at M-5. The product and the agreements support three areas: threats (CSSP alerts), traffic (the CSSP correlates the access point's logs) and employee use (UAM kept in DoD hands, cloud.yaml). Nothing gives EFRAS awareness of faults, performance, bandwidth, routes or network management. The access point's agreement covers boundary protection and inspection only, and its reporting did not reach the program in the cycle (SRV-06).
- Workaround used: Recorded the three supported areas in conmon.yaml (`--task S-5` still 0) from INT-213.A2. Left the other five unclaimed. The CISO's organization-tier review sends the gap to P-7 (INT-215.A1). **MRPT-001 remains the run's one `--final` error.** It was not fixed, because fixing it would mean inventing coverage.
- Recommendation: Ask for `reporting.dodin.awareness` at S-5, with the persona question that fills it, and name the provider of each area. For a cloud system behind an enterprise access point, allow an area to be attributed to a common control provider (the access point, the CSP) rather than demanding it of the system's own ISCM. Make the M-5 playbook say that MRPT-001 reads conmon.yaml.

### F-16-3: M-5's entry criterion depends on M-4, which this run defers; `rmf status` still names M-5 next
- Where: playbooks/M/M-5.md step 1 ("Authorization artifacts current (M-4)"); framework/tasks/M.yaml; `rmf status`
- Kind: gap
- Severity: minor
- What happened: M-4 is deferred, so the authorization artifacts are not current. The pl-2, cp-2, ir-8 and cm-3 statements, ART-IRP/incident-response.yaml and stig-summary.yaml are stale (see F-16-6). Read literally, M-5's entry check says to stop. `rmf status` treats M-4 as out of scope and names M-5 next.
- Workaround used: Journal NOTE at 07:38Z. M-5 proceeded, and ART-SECRPT lists the stale records under "Matters for ongoing authorization".
- Recommendation: When a dependency is deferred, have the entry check say so: either "or deferred, with the stale records listed in the report", or block M-5. Make `rmf status` and the playbook agree.

### F-16-4: MCHG-002 asks for a root-cause response on a requested change; the schema says root_cause is for unauthorized changes
- Where: MCHG-002 (monitor.py); `changes.schema.json` `root_cause`; CHG-003
- Kind: defect
- Severity: minor
- What happened: CHG-003 (release 1.6) is a requested, significant change with `privacy_impact: true`. The checker demanded `root_cause` with a `response` for it, but the schema title describes `root_cause` as the analysis of an unauthorized change. The M-1 playbook does not explain the requirement.
- Workaround used: Gave CHG-003 `root_cause {cause: other, determined: 2027-01-20, response: POAM-001}`, the item the release remediates.
- Recommendation: Either limit the root-cause requirement to `kind: unauthorized`, or retitle the schema field and add a playbook line saying why a requested change needs it.

### F-16-5: M-1 must edit earlier tasks' files that its playbook does not list (pia.yaml, bia.yaml, boundary.yaml reads)
- Where: PRIV-005 (pia.yaml `updates`, P-14's file); BIA-003 (bia.yaml Monitor iteration); MCON-001 (reads boundary.yaml, not an M-1 input); playbooks/M/M-1.md
- Kind: gap
- Severity: minor
- What happened: A change with `privacy_impact: true` fails PRIV-005 until P-14's pia.yaml has an `updates` entry that names the change. BIA-003 needs a Monitor iteration in bia.yaml. MCON-001 judges connections against boundary.yaml, which M-1 is told not to open. All three passed on the first cycle only because the rule messages were precise. This is more evidence for the pattern in F-06-8, F-09-7 and F-15-3.
- Workaround used: Added the pia.yaml update (INT-205.A1) and the bia.yaml iteration, and checked P-14 and P-8 afterwards (0).
- Recommendation: List these files as M-1 update outputs, or add playbook steps for them, so `touched_by` records the edit.

### F-16-6: Records that ASM-025's simulated progress made stale have no Monitor owner short of M-4
- Where: ART-IRP / incident-response.yaml; ART-STIG / stig-summary.yaml; SSP pl-2, cp-2, ir-8, cm-3; cm-plan and IRP schemas (no approval field)
- Kind: gap
- Severity: minor
- What happened: R-3 recorded under ASM-025 that the PM approved the plans on 2026-12-15 and that the container checklist was completed on 2027-01-08. The handoff asked for the stale records to be cleaned up. M-1 could update the inventory, the cm-plan header and the contingency record of changes. ART-IRP and ART-STIG have no Monitor updater, and the cm-plan and IRP schemas have no approval field to record the approval in. The SSP statements belong to M-4.
- Workaround used: Cleaned what M-1 owns. Left the rest in a journal NOTE (07:14Z) and in ART-SECRPT for M-4. POAM-012's "plan references the approved PIA" milestone is recorded as slipped (M-3).
- Recommendation: Add an `approval` block to the cm-plan and incident-response schemas. Name a Monitor updater for ART-IRP and ART-STIG (M-1 for changes, M-2 for rescans).

### F-16-7: The three-family session limit conflicts with an M-2 unit where most families are due
- Where: AGENTS.md "Session units ... at most 3 control families"; playbooks/M/M-2.md; conmon.yaml frequencies
- Kind: friction
- Severity: minor
- What happened: At 2027-02-01, au, cm, ra, sa, sc, si and sr (continuous to monthly), ca-5, ca-7 and cp-9, and about 15 POA&M-due controls were all due. Only three families fit in a session.
- Workaround used: Assessed cm, ra and ca, and carried the rest to the next ongoing assessment session, recorded in ART-SAP and the SAR M-2 section.
- Recommendation: Let M-2 run as several sessions with a carried-over list that `rmf status` tracks, or state that M-2's family limit is per sub-session.

### F-16-8: M-2 header lists ART-SAP as an output, but the body never says what to write; the playbook's date stamp uses as_of
- Where: playbooks/M/M-2.md (Outputs, step 4); ART-SAP
- Kind: doc
- Severity: minor
- What happened: The Outputs table lists ART-SAP, but no step says what M-2 adds to it. The playbook also suggests an "M-2 <as_of>:" prefix, while `as_of` (2026-11-18) predates the assessment itself.
- Workaround used: Added "## Ongoing assessment plan (M-2)" to ART-SAP (scope, carried families, evidence limits), and dated the M-2 records 2027-02-01.
- Recommendation: Add an ART-SAP bullet ("the ongoing assessment scope for this session and what is carried"), and use the cycle date rather than `as_of`.

### F-16-9: MSR-01 (mean time to remediate) has no value when nothing closes in the cycle
- Where: MMEAS-001; conmon.yaml `measurement`
- Kind: gap
- Severity: note
- What happened: MMEAS-001 needs a numeric result. No high finding closed, so the mean is undefined.
- Workaround used: Recorded 104, the age of the two open highs, which is the floor of the mean once they close. The analysis says so.
- Recommendation: Allow `value: null` with a reason, or define the measure to include open items' ages.

### F-16-10: VULN-004/005 need CVSS scores and six cost factors that monitoring records rarely carry
- Where: VULN-004, VULN-005 (vulnerability.py); `poam-items.schema.json` `vulnerabilities`
- Kind: friction
- Severity: minor
- What happened: The product gives only "one new medium finding in the web framework runtime (INV-016)". The rules need a CVSS 3.1 score, C/I/A loss ratings, an advisory, and asset value, exposure factor, SLE, ARO, ALE and TCO as numbers.
- Workaround used: Recorded them as the ISSM's estimates under ASM-027 (INT-210.A2), and described the advisory as "identifier not in the program's records".
- Recommendation: Let the cost factors be omitted with a reason (DoDI 8531.01 frames the calculation as a consideration). Add these fields to the scenario's monitoring data so a synthetic run does not have to estimate them.

### F-16-11: ASMT-006 (triage of a new finding) is charged to M-2, but the triage is the PM's
- Where: ASMT-006; playbooks/M/M-2.md; FND-025
- Kind: friction
- Severity: minor
- What happened: The first `--task M-2` check failed on ASMT-006 because FND-025 had no triage block. The triage is the PM's decision, but the M-2 RACI centres on the assessor, so a PM interview inside M-2 was needed.
- Workaround used: Added INT-209 (PM) and the triage block. Second cycle: 0. Journal RETRY at 07:33Z, which corrects the M-2 CHECKPOINT's "first cycle" claim.
- Recommendation: Have the M-2 playbook say that a new finding needs the PM's triage before the task ends, and list PER-PM as R for that step.

### F-16-12: SRA-004's control count goes stale silently when M-3 adds a finding to a risk
- Where: SRA-004; rar.yaml `controls_by_level`; playbooks/M/M-3.md
- Kind: friction
- Severity: minor
- What happened: Adding FND-025 (cm-3) to RSK-004 changed the number of controls at the moderate level from 10 to 11. SRA-004 failed on the first M-3 check.
- Workaround used: Updated the count. Second cycle: 0. Journal RETRY at 07:33Z.
- Recommendation: Have `rmf build` derive `controls_by_level` from the risks, or add a line to the M-3 playbook.

### F-16-13: `rmf status` sends the run back to A-6 after a new M-2 finding
- Where: `rmf status`; SAR-POAM-001; RAR-001
- Kind: friction
- Severity: minor
- What happened: After M-2 added FND-025, `rmf status` named A-6 as next (no POA&M item, no risk), although M-3 owns both in Monitor. This is more evidence for F-15-5.
- Workaround used: Went on to M-3, and recorded this in a journal NOTE (07:22Z).
- Recommendation: As F-15-5: in Monitor, attribute a new finding's POA&M and risk gaps to M-3.

### F-16-14: No rule says whether a CSSP vulnerability alert is a directed action
- Where: playbooks/M/M-3.md Done-when (EXT-DIRECTIVES); `directed_actions` schema
- Kind: gap
- Severity: note
- What happened: The cycle has "one alert relevant to the managed Kubernetes version" from the CSSP. The provider patched it. The schema needs an IAVM reference and an issuing authority (CDRUSCYBERCOM, JFHQ-DODIN and so on), and the product gives neither.
- Workaround used: Treated it as a provider advisory, not a directed action. This is stated in ART-RA, ART-POAM and the journal.
- Recommendation: Say in M-3 how to classify a CSSP alert that carries no IAVM number. Have scenarios mark which alerts are IAVM.

### F-16-15: The `external_service` field reads differently in the schema and the rule
- Where: `changes.schema.json` `external_service` ("status altered"); MRPT-001 message ("which external service it touches")
- Kind: doc
- Severity: note
- What happened: CHG-002 is the cloud provider's own control-plane patch, and the provider is an external-service leveraged authorization (LA-01). Under the schema's wording it is not a status change. Under the rule's wording it touches the service and would need reporting to USCYBERCOM.
- Workaround used: `external_service: null` for CHG-002 (a routine patch in the announced window, no status change).
- Recommendation: Use one wording in both. Define "status change" (outage, loss of authorization, CPCON) separately from "touches".

### F-16-16: Persona cards lack M-step questions for the PM and the ISSO
- Where: personas/PER-PM.md, personas/PER-ISSO.md `## Question bank by step`
- Kind: gap
- Severity: minor
- What happened: The M-1, M-3 and M-5 playbooks say to take questions from the cards for step M. The PM and ISSO cards have few or no Monitor questions. This is more evidence for F-15-12.
- Workaround used: Wrote the questions from the playbooks' Done-when lists.
- Recommendation: Add Monitor questions to the cards: the change log, root cause, risk response, condition status and the posture report.

### F-16-17: The ART-CMP template comment and the M-1 playbook name different update sections
- Where: templates/artifacts/ART-CMP.md (comment "## Change updates"); playbooks/M/M-1.md ("## System and Environment Changes (M-1)")
- Kind: doc
- Severity: note
- What happened: The template comment and the playbook name different section headings.
- Workaround used: Followed the playbook.
- Recommendation: Align the template comment with the playbook.

### F-16-18: Monitor change and plan-update rules give precise, actionable messages
- Where: MCHG-001..003, PRIV-005, UPD-002, BIA-003, MRPT-003
- Kind: positive
- Severity: note
- What happened: M-1 passed on its first check cycle. Each cross-file duty, such as the PIA update for a privacy-impacting change, the plan change for a significant change and the BIA iteration, was named exactly in the rule message, file included. MRPT-003's plan-change window caught the pre-authorization version 1.1 that the report period covers.
- Workaround used: none needed.
- Recommendation: Keep this message style. Bring SRA-004 and ASMT-006 up to it by naming the task that should act.

### F-16-19: Process deviations in this session
- Where: run files under `runs/20261118-synthetic-01`
- Kind: friction
- Severity: note
- What happened: Run-data YAML and artifact Markdown were changed in place with the Edit tool rather than rewritten whole (INV-8). Every edit kept the file whole and valid, and was checked by `rmf build` and `rmf check`. Interviews and Monitor records are dated 2027-02-01, after the run's clock (F-12-2). The conmon.yaml `awareness` field (S-5's file) was edited at M-5 (F-16-2). The journal's M-2 CHECKPOINT wrongly said "0 on the first cycle"; a later RETRY corrects it, because the journal is append-only.
- Workaround used: as described.
- Recommendation: Let INV-8 allow tool-mediated in-place edits that leave the file whole, or provide an `rmf` write helper.

## Session summary

- Tasks done:
  - M-1: changes.yaml and ART-CHG (CHG-001 to CHG-003, CON-001/002), inventory, PIA, BIA, plan change 1.3, contingency record.
  - M-2: cm, ra and ca assessed; new FND-025; MRS-01/02; service-agreement effectiveness for all five agreements; ART-SAP ongoing plan.
  - M-3: POAM-025, POAM-026 with VUL-001, two milestone slips, RSK-004 extended, three risk timelines moved to the conditions, COND-01..06 tracked in ART-RAR.
  - M-5: SPR-001 with the organization tier review, and ART-SECRPT.
  - Then `rmf build`, `rmf check --final`, plain `rmf check` and `rmf oscal validate`.
- Build/check cycles: M-1 1; M-2 2 (ASMT-006); M-3 2 (SRA-004); M-5 1 (MRPT-001 left); the final pass 2 (before and after the journal update).
- Last results:
  - `rmf check --final`: **1 error**, MRPT-001, five DODIN awareness areas not covered (F-16-2). Not fixable without inventing coverage.
  - Plain `rmf check`: 0.
  - `rmf oscal validate`: 0.
  - `rmf status`: 43/44 active tasks done, 3 deferred, M-5 open on MRPT-001.
  - The handoff's MCHG-001, SVCA-002 x5 and the earlier MRPT-001 are resolved.
- Left:
  - The MRPT-001 awareness gap (an S-5/P-7 strategy decision).
  - M-4, deferred: the stale SSP statements (pl-2, cp-2, ir-8, cm-3), ART-IRP and stig-summary.yaml.
  - The ongoing assessment of au, sa, sc, si, sr, cp-9 and the POA&M-due controls, carried to the next M-2 session.
  - Verification of release 1.6 fixes under COND-01 and COND-05.
  - POAM-024's first milestone (monthly roll-up), met by SPR-001, still to be marked in the next POA&M update.
