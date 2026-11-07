# Scan and figure reads for WI-50 and WI-53

Date: 2026-11-07.

What was read: two sets of page images, each compared with the text extraction.

1. WI-50 (finding I-1 in `docs/audits/2026-11-01-import-findings.md`). CNSSP12 is a scan, and its text is an Acrobat OCR layer. Every in-scope page (PDF pages 5 to 11, per `conformance/sources.yaml`) was read against the statement of each of the 66 live entries in `conformance/requirements/CNSSP12.yaml`.
2. WI-53 (finding I-4). The image-only figures on 20 pages of eight documents were read, and each was described in words. Each figure was checked against the register entries on its page and nearby, using `uv run rmf conformance page REF N`.

Method: each page was rendered to PNG with `pdftoppm` (poppler, installed at `/opt/homebrew/bin/pdftoppm`). The images were viewed one page at a time.

- CNSSP12 pages were rendered at 110 dpi (`pdftoppm -r 110 -png -f N -l N`). Each statement was compared with the printed page word by word.
- Figure pages were rendered at 80 dpi. DODCIO-CATO-EVAL Figure 3 was too small at 80 dpi, so it was cropped and rendered again at 160 dpi.
- Page numbers are the `<!-- page N -->` markers of `references/text/<REF>.md`, which are PDF page indexes. On every figure page, the caption in the image matched the caption in the text.

## CNSSP12 OCR against the scan

Of the 66 live entries, 24 differ from the printed page and 42 match it word for word. Two kinds of difference occur:

- OCR errors in the text layer.
- Truncation: a statement stops mid-sentence. The extraction puts a blank line inside the paragraph, or the sentence runs onto the next page, so the rest of the sentence never reaches the statement. Truncation is not an OCR error, but it was found by the same read, so it is listed here.

The "meaning changed?" column answers yes when the extracted words alter a number, a negation, a role or a document ID, or drop part of a duty. It answers no when a reader recovers the printed words without doubt.

