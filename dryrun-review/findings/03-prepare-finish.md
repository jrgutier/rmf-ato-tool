# Dry-run findings 03: Prepare, finish (P-14 to P-18)

Run: `runs/20261118-synthetic-01` (synthetic, EFRAS). Session unit: finish P-14, then P-15 to
P-18. All five tasks reached 0 errors with `rmf check --task <T>`.

### F-03-1: The F-02-1 workaround works, but its cascade costs a lot and leaves the run contradicting itself undetected (evidence for F-02-1 and F-02-14)
- Where: P-14; `scrm.yaml` `criticality.functions`; SCRM-001/002/003/005; `bia.yaml`; later S-4 (SCRM-009, SCRM-012)
- Kind: defect
- Severity: major
- What happened: As the orchestrator decided, I recorded CF-01 (the nightly ingest and the integrity of readiness data, on INV-004, INV-008 and INV-010) only to satisfy `minItems: 1`. The rules then demanded the following, none of which the BIA supports:
  - SUP-01 (ERST) and SUP-03 (the cloud provider) became `critical` (SCRM-001).
  - Two full supply chain risk assessments, SA-01 and SA-02, covering all 18 Table 28 factors (36 factor records), plus SCRSS level, escalation, review and handling (SCRM-003/004/005).
  - `focal_point.threat_analysis` could no longer be `not-required` (SCRM-002). That meant a TSN threat analysis request and a DIA SCRM TAC request (TAC-01) that the PM had earlier said were not needed (INT-037.A5).
  - The TSN practices `hardware-assurance` and `anti-counterfeit` (SCRM-002, DoDI 5000.83 minimum mitigations), for a program that owns no hardware. I recorded them as inherited from the cloud provider's authorization.
  - Two extra interviews (INT-039 PM, INT-040 ISSM) and ASM-012.
  - Owed later at S-4: C-SCRM plan relationships and monitoring for both "critical" suppliers (SCRM-009, SCRM-012).

  P-14 passed on the first build/check after the change. But the run now holds `bia.yaml` "no mission-critical function", `scrm.yaml` CF-01 with two critical suppliers, and `pm_actions.risk_tolerance.basis` "no mission-critical function", and no rule compares them. BIA-001 checks only bia.yaml against itself.
- Workaround used: CF-01 is worded as "the program's most important function, recorded because the schema requires an entry". ASM-012 and ART-RA say so plainly, and every extra record cites ASM-012.
- Recommendation: Fix F-02-1 (allow an empty `functions` with a rationale). Then add a consistency rule: `scrm.yaml criticality.functions` must be empty when `bia.yaml mission_critical` is false, and must name the BIA functions when it is true. Make SCRM-002's hardware and anti-counterfeit demands conditional on the system having hardware (inventory kinds), or let "inherited" be recorded explicitly.

### F-03-2: HOST-001 at P-16 requires service-agreements.yaml, an S-4 output
- Where: P-16; HOST-001 (`src/rmf_tool/check/rules/cloud.py` lines 667-670); `artifacts/data/service-agreements.yaml` (S-4)
- Kind: defect
- Severity: major
- What happened: The first P-16 check failed with `HOST-001 artifacts/data/boundary.yaml: the cloud assessment says the system is cloud-hosted and service-agreements.yaml does not name the cloud among its environments`. That file is written at S-4, ten tasks later. Neither the P-16 playbook nor its inputs mention it. The only honest P-16 value is `cloud.assessment: cloud-hosted`, because the rule also refuses `environment: cloud` with any other assessment.
- Workaround used: On the second attempt I wrote service-agreements.yaml early with only what P-16 knows: `dodin_connected: true`, `system_environments: [cloud]`, `agreements: []`. The journal has a RETRY and a note that S-4 must rewrite it whole. P-16 then passed.
- Recommendation: Run the service-agreements cross-check only once S-4 is in scope, or check it from S-4's side. Alternatively, let P-16 own `system_environments` in boundary.yaml `hosting` and have S-4 read it from there.

### F-03-3: The P-15 playbook lists scrm-acquisition.yaml as a P-15 output, but everything else puts it at P-17
- Where: `playbooks/P/P-15.md` step 4 and Outputs; `templates/data/scrm-acquisition.yaml` header ("P-17"); SCRM-007/008/015 and SCRMLC-001 (all P-17)
- Kind: doc
- Severity: minor
- What happened: P-15 says to write `scrm-acquisition.yaml` whole. Its template, its four rules and the P-17 Done-when bullets say it is P-17's file. It also needs requirements allocated to `contract`, which only P-17 does. Nothing at P-15 checks for it.
- Workaround used: Wrote it at P-17. Journaled at the P-15 CHECKPOINT.
- Recommendation: Drop scrm-acquisition.yaml from P-15's outputs in `framework/tasks/P.yaml` (leave ART-REQ's file list as is).

