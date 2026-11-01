# Coverage and consistency audit, 2026-10-31

Audit of commit `e996ae6` against the public NIST, DoD and CNSS documents and against the
original specification. It seeds the requirements register (`conformance/`). Findings keep
their IDs here so later phases can reference them.

## How to read this

- Three read-only audits produced the findings: NIST (`N-*`), DoD and CNSS (`D-*`) and
  internal consistency (`C-*`). High-severity items were then re-checked against the source
  text and the code. An independent review re-checked the main factual claims.
- A finding records a difference from a source. It is not a claim that a real program is
  non-compliant. Outputs of this tool remain drafts (AGENTS.md).
- The areas under "Not assessed" were not reviewed. Their absence from the findings is not
  evidence of coverage.

## Baseline

Run on unmodified `e996ae6` with `EXTRACT=1 make bootstrap` and `uv run rmf ci --release`.
Log: [`2026-10-31-baseline-release.log`](2026-10-31-baseline-release.log).

| Measure | Result |
|---|---|
| Release gate | exit 0, 16 of 16 steps passed |
| Tests | 836 passed, 5 deselected, 34:45 |
| Coverage | 95.41% (required 85%) |
| Warnings | 1: `RUN-STALE-001` on the example (known, upstream changed mid-run) |
| Working tree | clean before and after |

This closes finding C-1 in part: `rmf ci --release` does pass at this commit.

All 63 rules passed, yet the findings below exist. The rules check structure: `FW-TASK-001`
pins task IDs and names but not inputs, outputs or roles, and a citation proves that a
passage exists, not that the requirement in it is met.

## NIST findings

| ID | Source | Specified | Repository at audit | Sev |
|---|---|---|---|---|
| N-1 | SP 800-37r2 App. F, R-4, M-6 | ATO, authorization to use, common control authorization, and denial of each | Decisions are IATT, ATO, ATOC, DATO, cATO; AODM-001 rejects the rest | High |
| N-2 | SP 800-37r2 S-4, S-6, App. D | Privacy plan, approved by the SAOP before the AO | Security-only ART-SSP; PER-PRIV only Consulted on S-6 | High |
| N-3 | SP 800-37r2 A-2, A-4; 53A App. E | Privacy assessment plan and report | ART-SAP and ART-SAR templates never mention privacy | High |
| N-4 | SP 800-37r2 §2.8, App. F; 18r2 §2.3 | SCRM plan, strategy and supplier information | No artifact or external input | High |
| N-5 | SP 800-37r2 Ch. 3 potential inputs | 19 tasks name inputs the framework omits | Run protocol forbids reading unlisted inputs | High |
| N-6 | SP 800-37r2 App. F, M-6 | Time-driven frequency or ATD, review events, no ATD under ongoing authorization | Schema has neither frequency nor events; M-6 "continue" has no decision value | Med |
| N-7 | SP 800-37r2 M-1, M-3, M-7, R-5 | Updated plans, POA&Ms, SARs, inventory, registry annotation | Those outputs are missing from the tasks | Med |
| N-8 | SP 800-37r2 tasks, App. F | Existing O&M path and reauthorization | No P, C, S, I, A or R task lists PH-OS | Med |
| N-9 | SP 800-37r2 P-10 to S-4 | BIA or criticality analysis at 8 tasks | BIA exists only inside ART-CP, produced at S-4 | Med |
| N-10 | SP 800-37r2 App. F | Type, facility and joint authorization | Absent | Med |
| N-11 | SP 800-37r2 R-1, App. F | Package executive summary | Manifest only | Med |
| N-12 | SP 800-37r2 P-16 | Updated architectures, cloud plans | ART-BND only | Med |
| N-13 | FIPS 199; 60V1 §4.4 | NA confidentiality; system value derives from type values | Enum lacks NA; no rule reads infotypes | Med |
| N-14 | 53A App. E | Depth and coverage per control | Narrative only | Med |
| N-15 | 137 §3.2.1; 37r2 fn. 82 | Metrics, privacy continuous monitoring | Absent from conmon schema and template | Med |
| N-16 | All templates | Required content | No rule requires headings | Med |
| N-17 | 53B §2.1; 37r2 C-3 | PII triggers the privacy baseline and SAOP approval | `infotypes.privacy` tied to neither | Med |
| N-18 | SP 800-30 App. K | Risk assessment report content | Partly absent (App. K is exemplary) | Low |
| N-19 | SP 800-37r2 P-8, A-1 | Missions, assessor selection | Tasks have no outputs | Low |