| Entry | Page | Extracted | Printed | Meaning changed? |
|---|---|---|---|---|
| REQ-CNSSP12-0001 | 5 | `l. This document` | `1. This document` | No. Paragraph number only. The locator field is `l`. |
| REQ-CNSSP12-0002 | 5 | `(NSD- 42)`. The statement ends at `for securing National` | `(NSD-42)`. The sentence goes on: `Security Systems (NSS), consistent with applicable law, as amended, and other Presidential directives, executive orders, and memoranda.` | No duty is affected (the entry is not-a-requirement). The space comes from a line break, and the sentence is truncated. |
| REQ-CNSSP12-0003 | 5 | `Director of ational Intelligence` | `Director of National Intelligence` | No. The role is recoverable. |
| REQ-CNSSP12-0007 | 5 | `(l) Used to collect` | `(1) Used to collect` | No. Item number only. The locator field is `b.(l)`. |
| REQ-CNSSP12-0010 | 5 | `capabilities for CNSSP 12 current and future space NSS` | `capabilities for current and future space NSS` | No. The running header of page 6 (`CNSSP 12`) is spliced into the sentence. |
| REQ-CNSSP12-0012 | 6 | `includes non- NSS` | `includes non-NSS` (split across a line) | No. A line-break artifact. `system-of- systems` is printed that way. |
| REQ-CNSSP12-0014 | 6 | The statement ends at `usually operating at less than` | `usually operating at less than 100 kilometers (km) in altitude.` | Yes. Truncation drops the number, 100 km, that bounds the exclusion. |
| REQ-CNSSP12-0017 | 6 | `I 0. Space NSS and services` (also in the citation anchor) | `10. Space NSS and services` | No. Paragraph number only. |
| REQ-CNSSP12-0018 | 6 | The statement ends at `and Committee on National Security Systems` | It continues on page 7: `Policy 8 (CNSSP 8), Policy Governing the Release and Transfer of U.S. Government Cryptologic National Security Systems Technical Security Material, Information, and Techniques to Foreign Governments and International Organizations (Reference l).` | Yes. Truncation drops the ID (CNSSP 8) of the document that governs the control. |
| REQ-CNSSP12-0021 | 7 | `in accordance with CNS SP 22` | `in accordance with CNSSP 22` | Yes. Document ID corrupted. |
| REQ-CNSSP12-0022 | 7 | `- b. NIST SP 800-37` | `b. NIST SP 800-37` | No. A stray leading dash. |
| REQ-CNSSP12-0024 | 7 | `(CNS SI 1254 )`, `(Reference o )` | `(CNSSI 1254)`, `(Reference o)` | Yes. Document ID corrupted. |
| REQ-CNSSP12-0025 | 7 | `(Reference p )` | `(Reference p)` | No. Spacing only. |
| REQ-CNSSP12-0026 | 7 | `In accordance with C SSI 1200` and `in coordination with SA` | `In accordance with CNSSI 1200` and `in coordination with NSA` | Yes. Document ID corrupted, and the coordinating role reads `SA` for `NSA`. |
| REQ-CNSSP12-0027 | 7 | The statement ends at `cybersecurity guidelines, standards, and` | It continues on page 8: `policies issued by the applicable Heads of USG Departments and Agencies having control, purview, or cognizance over the systems.` | Yes. Truncation drops whose guidelines, standards and policies the system must be consistent with. |
| REQ-CNSSP12-0028 | 8 | `for National Security Systems (References).` | `for National Security Systems (Reference s).` | Yes. The reference letter `s` (CNSSI 1253) is merged into a plural and lost. |
| REQ-CNSSP12-0029 | 8 | `CNS SP 22 requires A Os to assess` | `CNSSP 22 requires AOs to assess` | Yes. Document ID corrupted. `A Os` is recoverable. |
| REQ-CNSSP12-0043 | 9 | `the com pliancy status` | `the compliancy status` | No. |
| REQ-CNSSP12-0045 | 9 | `a CSP and SK.MP to` (also in the citation anchor) | `a CSP and SKMP to` | No. The acronym is recoverable from REQ-CNSSP12-0034. |
| REQ-CNSSP12-0051 | 10 | `CNSSI I 254 (Reference o )` (also in the citation anchor) | `CNSSI 1254 (Reference o)` | Yes. Document ID corrupted. |
| REQ-CNSSP12-0058 | 10 | `the com pliancy status` | `the compliancy status` | No. |
| REQ-CNSSP12-0062 | 11 | `requirements of CNS SI 1010` | `requirements of CNSSI 1010` | Yes. Document ID corrupted. |
| REQ-CNSSP12-0064 | 11 | `CNSSP 11 , National Policy` | `CNSSP 11, National Policy` | No. Spacing only. |
| REQ-CNSSP12-0065 | 11 | `contained in CNSSl 4009` (lowercase l; also in the citation anchor) | `contained in CNSSI 4009` | Yes. Document ID corrupted. |

Eleven entries change meaning: REQ-CNSSP12-0014, 0018, 0021, 0024, 0026, 0027, 0028, 0029, 0051, 0062 and 0065.

- Only REQ-CNSSP12-0026 changes a role, and it also corrupts a document ID.
- Three are truncations: 0014 loses a number, 0018 loses a document ID, and 0027 loses the end of a duty.
- No error changes a negation.
- Of the paragraph numbers, `l.`, `(l)` and `I 0.` are wrong in the text, but the entries' order and context make them clear.

Reason fields. Only one reason quotes a corrupted word: that of REQ-CNSSP12-0026. It names `SA` and `C SSI` as OCR losses ("the SA of the extracted text is NSA with its N lost, as in 'C SSI' for CNSSI"), so it does not treat them as the source's words. Other fields still carry corrupted text:

- The evidence `sentence` fields of 0021 (`CNS SP 22`), 0026 (`C SSI 1200`, `SA`), 0028 (`(References)`) and 0058 (`com pliancy`) copy the extracted statement. That is by design, because a sentence must match its statement.
- The `context` field of REQ-CNSSP12-0048 to 0064 reads `C SSP 12`, which is the OCR of the running header `CNSSP 12`.
- Locators `l` (0001) and `b.(l)` (0007) carry the OCR form of 1.

Nothing on pages 5 to 11 was unreadable at 110 dpi.

## Figures on the I-4 pages

The 20 pages hold 21 figures, because DODCIO-CATO-EVAL page 6 has two. "Duty not in an entry?" asks whether the figure states a must, shall or will obligation, or a required sequence of acts by a named role, that no register entry of the document states.