### F-03-4: Whether the system is an NSS has no single home, and the run disagrees with itself
- Where: P-16 `nss-assessments.yaml nss`; P-14 `ra.yaml external.connections[].nss`; P-4 INT-010.A1; ART-PIA (NSS exclusion); PPROT-006; facts.yaml (no NSS fact)
- Kind: gap
- Severity: major
- What happened: The previous handoff expected `nss: true`. P-4's simulated risk board said "its systems are national security systems". P-14 marked every connection `nss: true`. EFRAS is a logistics decision-support application with no classified information, which the statutory definition excludes. If the run recorded `nss: true`, PPROT-006 would demand an NSA assessment before DP-SWP-EXECUTION (2026-03-02), which would have to be invented. The CIO's P-16 answer (INT-051.A1) gives `nss: false`. No rule notices that ra.yaml and nss-assessments.yaml disagree. The NSS status drives several rules (PPROT-006, AODM-011, SRA-002, the PIA exclusion), yet it is not a system fact. INV-4 suggests it should be one.
- Workaround used: Recorded `nss: false` with the CIO's reasoning. Journaled a NOTE that the INT-010.A1 wording and ra.yaml's nss flags should be revisited. I did not edit them, because they are other tasks' outputs.
- Recommendation: Make `nss` a fact in facts.yaml (set at P-16 or C-1, with its basis), have every rule read it, and add a consistency check against ra.yaml connections. Give P-12 or P-16 a short decision aid for the statutory NSS test, and explain that "uses CNSSI 1253" does not mean "is an NSS".

### F-03-5: The playbooks and the templates name different headings for the P-16 and P-17 sections
- Where: `playbooks/P/P-16.md` step 4 vs the ART-BND template comment; `playbooks/P/P-17.md` step 4 vs the ART-REQ template comment
- Kind: doc
- Severity: minor
- What happened: P-16 says to add `## Enterprise Architecture (P-16)`, while the ART-BND comment says to append `## Connections and approvals`. P-17 says `## Requirements Allocation (P-17)`, while the ART-REQ comment says to add an "Allocated to" column plus `## Allocation` and `## Contract requirements`. The P-16 body also never says which boundary.yaml keys it adds (`dodin`, `connections`, `hosting`); only the template's comments and the Done-when bullets reveal them.
- Workaround used: Used the playbook H2 and put the template's sections under it as H3. Allocation is a separate table rather than a new column.
- Recommendation: Generate one wording for both, and name the boundary.yaml keys in the P-16 step.

### F-03-6: boundary.yaml connections cannot record system-to-system agreements or interim approvals
- Where: `framework/schema/boundary.schema.json` `connections[].approvals[].authority` (enum DISA, ISRMC, DSAWG, DOD-CIO)
- Kind: gap
- Severity: minor
- What happened: The EMIS connection runs on an interim e-mail approval while its MOA is under legal review. This is disclosed limitation 3, a real weakness. The supply service has a signed SLA. The approvals list accepts only DoD connection authorities, so CONN-04 and CONN-05 show `approvals: []` and the interim state appears only in the Markdown.
- Workaround used: Stated it in ART-BND prose. The agreements will reach service-agreements.yaml at S-4.
- Recommendation: Add an `agreement` block to each connection (`instrument: isa|moa|sla`, `status: interim|draft|signed`, date), so the weakness lives in one judged record that later tasks can feed into the POA&M.

### F-03-7: `infotypes.yaml privacy.sorn.contractor_operated` lacks guidance, and PRIV-007 depends on it
- Where: P-12 output `contractor_operated: false`; PRIV-007 (`privacy.py` line 450); P-15
- Kind: doc
- Severity: minor
- What happened: The cluster and database that hold the maintainer records are operated by ERST contractors, and the privacy officer wanted Privacy Act clauses in the task order. The P-12 value is false, so PRIV-007 did not ask P-15 for `contract-provisions`. P-12's playbook and schema do not explain what counts as contractor operation of a system of records (Privacy Act (m)).
- Workaround used: Added `contract-provisions` to `privacy_act` anyway (REQ-15). Journaled a NOTE feeding back to P-12.
- Recommendation: Give `contractor_operated` a title or playbook line that says what qualifies, for example "contractors operate the system or its hosting on the agency's behalf".

### F-03-8: Agent error: a P-15 claim contradicted the product, and nothing caught it
- Where: P-15 (REQ-04, CON-05, an agreement issue, INT-041 and INT-045); `product/data-flows.md#top` DF-3
- Kind: friction
- Severity: minor
- What happened: Writing P-15 without having read data-flows.md (it is part of EXT-PRODUCT), I stated that the EMIS extract carries a checksum but no signature, and built an issue and a constraint on that. DF-3 says the extract is signed by EMIS. I noticed while reading data-flows.md at P-16. P-15 had passed with 0 errors, because trace tokens are checked for existence, not content.
- Workaround used: Corrected the session's own simulated answers and the P-15 records before anything built on them. Journaled a NOTE. P-15 rechecked at 0 errors.
- Recommendation: Name the product files each task should read in the playbook (for P-15: data-flows.md, architecture.md, privacy.md), rather than "files in the run's product directory". Consider a lint that flags simulated answers contradicting a cited product passage. This is hard in general, but a reviewer checklist item would help.