## DoD and CNSS findings

| ID | Source | Specified | Repository at audit | Sev |
|---|---|---|---|---|
| D-1 | CNSSI 1253 App. D | Parameter Value column sets NSS minimums | Untranscribed. Example RA-5 value "at least monthly when connected" is looser than "at least every 30 days" and passed | High |
| D-2 | CNSSI 1253F Att. 2 §3, §5 | Space overlay: 83 additions, 262 removals on H/H/H | `transcribed: false`; overlay blocks are add-only | High |
| D-3 | CNSSI 1253 p10; DoDI 8510.01 §2.7.f | CDS, Intelligence and DoD KS overlays | Unknown overlay IDs fail | High |
| D-4 | DoDI 8510.01 §4.3.c(7) p26 | Component CIO concurrence at High or Very High risk | Prose only; no schema field; AODM-001 ignores `risk_level` | High |
| D-5 | DoD cATO memo pp1-3 | Dashboard, active cyber defense, reference design, SBOM, evidence to DoD CISO | Prose only; no data | High |
| D-6 | DoDI 5000.90 p11 | ATO limits; IC threat assessment within 12 months before the ATO | AODM-001 tests ATD presence only, and the 12-month rule is prose. Source is 5000.90, not 8510.01 | Med |
| D-7 | DoD cATO memo p3 | cATO leaves the underlying ATO intact | One `decision.yaml`; IATT decided at A-2 but only R-4 produces ART-AODM | Med |
| D-8 | DoDI 8510.01 Table 8, §4.4.a(8) | PAO, DoD CISO, JCA CPM, RMF TAG rep, operational commanders | No personas | Med |
| D-9 | DoDI 8510.01 §3.1.c(2) | Assess Only process | A note only | Med |
| D-10 | DoDI 8510.01 §1.2.f-g, §4.2.b(1)(b); CNSSI 1254 | Reciprocity, receiving organizations | One mention; CNSSI 1254 absent | Med |
| D-11 | DoDI 5000.90 §2.3.c, §3.3.a(2); 5000.89 §3.5.b | Cybersecurity strategy annex, PPP, TEMP, VOLT | No entries; A-2 requires a TEMP it cannot model | Med |
| D-12 | DoDI 5000.90 §3.4; CNSSI 1253 p16 | SCRM actions; SAOP approves the privacy plan | See N-2, N-4 | Med |
| D-13 | CNSSI 1253 pp8-9, §3.2.1(3) | Privacy Implementation Considerations require SAOP coordination | About 100 rows untranscribed | Med |
| D-14 | DoDI 5000.02 Ch. 2 §1.5.a | JCIDS disestablished | `EXT-CAPDOC` and C-2 still use it. 8510.01 and 5000.89 predate the change | Med |
| D-15 | DoDI 5000.90 p13; 5000.87 §3.1.b; 5000.02 §4.1.a | cATO excluded for software-enabled hardware; combined pathways | No code reads `pathway` | Med |
| D-16 | DoDI 5000.85 §3.8.c | CDD Validation before RFP release | Absent from milestones | Low |
| D-17 | DoDI 5000.85 §3.15 | O&S starts at first fielding | PH-OS entry uses MS-IOC | Low |
| D-18 | DoDI 8510.01 §3.3.a(3), §2.7.s, Tables 1, 3, 7 | Most-severe-threat rule; 8140 training; ISSO primary on P-14, P-17, S-3 | Absent; ISSM substitutes | Low |

## Internal consistency findings

