# Triage audit: repository against source, and library gaps

Date: 2026-11-01. Found while triaging every register entry against its pages; full notes by job are
in `report-excerpts.md` and `reports/`. Finding IDs continue the I-n series of
`docs/audits/2026-11-01-import-findings.md`. "Item" is the work item that closes the finding.

## Repository against source

| ID | Source | Repository | Item | Phase |
|---|---|---|---|---|
| I-27 | SP800-53AR5 0181, 0187, 0337: method selection and its rationale decide the quality of an assessment | `playbooks/A/A-2.md` step 4: "do not list them by hand" | WI-269 | p11 |
| I-28 | SP800-53AR5 0188, 0194: common controls are not reassessed at system level, only the inheritance is verified | SAR-COV-001 asks a determination of every scoped control | WI-156 | p11 |
| I-29 | SP800-53AR5 0328: assessors disregard a non-applicable requirement and can still find satisfied | `playbooks/_shared/assessment-batching.md` step 5: `satisfied` needs evidence for every objective | WI-265 | p11 |
| I-30 | DODI8500.01 0173: deviations from a STIG take AO approval | ART-STIG `## Accepted deviations` says through configuration management | WI-176 | p11 |
| I-31 | SP800-37R2 0207 and footnote 62 (0211): the FIPS high-water mark, qualified for NSS | P-6 entry criteria carry the FIPS wording unqualified for NSS, while a run follows CNSSI 1253 per objective | WI-329 | p11 |
| I-32 | DODI5400.16: "the PIA requirements exclude National Security Systems" | The Privacy Overlay selects RA-8 for NSS, and the framework has to say which holds | WI-135 | p11 |
| I-33 | SP800-37R2 0350, 0357, 0479, 0621, 0632: the SAOP is the privacy assessor | The A-3 pin has Control Assessor primary, SAOP supporting | WI-03 | p11 |
| I-34 | SP800-37R2 and DODI8510.01: Task M-4 is "Authorization Package Updates" | `framework/tasks/M.yaml` names it "Authorization Updates" | WI-330 | p11 |
| I-35 | SP800-37R2 0589: an authorization to use has no termination date | AD-ATO has `atd_required: true`, so WI-01 needs a decision type of its own, and WI-10 depends on it (0658, 0659) | WI-01 | p11 |
| I-36 | CNSSI1253F-ATT2-SPACE: 262 removals, 306 retained, 568 | The framework selects 573 at High, so five controls are unreconciled | WI-21 | p11 |
| I-37 | SP800-161R1 0277: supplier risk assessment follows the impact level | P-14 runs before C-2, and C-2 reads ART-RA | WI-331 | p11 |
| I-38 | CNSSI1253F-ATT6-PRIVACY p12: the risk level replaces the PCIL | CNSSI 1253 footnote 23 and the template's sample still use PII impact levels; a run follows the overlay, unrecorded | WI-332 | p11 |
| I-39 | DODI5000.74: PW-AOS phases are PH-PD and PH-OS | P-8's entry criterion needs PH-MSA and the Materiel Development Decision, so a PW-AOS run cannot meet it | WI-333 | p12 |
| I-40 | DODCIO-CSRMC graphic: Authorize maps to NextGen CSSP onboarding and a CSSP watch officer disconnects | DODI8510.01 gives the decision to the AO | WI-51 | p12 |
| I-41 | SP800-34R1 Appendix A: template content | S-4 step 5 and its Outputs table let ART-CP stay a one-section stub; 64 x_existing rest on the headings | WI-16 | p11 |
| I-42 | SP800-18R2 p27: major application is deprecated | DODI8500.01 keeps it, and the system-type item must not cite SP800-18R2 for that value | WI-196 | p11 |

Sources that disagree with each other, ruled in `docs/adr/ADR-0005-acceptance-criteria-from-ac-24.md`
or left to p13:

- cATO authority: DoD CISO (DODCIO-CATO, CATO-EVAL) against AO (DODI5000.90). ADR-0005 keeps both.
- SP800-39 0149 and 0175 read differently on whose tolerance the AO applies. Kept live, both noted.
- DOT&E and OT oversight: live in DODI5000.89 0011, 0025, 0074, 0075, `x_defer` in DODI8500.01 and
  DODI8510.01, deferred in DODI5000.85. One ruling for the user at p13.
- The class-of-fork rule and the persona rule collide for cloud (`reports/DTM-24-001.md`): persona
  went first, so CSO duties are work items conditional on using a CSO.

## Left for later phases

| ID | What | Where it goes |
|---|---|---|
| I-43 | Extractor misses NIST TASK statements: SP800-30R1 14 of 15, SP800-39 10, SP800-161R1 10, caught by promote | Recall figures at p13 |
| I-44 | Figure pages not on I-4: DODCIO-DEVSECOPS 14 pages, DODCIO-CATO-IG p11 Table 1, DODI5000.74 p6 | WI-53's list at p13 |
| I-45 | 27 tier 1 `x_defer` entries await the user, with no status set | p13 ruling, listed in `decisions/` by `x_defer` |
| I-46 | SP800-37R2 0001, SP800-161R1 0283, DODI8530.01 0027: live entries to re-check when evidence is built | p11 evidence |
| I-47 | DODI5000.74's 30 not-applicable entries rest on the touchpoints approval | Confirm at p13 |

## Library gaps

I-48. The register leans on these and `references/` lacks them. Entries that lean on one stay live or
are noted; nothing was invented from memory. Each job's full list is in `report-excerpts.md`.

| Gap | Who leans on it |
|---|---|
| DoDI 5200.44 | DODI5000.82, DODI5000.90, DODI8500.01, DOWI8430.01; the TSN processes item |
| DoDI 8580.1 | DODI5000.82 0098 |
| DAU AAF information requirement tables | DODI5000.02, .80, .81, .85: rows never read, `pathway-information` item |
| DFARS 252.204-7012 and neighbours | CTI safeguarding, cloud and contract items |
| DCWF, DoDI 8140.02, DoDM 8140.03 | DODD8140.01, WI-37 |
| CNSSI 1200 | CNSSP12, Space overlay: holds the detailed space requirements |
| CNSSD 504, 505; CNSSP 11, 15, 17, 18, 25, 26, 31, 32; CNSSI 1001, 1010, 1015 | Overlays, CNSSP12 |
| SP 800-137A catalog spreadsheet, SP 800-55, SP 800-92 | SP800-137A, SP800-137, WI-15 |
| 2019 DoD CIO scorecard memo | Cyber scorecard, in the AO reporting item |
| DoD Cloud Computing SRG, DoDI 8530.03, DoDM 8530.01 | DTM-24-001 |
| DoD 5400.11-R, OMB A-130, A-108, M-17-12 | DODI5400.11, overlays |
| DevSecOps Activities and Tools Guidebook, reference designs | DODCIO-CATO-EVAL, CATO-IG, DEVSECOPS |