### F-03-9: More product gaps: capability document, registry record, NSA assessment (more evidence for F-01-2 and F-02-12)
- Where: P-15 EXT-CAPDOC; P-18 EXT-REGISTRY; P-16 EXT-NSA-ASSESSMENT
- Kind: gap
- Severity: minor
- What happened: The product names the capability needs statement (stakeholders.md) but does not include it. It also has no operational mode summary, mission profiles, registry record or PPSM registration. SSE-001 requires all four derivation inputs. ACQLC-004 and PPROT-004 need the document's kind, date and protection content.
- Workaround used: ASM-013 (the CNS content and the ConOps sections standing in for the OMS and MP) and ASM-014 (eMASS and PPSM records, fictional identifiers).
- Recommendation: Add optional slots to the product template: `capability-document.md`, `registry.md` (registry record, PPSM), and an OMS/MP section in conops.md.

### F-03-10: Lists the rules enforce are only in the source code
- Where: REQS-002 design policy statements (the template comment points to `src/rmf_tool/check/rules/requirements.py`); SSEP-001 principle names; SSE-002 "manufacture" for software
- Kind: doc
- Severity: minor
- What happened: To address all 28 design policy statements, use the 30 accepted principle slugs, and decide whether `manufacture` is owed, I had to read rule source. Whether SSE-002 exempts manufacture depends on `product_kind`, which the agent cannot see. I listed manufacture (the factory's signed builds) to be safe.
- Workaround used: Read `requirements.py` and `engineering.py`.
- Recommendation: Have the requirements template list every DP key with its conditional flag, and the principle slugs (or generate them with `rmf checks-doc`). Have `rmf status` or the playbook state the product kind.

### F-03-11: P-15, P-17 and P-18 passed on the first cycle (positive)
- Where: P-15, P-17, P-18
- Kind: positive
- Severity: note
- What happened: Each reached 0 errors on its first build/check, with large judged records: 16 to 19 requirements, 28 design policy records, derivation and engineering, the Privacy Act rules, C-SCRM terms and 5x9 supplier screenings. The HOST-001 message in F-03-2 named the exact file and field, which made the forward dependency obvious in one read. The templates for requirements.yaml and scrm-acquisition.yaml were close enough to the schemas that no schema reading was needed for them.
- Workaround used: n/a
- Recommendation: Keep it up.

### F-03-12: Deviations from the brief and the protocol
- Where: this session
- Kind: friction
- Severity: note
- What happened:
  - Once, at the first P-14 check, I piped `rmf check --format json` into `uv run python` to count errors. Bash was otherwise used only for `uv run rmf` (with grep and tail on its output).
  - I read rule sources (`scrm.py`, `pm_scrm.py`, `requirements.py`, `engineering.py`, `privacy.py`, `protection.py`, `connections.py`, `cloud.py`, parts of `authorization.py` and `risk_assessment.py`), schemas, and SP 800-161r1 Table 29 in `references/text/` via Read rather than `rmf refs show`, because `--section "Table 29"` and the page anchor did not resolve.
  - I did not load the persona cards or `_shared/interviewing.md`. I followed the format of the existing interview files, which passed the checks.
  - I wrote one S-4 file early (F-03-2) and edited two of this session's own interview files to correct F-03-8.
- Workaround used: n/a
- Recommendation: As in F-02-18, add `rmf schema show <name>`. Make `rmf refs show` resolve table captions such as "Table 29".

## Session summary

- Tasks done:
  - P-14 finished with the CF-01 workaround (F-03-1).
  - P-15, P-16, P-17 and P-18 completed.
  - Each has a CHECKPOINT, and `rmf check --task <T>` reports 0 errors for each of P-14 to P-18.
  - The final plain `rmf check` reports 0 errors.
- Interviews: INT-039 to INT-057. Assumptions: ASM-012 to ASM-014.
- Build/check cycles:
  - P-14: 1.
  - P-15: 1, plus 1 recheck after the F-03-8 correction.
  - P-16: 2 (F-03-2).
  - P-17: 1.
  - P-18: 1.
  - 2 final full build/check passes.
- Left for the next session:
  - C-1 is next, and owes the first `registration.yaml` update.
  - S-4 must rewrite service-agreements.yaml whole, write cloud.yaml (CLOUD-001), record the REQ-18 DTM 24-001 clauses on the cloud contract (CLOUD-004), and give SUP-01 and SUP-03 plan relationships and monitoring (SCRM-009, SCRM-012).
  - P-14's ra.yaml `nss` flags and P-12's `contractor_operated` should be revisited at their next update. Journal NOTEs at 03:08Z and 03:12Z say why.
  - REQ-05, REQ-14 and REQ-16 are requirements the system does not meet yet. They should become SSP partials and SAR findings later.