| Document | Page | Figure caption | What it shows | Duty not in an entry? | Nearest entry |
|---|---|---|---|---|---|
| DODI5000.74 | 5 | Figure 1. Adaptive Acquisition Framework | "Path Selection" branches into six pathways: urgent capability, middle tier, major capability, software, defense business systems and services. Each pathway shows its phases, milestones and time limits (under 2 years, 5 years or less, under 1 year). A cybersecurity arrow spans all six, and all feed Operations and Sustainment. The services row lists seven steps, from form the team to manage performance. The time limits are not in the 5000.74 text, but the figure is an overview. | No | REQ-DODI5000.74-0011 (DoD employs an adaptive acquisition framework); REQ-DODI5000.74-0012 |
| DODI5000.74 | 12 | Figure 3. Federal Category Structure | A grid naming the 19 categories, 10 common and 9 DoD-centric. Footnotes exclude construction, R&D and four supplies-only categories from services category management. The text gives only the counts. The names and exclusions are scope notes, not duties. | No | REQ-DODI5000.74-0067 (category portfolios on the federal taxonomy, 19 categories) |
| DODI5000.75 | 6 | Figure 1. Business Capability Acquisition Cycle | The five BCAC phases on a timeline, with six ATP decision points and a contract award marker. Parallel bars below run across the whole cycle: market research, IT solution, IT requirements and organizational change management. | No | REQ-DODI5000.75-0008 (ATP decision points of Figure 1 provide the framework); REQ-DODI5000.75-0010 |
| DODI5000.81 | 4 | Figure 1. Adaptive Acquisition Framework | The same chart as DODI5000.74 Figure 1. It adds a box of the six tenets of the defense acquisition system, pointing to DoDD 5000.01 and DoDI 5000.02, and an acronym legend. The tenets are not in the 5000.81 text, but they are principles, not duties. The page has no entries. | No | REQ-DODI5000.81-0005 (management principles are in DoDD 5000.01) |
| DODI5000.81 | 9 | Figure 2. Flow of JUONs and JEONs | A swimlane flow, in this order:<br>1. The CCMD submits the need, J8 JCD gatekeeps it, the FCB triages it, and JROC or DDR validates it.<br>2. JRAC assigns it, and the PM runs pre-development, development, production and deployment, and O&S, with MDA approvals between phases.<br>3. The CCMD assesses operational utility "NLT 6 mos after initial delivery".<br>4. The PM runs the post-deployment assessment with CCMD input. A rework loop checks that the work is within the original scope.<br>5. The disposition official does a disposition analysis "NLT 1 yr after deployment".<br>6. The component head and CAE decide whether to terminate, sustain, or transition to a program of record.<br>7. JROC or DDR does a validation review "two years after validation". | Possibly yes. Two timed acts appear only in the figure: the CCMD operational utility assessment within 6 months of initial delivery, and the JROC or DDR validation review two years after validation. Gatekeeping by J8 JCD and triage by the FCB also appear only here. These acts belong to CJCS issuances and may be outside run scope. | REQ-DODI5000.81-0105 (within 1 year, appoint an official to conduct a disposition analysis); REQ-DODI5000.81-0104 (post-deployment assessment) |
| DODI5000.81 | 10 | Figure 3. Urgent Capability Acquisitions | Staggered bars in order: urgent need generation, a course of action decision point, pre-development (days), the development milestone and development (months), the production and deployment milestone and that phase (months), and O&S (months to years) ending in disposition. Dashed lines mark concurrent work. The text calls the figure representative. | No | REQ-DODI5000.81-0042 (Figure 3 depicts representative activities) |
| DODI5000.82 | 5 | Figure 1. Adaptive Acquisition Framework | The same as DODI5000.81 Figure 1: the tenets, the six pathways and the legend, in the 2023 drawing. The page has no entries. | No | REQ-DODI5000.82-0005 (principles in DoDD 5000.01 and DoDI 5000.02) |
| DODI5000.83 | 20 | Figure 1. Technology and Program Protection Framework | The AAF chart with two bands beneath it. S&T Protection covers the early part and hands off to Program Protection for the rest of the life cycle. An arrow labelled "Technology Area Protection Plans for DoD Modernization Priorities" spans both bands. Only the figure shows where the hand-off falls. Some milestone labels are blurred at 80 dpi, but the structure is clear. | No | REQ-DODI5000.83-0228 (a TAPP is established for each S&T modernization priority area) |
| DODI8500.01 | 27 | Figure 1. Three-Tiered Approach to Risk Management | The NIST SP 800-39 pyramid: tier 1 organization, tier 2 mission and business processes, tier 3 information systems, from strategic to tactical risk. The down arrow reads traceability and transparency of risk-based decisions, and organization-wide risk awareness. The up arrow reads communication within and between tiers, and a feedback loop. | No | REQ-DODI8500.01-0204 (Figure 1 illustrates the three tiers); REQ-DODI8500.01-0205 |
| DODI8500.01 | 37 | Figure 2. DoD Information Technology | A tree of DoD IT with four branches: information systems (major applications, enclaves), PIT (PIT systems, PIT), IT services (internal, external) and products (software, hardware, applications). A solid box marks information systems and PIT systems "Assess & Authorize". A dashed box marks PIT, services and products "Assess" only. The text states the same split in several places. | No | REQ-DODI8500.01-0202 (RMF, including authorization, for all DoD information systems and PIT systems); REQ-DODI8500.01-0340 |
| DODI8530.01 | 34 | Figure 1. DODIN Operations, DCO Internal Defensive Measures, and Situational Awareness | A pyramid with three levels: USCYBERCOM and JFHQ-DODIN (GEOC); DoD Component NOSCs and service providers with EOCs; local control centers with data and applications. "Directed Cybersecurity and DCO actions" flow down, and "Shared Situational Awareness" flows up. Clouds show intelligence, IT, CMF teams and CSSPs. Footnote **: "EOCs will direct actions and provide cybersecurity services and implement DCO internal defensive measures with integrated service providers as the JIE is implemented within DODIN." | Borderline yes. Footnote ** is a will-statement for EOCs that no entry states. It applies only as the JIE is implemented, and it mostly repeats the NOSC direction duties. | REQ-DODI8530.01-0263 (Figure 1 represents the flow); REQ-DODI8530.01-0265 (system owners and AOs comply with actions directed by their NOSC) |
| DODI8530.01 | 35 | Figure 2. Notional View of Current and Future Integration of Cybersecurity Activities | USCYBERCOM and JFHQ-DODIN (GEOC) sit above mission partner NOCSs, the current DoD Component NOSC and CSSPs. A "JIE Transition" arrow leads to an EOC with integrated services. Below are major command and regional NOSCs, subordinate commands, and data and applications. A legend gives the system types and the direction and coordination lines. Footnote *: "Requires an MOA or contract". Footnote ** gives the page 34 EOC sentence and adds "An EOC's organizations will conduct required actions with common sets of tools provided from core data centers." | Borderline yes. The EOC will-statements in footnote ** are the same issue as on page 34. Footnote * is stated by REQ-DODI8530.01-0270. | REQ-DODI8530.01-0266 (actions implemented as directed by the joint or Component NOSC); REQ-DODI8530.01-0270 |
| DODI8531.01 | 14 | Figure 1. Vulnerability Management Process | A five-step cycle, clockwise: identification, analysis, analysis reporting, remediation or mitigation, verification and monitoring. It matches the text of section 3.1. The page has no entries, because the one sentence there is rejected as having no marker and is descriptive. | No | REQ-DODI8531.01-0118 (perform vulnerability scanning per NIST SP 800-115) |
| DODCIO-CATO-IG | 7 | Figure 1. Software Factory: cATO Viewpoint | Stacked layers. The DevSecOps platform holds continuous monitoring, active cyber defense (CSSP, incident response), a secure supply chain and pipelines (automation, control gates, repositories), and environments (development, test, staging, and production, which is optional). Below it, the infrastructure layer holds the hosting environment, either "Cloud with DoD PA or ATO" or another DoD-approved environment. The hosting label is not in the text, but it is not phrased as a duty. | No | REQ-DODCIO-CATO-IG-0015 (the software factory follows a DoD Enterprise DevSecOps reference design) |
| DODCIO-CATO-IG | 12 | Figure 2. Cybersecurity Risk Governance Group | A pie of four parts: mission owner, application development team, platform security management team, and security risk assessment team. It matches the text on page 13. | No | REQ-DODCIO-CATO-IG-0058 (the organization establishes a cybersecurity risk governance group) |
| DODCIO-CATO-IG | 17 | Figure 3. Software Factory with an Integrated Production Environment | One software factory boundary holds everything, in this order:<br>1. Code and the IDE feed the code and artifact repositories.<br>2. Pipelines 1 to N run development, continuous integration and test, with control gates between stages.<br>3. Integration and pre-production (continuous delivery) produce a release package, which goes to the released artifact repository and to production.<br>A feedback arrow runs back to the pipelines, and a management environment (support, logging, metrics, forensics) sits below. | No | REQ-DODCIO-CATO-IG-0122 (Use Case 1, inside the DSOP boundary); REQ-DODCIO-CATO-IG-0121 |
| DODCIO-CATO-IG | 18 | Figure 4. Software Factory with a Separate Production Environment | The same drawing as Figure 3, but production sits in a separate boundary. The artifact repository straddles the crossing, and feedback runs back across it. The page has no entries. | No | REQ-DODCIO-CATO-IG-0123 (Use Case 2: agreements must be in place to pass software across the boundary) |
| DODCIO-CATO-EVAL | 5 | Figure 1. Single Authorization Boundary | The same as DODCIO-CATO-IG Figure 3. | No | REQ-DODCIO-CATO-EVAL-0007 (Use Case 1); REQ-DODCIO-CATO-EVAL-0006 |
| DODCIO-CATO-EVAL | 6 | Figure 2. Multiple Authorization Boundaries | The same as DODCIO-CATO-IG Figure 4. | No | REQ-DODCIO-CATO-EVAL-0008 (Use Case 2: agreements must be in place) |
| DODCIO-CATO-EVAL | 6 | Figure 3. Software Factory/Production Boundary | A DevSecOps infinity loop, read at 160 dpi. The DEV side has plan, develop, build, test and release. The OPS side has deliver, deploy, operate, monitor and feedback. SEC is at the center. A ring of security activities surrounds the loop: secure coding, threat model, security as code, SAST, DAST, pen test, digital signing, secure transfer, configuration, patching, scanning, audit, monitoring and analysis. The outer path is labelled with the RMF steps prepare, categorize, select, implement, assess, authorize and continuously monitor. The text notes that this placement does not map onto the lifecycle phases. | No | REQ-DODCIO-CATO-EVAL-0193 (all RMF steps must be followed, and the system must be in Monitor before applying for a cATO) |
| DODCIO-CATO-EVAL | 7 | Figure 4. Assessment Method Overview | Not image-only: the figure is vector text and is already in the extraction. It shows an RMF row (prepare, assess, authorize, monitor) above eight chevrons: identify assessors, develop the assessment plan, assess the DSOP, assess teams, assess processes, develop a recommendation, authorize the cATO, and monitor risk. Bullets sit under each chevron, including that the CISO issues the authorization and decides on revocation. | No | REQ-DODCIO-CATO-EVAL-0194 (the chevron row gives the steps of the cATO assessment); REQ-DODCIO-CATO-EVAL-0021 (the CISO issues the authorization) |

Some content appears only in a figure but is not a duty:

- the six acquisition tenets (DODI5000.81 page 4, DODI5000.82 page 5);
- the federal category names and exclusions (DODI5000.74 page 12);
- the "Cloud with DoD PA or ATO" hosting layer (DODCIO-CATO-IG page 7);
- the placement of security activities and RMF steps on the DevSecOps loop (DODCIO-CATO-EVAL page 6, Figure 3).

The bullets under the chevrons of DODCIO-CATO-EVAL Figure 4 are handled two ways. Sixteen are register entries (REQ-DODCIO-CATO-EVAL-0010 to 0027). Ten siblings, such as "Identify skills", "Develop schedule" and "Aggregate findings", are rejected as label-only.

What could not be read: nothing was unreadable, but some labels were only just legible at 80 dpi and were not rendered again:

- the smallest labels in DODI5000.81 Figure 2;
- some milestone labels in DODI5000.83 Figure 1;
- the "production environment" sub-label in the DODCIO-CATO pipeline drawings.

Every label that bears on a duty was legible.