| ID | Evidence | Sev |
|---|---|---|
| C-1 | Phase 8 had no recorded `rmf ci --release` pass. The baseline above closes this. GitHub Actions has 0 runs; only one push has occurred, and the cause is unproven | High |
| C-2 | `playbooks/R/R-4.md` and `templates/data/decision.yaml` let R-4 issue AD-IATT though `decided_in` is A-2. AODM-001 never reads `decided_in` | Med |
| C-3 | Example decision dated 2026-10-29, SAP schedules assessment from 2026-11-09 | Med |
| C-4 | L-0036 fixed only in the example; `M-2.md` expects `product/monitoring/`, the fork template has no guidance | Med |
| C-5 | Only 15 of 35 negative specs run on the example, though the docstring of `test_example_non_vacuous.py` implies all do. `test_example_base_coverage_ge_80pct` was never built | Med |
| C-6 | `ca-2` and `ca-2.1` remain `planned` in the SSP while the SAR says `satisfied` | Med |
| C-7 | `product-profile` and `baseline` schemas are not validated at runtime | Low |
| C-8 | Stale statements at `README.md:4`, `README.md:48-50`, `AGENTS.md:26`, `AGENTS.md:148` | Low |
| C-9 | AGENTS.md repo layout omits `examples/`, `docs/adr/`, `docs/CHECKS.md`. `rmf new` already creates a run, so fork step 5 creates a second | Low |
| C-10 | `--no-examples` absent. `rmf ci --profile p7` runs slow e2e only with `--slow` | Low |

## Reference currency

Checked 2026-10-31 against public sources.

- Pinned DoD PDFs carry their latest changes: 5000.02 Change 2 (2026-04-08), 5000.80 Change 1
  (2024-11-25), 5000.85 Change 1 (2021-11-04). Only the `revision` labels in `index.yaml` lag.
- No reissue or cancellation of DoDI 8510.01 was found. This is a search result, not proof.
- The SP 800-53 catalog is pinned at 5.2.0. Seven controls are in it but absent from the
  pinned SP 800-53 PDF text: IA-13, IA-13(1), (2), (3), SA-15(13), SA-24, SI-2(7).
- CSRMC was announced by the DoD CIO in September 2025 and maps its phases onto RMF steps.
  No implementing issuance was found, so RMF stays the process model.
- 7 cited PDFs are marked `required: false`, which their citation counts do not support.

## Verified as correct

- All 1,007 live CNSSI 1253 Appendix D C/I/A rows match an independent PDF parse.
- NIST cross-check of baselines, with the differences ADR-0002 documents.
- Classified overlay on all 108 controls; Privacy overlay set totals.
- Space overlay arithmetic: 573 = 262 removed + 306 unchanged + 5 in neither table (SA-8(1),
  SA-8(3), SA-8(4), SA-9(3), SC-7(13)).
- All six AAF pathways and every DoDI 5000.88 review.
- 63 rules implemented, wired and fixtured; AGENTS.md CLI table matches the code both ways.
- No unknown IDs in playbooks, personas or templates; all 22 persona cards match.
- No `xfail`, `.only`, TODO, FIXME or NotImplementedError in `src/` or `tests/`.
- The example run is non-vacuous: 524 controls, 69 findings, 69 POA&M items, 115 interviews.

## Source conflicts

Recorded so they are resolved deliberately, not by accident.

- **cATO approver:** DoDI 5000.90 says the AO may authorize; the cATO memo says the DoD CISO
  approves.
- **3-year ATO update:** DoDI 5000.90 attributes it to DoDI 8510.01, whose 2022 edition has no
  such limit; 5000.90 cites the 2014 edition.
- **ATO before Milestone C:** the sources do not state it.
- **Space overlay:** see the 5 controls above.

## Not assessed

- RMF Knowledge Service content (not public).
- SP 800-60 Vol. 2 per-type values; SP 800-160 process by process; SP 800-34 §4.5 and its
  templates; FIPS 200's 17 areas individually; SP 800-37r2 Appendix G, §2.6 and §2.7.
- Figures other than DoDI 5000.90 Figure 2; overlay guidance text; Space appendices.
- DoDI 5000.80, 5000.87, 5000.88 and DevSecOps were keyword-searched, not read in full.
- Most playbook bodies, persona prose, and citation accuracy beyond existence.

## Resolved after the audit

- **cATO approver:** AO decides, and a recorded DoD CISO approval is also required (ADR-0005).
