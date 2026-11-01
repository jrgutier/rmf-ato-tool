# Report excerpts: source conflicts and library gaps

Copied by script from reports/*.md, one section per job. The reports are the source; audit.md lists what drives work.


## CNSSI1253

- Source conflicts
- WI-13 asks for NA in the enum. 0046 'Retain the three impact levels' and 0007's precedence keep c, i, a at low, moderate, high for NSS, so NA can stop at the information type at most. Decide before WI-13 changes facts.schema.json.
- Footnote 23 sends the reader to 'the different impact levels of PII' in the Privacy Overlays; the attachment's privacy risk analysis 'replaces the analysis to determine a privacy confidentiality impact level'. pii-impact-adjustment must rest on that analysis.
- High water mark: Section 1.2 rejects FIPS 200's, 3.1.2 requires one per objective. Not a conflict; C-2 follows it.
- Section 3.2.2 applies overlays at S-2; the tool decides them at C-2 before C-3. 0061 notes it, and S-2 step 3 revisits them.

## CNSSI1253E-ATT1-TEMPLATE

- Source conflicts
- 0029 says the Privacy Overlays have 3 columns; the current one has 4 sets and an optional column.
- 0051 and 0064's PII samples use the PCIL form, which the Privacy Overlays replaced.
- 0012 to 0022 are an older Space overlay than the August 2025 attachment.
- 0008 labels 45 CFR parts 'Federal Acquisition Regulations'.
- References the library lacks: none needed beyond WI-22's CDS Overlays.

## CNSSI1253E-ATT5-CLASSIFIED

- Expected shares: retired 0%, noise 16/43 = 37%. No flag.
- Source conflicts
- 0007 cites the template as August 2013; the library's attachment is December 2022.
- 0043's third class, networks with non-US persons, names no overlay the library or WI-22 holds. See 0015.
- References the library lacks: CNSSD 504, 505, CNSSP 15, 17, 18, 25, 26, 32, CNSSI 1001, EO 13526, EO 13873, NSM-8, CDS Overlays and Intelligence Overlay (WI-22).

## CNSSI1253F-ATT2-SPACE

- Conflict to settle in WI-21: 262 removals + 306 retained = 568, but framework/baselines/cnssi-1253.yaml selects 573 at High on any objective. Five controls are unreconciled; I did not find which.
- References the library lacks: CNSSI 1200 (Applicability cites it), Aerospace TOR-2023-02161, SPARTA website.
- Source conflict: none other than the 568 and 573.

## CNSSI1253F-ATT6-PRIVACY

- Source conflicts
- 0067 cites 'Appendix D provides system risk analysis use cases'; this document has one Appendix and no use cases.
- Page 12 says the risk level replaces the PCIL; CNSSI 1253 footnote 23 and the template's sample still use PII impact levels. See 0049.
- Page 11: no control set for PHI; pii-phi-issuances should know.
- WI-13 NA and overlay removal: none here; AC-2(8) is the only -- row and sits in no NSS baseline, so nothing is removed.
- References the library lacks: CNSSI 1015, CNSSP 11, 15, 17, 25, 26, the FPC Collaboration Index, OMB M-17-12, A-130.

## CNSSI1254

- FLAG: the x_existing on RAR rows reads ART-RA and ART-RAR together as the RAR. ART-RA is `package: supporting`, ART-RAR `core`, and threat events and vulnerabilities live only in ART-RA. If the lead wants them in the core document, 0074 0075 0078 0082 0083 move to WI-18.
- FLAG: 0114 is held by the shape of decision.yaml, one object per run. No rule tests it. 0114 is my weakest x_existing.
- Source conflicts:
- 'must be captured' (8.b, 0012) against 'provide guidance' (Annex C para 2, 0019; para 5, 0005). I took must: the cover says the Instruction prescribes minimum standards.
- Annex D 2.d (0117) says a receiving AO issues no new ATO; 3.b (0121) says the AO may issue a separate authorization; 5.f (0141) has an authorization to connect; DODCIO-RECIPROCITY has an ATU. Decision type stays with WI-01.
- 0104 limits the decision to ATO or DATO; 0040 lists five statuses, including IATT and no determination. Neither fits AD-* exactly.
- 0118 gives a refusal 'upon request'; DoD's 10 business days is stricter, not a conflict in effect.

## CNSSI4009

- FLAG: this leaves the document with no live entry. 0001 is an applicability clause, decided as CNSSP22 0013, DODI8531.01, DODI5400.16 and others were: it says whom the glossary reaches and names no act. conformance/sources.yaml `basis` calls it 'the one binding sentence', which it is only in that nothing else here could bind; nothing in framework/, playbooks/ or templates/ cites CNSSI 4009. If the user wants the glossary to bind a run, the home would be a run-wide term rule, which is new work. Not a false exclusion.
- Source conflicts: none.

## CNSSP12

- FLAG, the class rule. The brief says a duty only one class of fork has is not-applicable. Every entry here is written for space NSS, so read literally that retires the document. I applied it this way:
- Substance every fork has, with space only as the subject (RMF, roles, core documents, FISMA, patching, incidents): held or slugged as for any fork. 0016 0021 0022 0024 0027 0032.
- Space-only and carried by a control the Space Platform Overlay adds: WI-21. 0017 0030 0031 0036. The controls are unselected today (I checked the baseline), and their guidance states the duty: SC-51 secure boot and root of trust, SI-4(7) on-orbit IDS, SC-8(3)/(4) TRANSEC, CP-12 and SI-17. This matches REQ-DODI8500.01-0355's x_gap, 'CNSSP 12 at WI-21', and overlay section 4 takes its scope from CNSSP 12.
- Space-only with no open item: not-applicable with the condition. 0037 (launch vehicles), 0055 (contracts against this policy).
- FLAG: an overlay transcription binds these only if WI-21's closure tests that a space run selects those controls. Transcribing the overlay alone does not show a secure boot is built.
- FLAG: CNSSI 1200 (Aug 2025), which holds the detailed space requirements and the exceptions to 14.a, is not in references/index.yaml. Nor are CNSSD 505, CNSSI 1010, CNSSP 11, 15, 31 or CNSSD 502. Entries 0026 0028 0034 0035 0037 lean on 1200; a space fork cannot read them from this repository.
- Source conflicts:
- Reference letters in the body run one behind Annex B from s on: CNSSI 1253 is s in the body and t in Annex B, whose s is PL 114-113; CNSSI 1253F2 t and u; CNSSD 502 w and x; CNSSI 1010 x and y; CNSSP 15 y and z; CNSSP 11 z and aa.
- 14.c prints 'CNSSP 3 (Reference u)' (read at 200 dpi). Annex B has no CNSSP 3; CNSSP 31, the TRANSEC policy, is at v and CNSSI 1031 at w. Likely a printing error; the statement stands as printed.
- Annex A calls CNSSI 4009 Reference aa; para 17 and Annex B say bb.
- 13.b gives SP 800-37 the Revision 1 title; Annex B n says Rev. 2 with that same title.

## DODCIO-CATO-EVAL

- FLAG, extraction: page 10's 0041 makes bold items deliverables, and the text has no bold. Nine deliverables are rejected as labels: System CONMON Strategy, Business Rules, Automated Monitoring Information, Incident Response Plan, Continuous Vulnerability Management Documentation, Security Testing and Documentation, Activities and Tools Mapping, Insider Threat Monitoring, Onboarding/Offboarding. I treated all bold noun labels as nouns under 0041, whose x_note lists every bold item from the PDF font. Anything that reads the register alone will not see which items are deliverables.
- FLAG, entry size: 0028 holds six duties across pp. 7-8 in one entry, and an entry binds one item. Decided by its 'shall' as cato-revocation; x_gap sends the rest to cato-risk-tolerances, cato-conmon-content, cato-cnapp and WI-26. Promoting the p. 8 sentences would restate text the extraction joined, so I left it.
- Source conflicts: (1) who decides: this document says the CISO grants and the DoD CISO holds approval authority (0021, 0031, 0106); AD-CATO has decided_by: PER-AO, and M-6 R and A is PER-AO. Bound to WI-27. (2) P. 3 sends the package to DCIO(CS); pp. 10 and 13 say DoD CISO. (3) 0028: reverting needs the originating AO's approval and a new workflow; DODCIO-CATO p. 3 says the cATO does not affect the underlying ATO and it can be lost without losing the ATO. Put to WI-26. (4) 'within 90 days' at 0116 has no start date on the page. (5) P. 7 calls the RMF Knowledge Service authoritative and p. 3 a living document, so the 29 May 2024 text may be behind.
- Not in references/: DoD ISCM Strategy, DISA Connection Process Guide, OMB M-21-31, DevSecOps Activities and Tools Guidebook, DoDM 8140.03.

## DODCIO-CATO-IG

- FLAG, I-4: DODCIO-CATO-IG p. 11 is an image too; the list names pp. 7, 12, 17, 18 only. WI-53 should add it.
- FLAG, distribution: the cover (excluded page) says both 'CLEARED For Open Publication Apr 11, 2024' and 'DISTRIBUTION STATEMENT C. Distribution authorized to U.S. Government Agencies and their contractors'. Clearance is later and the PDF is on dodcio.defense.gov, so I left it; INV-7 owners may want to record that.
- FLAG, near cap: cato-team-training is at 24 of 25 with EVAL's 11, and cato-assessment-method at 22. Tell later jobs.
- Source conflicts: (1) Table 2: p. 19 says a threshold 'must be met' (0124), and the next paragraph says the intent is not that all practices 'need to be implemented, such as in a conformance checklist'. Read as: the organization selects (0188), and T rows bind in what it selects. p11 must decide. (2) P. 12: 'the SCSS is not required' (0052), while PP05 at 0164 is T; read as binding where a reference design uses a sidecar. (3) 'must be based on' a reference design (0047) against PP01 at O (0160). (4) 0043's briefing includes 'all conditions of the authorization', and AD-CATO has conditions_required: false. (5) 0024 'The cATO is issued to the software factory' states a holder and AD-CATO has none; WHO approves is decided and not flagged.
- Not in references/: DevSecOps Fundamentals Guidebook: Activities and Tools v2.2, CNCF Kubernetes reference design v2.1, DoD Software Modernization Strategy, DCWF.

## DODCIO-CATO

- Source conflicts: (1) DoD CISO approves here, AD-CATO decided_by: PER-AO, already in ADR-0005. (2) p. 3 cATOs 'do not have an expiration date' and a separate ATO stands beneath, against DODCIO-CATO-EVAL 0028 reverting needs a new workflow, already reported by EVAL. (3) The signer is titled 'DoD Senior Information Security Officer (SISO)' and the body says 'DoD CISO'; read as one role.

## DODCIO-CSRMC-TENETS

- FLAG for p12: WI-52's title says nine, so 0001, the CONMON tenet, is not bound to it and carries its own gap ('real-time visibility', held by S-5 only where AD-CATO is a goal; WI-24 for the dashboard). The heading words 'Control, and ATO' have no sentence. Mapping all ten together is the natural step; I did not extend the title.
- Source conflicts: this page says 'Enterprise & Inheritance', the CSRMC band says 'Enterprise Services & Inheritance'. 0003 'Enhancer ole-based' and 0007 'Integrate Integrate' are in the PDF as printed, confirmed in the image, so I-3's note stands and evidence quotes them so. 0005 'increase adoption proven frameworks' also lacks a word. 0004 and the rest read as sentence fragments; no effect.

## DODCIO-CSRMC

- Source conflicts, for p12: the graphic maps Authorize to NextGen CSSP onboarding and names no AO, and a CSSP watch officer deciding to disconnect, where DoDI 8510.01 gives the decision to the AO. NextGen CSSP, the ISCM Alignment System and the operational ISCM appear in no other library document I read for this job.

## DODCIO-DEVSECOPS

- FLAG, noise over 50%: needs a noise record with `approved_by: user`. It is what the document is: it calls itself 'an educational compendium', and 72 of the 112 are lists: 10 phase definitions, 6 DORA findings, 11 tenets, 27 metric and OKR lines, 8 role sketches, 4 Table 1 rows, 6 fragments. sources.yaml's basis 'should and indicative sentences' overstates it: almost no indicative sentence bound anyone. Live entries are 32 of 154.
- FLAG, extraction: shaded or highlighted paragraphs are read as tables, and the first line is taken for a header and lost. Lost: p. 11 'community of end users. It leverages automation', p. 14 'Software factories may contain ... Each', p. 16 'The CD acronym is often ambiguously used', p. 21 'The Plan Phase involves activities', p. 22 'analysis, requirements updating' and the MVCR head above. Only the last holds a duty, but the 'every raw line lands' test evidently misses table headers, and promote cannot reach them.
- FLAG, I-4 and WI-53: this document has image figures on 14 in-scope pages and is not on the I-4 list. None loses a requirement; WI-53 should add them, Figure 11 in particular.
- FLAG, scope: sources.yaml excludes pp. 1 to 6 as 'Cover, change record and table of contents'. There is no change record, and p. 3 (approval) and p. 4 (Foreword) are unnamed. The Foreword holds no duty. P. 44, the back cover, is in neither list. Glossary p. 41 holds 'should be included in the release control gate', out of scope and left.
- Source conflicts: p. 11 'necessary' against glossary p. 40 'encouraged' for a platform (0025). CD: p. 16 'manual decision to deploy' against p. 24 'in an automated fashion' (0040); CI/CD expands to Delivery on pp. 11 and 18, Deployment in Table 1's label and the glossary. Two captions read Figure 7, and the list of figures has one. P. 22 'should also define' against 5000.87 'will use' (0064). P. 35 one person in several roles, 'to be encouraged', against p. 14 separation of duties (0033, 0140). 0105 'delegate' against the AO's non-delegable decision, read as general advice. P. 27 'SP 800-137.26'. P. 28 JITC against the acronym list's JTIC, 'Joint Integration Test Center'.
- References the entries lean on that the library lacks: DevSecOps Fundamentals Guidebook: Activities & Tools (0058, 0153), DoD DevSecOps Reference Designs (0029, 0153), NIST SP 800-218 (0076), SP 800-204D (0054), DoD Zero Trust Strategy (0070), (CUI) DoD ISCM Strategy (0034). The first two set what 0058 and M-6 mean, so cato-activities-mapping cannot close without them.

## DODD8140.01

- Shares: noise 19/86 = 22%. Retired 46/67 real = 69%, OVER 25%, flag: a directive of OSD offices' charters; needs a retirements record with user approval. Noise and retired together 65/86 = 76%.
- Not in references/: DoD 8140 manual and DoDI 8140.02 (the qualification standards WI-37 tests against), the DCWF, DFARS Subpart 239.71.
- Source conflicts: none internal. Table of contents and cover agree.

## DODI5000.02

- Shares: noise 41/79 = 52%, OVER 50%, flag. Retired 27/38 real = 71%, OVER 25%, flag: an acquisition overview document; needs a retirements record with user approval. Noise and retired together 68/79.
- Not in references/: DoDI 5000.91, 5000.95, 5000.73, DoDD 5000.71, 5135.02, 5137.02, 5105.84; the AAF website; the DAU table at dau.edu/aafdid (0075), the one DODI5000.85 and 5000.81 also lean on.
- Source conflicts: none internal. Figure 1 is dated December 2019 and still shows it as current; Change 2 changed the text, not the figure.

## DODI5000.74

- Expected shares: noise 93/211 = 44%, under 50%. Retired 112/211 = 53% (95% of non-noise), OVER 25%: needs the `retirements` record in conformance/policy.yaml that ADR-0005 allows for 5000.74. FLAG: ADR-0005 covers that excess only 'where that comes solely from the touchpoints decision'. The 30 not-applicable are OSD offices (19), SRRB procedure (9) and workforce items (2): Fable should confirm they fall under the record, since they retire under the OSD and producer-procedure rules.
- Source conflicts: 1.1.b(2) and (3) cite 'Note 4 of Table 1' for the decision authority that ends an exemption, but Note 4 is about business systems aligning with 5000.75; the Table 1 row authorities are what is meant, unconfirmed. 'Paragraph b.(1)' in 4.7.c means 4.7.b.(1). 1.2.a and the references cite DoDI 5000.02T, and 4.8.b the Defense Acquisition Guidebook, as current.
- Library gaps: DoDD 5000.01 (0011), DoDI 5000.02T (0011), DoDI 5000.77 (0007), DoDD 1100.4, DoDI 1100.22, DoDI 7041.04, OMB A-76 (0141), OFPP Letter 11-01 (0018), FAR and DFARS parts cited at 0018, 0025, 0149, DPC memo of June 21, 2016 and the DoD Handbooks (0107, 0142), UARC Management Plan (0007).

## DODI5000.75

- Pages read: 2 to 38 (37, plus p39 references for library gaps). Entries: 252 (lead's 248 plus 4 promoted).
- Source conflicts: 0024 'Cybersecurity strategies mission-critical' drops 'for'. Sections 2.2, 2.3 and 3.2 assume a DoD CMO and MILDEP CMOs, an office Section 901 of the FY2021 NDAA repealed: the role here may be stale, and the library holds nothing later. Not re-checked outside the library. p38 scrambles 'MDA' and 'program manager' across the columns; 0247 is read as the program manager definition's sentence.
- Library gaps: DoDI 8330.01 (0212), DoDI 7041.03 (0116), DoD CMO memo on Defense Business Systems Investment Management (June 26, 2018; 0226), DOT&E memos on CEVA and Information and Business Systems T&E (0095, 0191), DAU Cybersecurity T&E Guidebook (0191), 10 U.S.C. 2222, 40 U.S.C. Subtitle III.

## DODI5000.80

- Shares: noise 25/93 = 27%. Retired 61/68 real = 90%, OVER 25%, flag: an acquisition pathway document, which the ADR's touchpoint decision makes the expected result; needs a retirements record with user approval. Noise and retired together 86/93.
- Not in references/: DAU AAFDID MTA requirements (0078, 0090), DoDI 5000.91, 5000.73, 3110.05, 5025.01, the MTA companion guide.
- Source conflicts: (1) 0052 and 0068 name the Joint Capabilities Integration and Development System, disestablished in DODI5000.02 Change 2 (0019); this issuance is Change 1, November 25, 2024, and predates it. WI-33. (2) Figure 1 shows MTA bars of '2-5 years' while the text says within 5 years with no floor; text governs. (3) 0039 DOT&E approval of a test strategy is deferred pending the p13 TEMP approval ruling in closeout.txt. (4) 0066 cites DoDI 5000.89 for a lifecycle sustainment plan, which 5000.89 does not govern; the document meant is likely 5000.91.

## DODI5000.82

- Library gaps: DoDI 5200.44 (0114, 0116 to 0123, 0162, cited throughout 3.5.c, and 8500.01 slugs lean on it); DFARS 252.204-7012, 7020, 7021, 252.239-7018, 239.76, 239.7306; DoD CC SRG; AAF DID CCA Compliance tables (0063 to 0067); 10 U.S.C. 3252 and the August 20, 2021 DepSecDef memo; DoDI 8310.01, 8320.02, 8330.01; DoDI 8582.01; DoD 5400.11-R; DoDI 4650.01, 4650.08, 4630.09; DoDD 5205.02E; Joint Staff Cyber Survivability Endorsement.
- Source conflicts: 0132 follows 'the Joint Capabilities Integration and Development System requirement' though JCIDS is disestablished (WI-33). 0098 cites DoDI 8580.1, 'Information Assurance (IA) in the Defense Acquisition System', an older title; it is in the issuance's references list and not in the library. Section 3.5.b(5) 0113 and Table 2 say the CSS is approved inside the PPP; 0113 also allows a stand-alone CSS, and DODI5000.75-0024 has the DoD CIO approving; WI-30 must carry both routes.

## DODI5000.83

- cti-safeguarding (4): 0134 0146 0147 0154. P-12 flag, P-17 clauses, M-3 losses.
- Source conflicts: JCIDS at 0082, 0084, 0085 (WI-33). 0251 'these items' has no antecedent, copied from 0238. 0253 'appendix' where 5000.90 says annex; it also says 'Urgent Operation Needs'. 0243, 0244 locators wrong (read 3.4.a, 3.4.b). 0194 widens its subject to S&T managers inside a list addressed to LSEs.

## DODI5000.85

- Touchpoint decision the lead asked for: 0118 and 0126 are live on WI-30. The table rows were NOT read: they are at dau.edu/mdid, not in references/. So I bound the rows by the lead's statement, not from a source. DODI5000.81-0058 stays deferred in its own decisions and now disagrees with this; the lead should reconcile it.
- Library gaps: DAU MDID tables (nine, 3B.1.a, incl. Milestone and Phase Information Requirements, EVM, CCA compliance; 3C.3.c(3)); DAU AAF MOSA page; DAG; DoDI 5015.02, Title 44 Chapter 31 (0214); DoDI 5000.66, 2040.02, 2010.06, 5000.91, DoDD 5000.01, DoDD 5135.02, CJCSM for JCIDS (0203).
- Source conflicts: ICD, CDD and JCIDS at 0046, 0072, 0203 (WI-33). Printed TOC page numbers run one high from Appendix 3A on (Figure 3 listed 29, printed 28). 0179 ends in a garbled 'provide additional discussions of technical management activities'. 5000.85 says 'requirements document' at 0013 with a plural verb, copied as is.
- 28 x_existing entries lean on phases.yaml, milestones.yaml, reviews.yaml; 17 of them carry an x_note marking other clauses as acquisition substance. The brief says never plain x_existing with a note that part is not held, but also that a gap names a slug that would hold it, and no slug should hold LRIP or funding. I applied the rule for another body's procedure by analogy: x_note, no x_gap.

## DODI5000.87

- Source conflicts: 0055 cites 'a new process as discussed in Paragraph 2.8.a', and 2.8.a is only a consultation clause. 0116 offers cATO across the pathway and 0038 applies guidance to both paths, while DoDI 5000.90 p13 excludes software-enabled hardware: the embedded path is WI-34's case. 0025 and 0098 both DOT&E as approver, consistent. 2.8.b 'capability needs statements' against glossary 'capability need statement'. 0103 'embedded pathway'. 0053 'there are ... resources are in-place'. 0066 'will continuously refined'. 0033 'DAs designate ... and supports'. 0088 'PM's will ensure'. 0086 'deliverables markings and assertions'. JCIDS at 0004 and 0055 predates WI-33's disestablishment.
- References the entries lean on that the library lacks: DAU AAF Software Acquisition Pathway Guidance (0013), DoDI 5010.44 (0011 0082), DoDI 5000.73 (0100 0102), DoDD 5000.01 (0002), Section 913 of P.L. 115-91 (0054), Section 800 of P.L. 116-92 (0005), 10 U.S.C. 2430 (0005).
- 0025, 0093, 0098: the test strategy stands for the TEMP at A-2, so WI-30's closure must admit it. Same flag as DODI5000.89: DOT&E approval is live here, x_defer in DODI8500.01.p2.

## DODI5000.88

- Source conflicts and oddities:
- 0023 has DoD Component heads appoint PMs; framework/personas.yaml PER-PM says the CAE, as DoDI 5000.85 does. Not fatal: the column records who did.
- 0118 and 0214 lean on DoDI 5000.02T enclosures; the 5000.88 cover cancels only Enclosure 3. 0056 cites JCIDS (WI-33).
- 0216 prints MIL-STD-822E for 882E. 0016 and 0017 print ACAT 1D. 0033 prints 'b Prepares', so its locator reads 2.5.a. 0083 says 'at least 120 days after contract award' where an outer limit is meant. 0232 calls the CAE 'the lead DoD Component'.
- References leaned on that the library lacks: DoDI 8320.04 (0253), DoD ITRA guidance and Framework for Risk Categorization (itra-input), DoDI 5000.02T, DoD SEP Outline, DoD RIO Guide, MIL-STD-882E.

## DODI5000.89

- Flag for consistency: DOT&E and USD(R&E) approval of the TEMP (0011 0025 0074 0075) is live here under 'content, approval or submission' because A-2 reads the TEMP; DODI8500.01.p2 marked a like DOT&E approval x_defer ('no RMF task waits on'). One rule should win. Non-TEMP documents (0096 0136 0137 0144 0163 0180) follow DODI5000.81-0013 and 0083.
- Source conflicts: 0055 'T&W WIPT'. 0116 parenthesis never closes. 0141 ends in a stray 'Memorandum.' 0075 ACAT IB and IC, 0213 1B/1C. 0135 'upon coordination with the DOT&E, the DOT&E approves'. 0218 'policies ... applies'. 0182 'vulnerability analysis', 0118 'threat analysis'. 0158 DAE as MDA with P.L. 115-91 s.838, 0214 USD(A&S) as MDA with 10 USC 2366b. JCIDS at 0056, 0113 (WI-33). DoDI 5000.02T cited as live at 0133, 0232.
- References the entries lean on that the library lacks: DoD Cybersecurity T&E Guidebook (0112 0113 0176); DOT&E Memoranda of April 3 2018, January 21 2015, September 14 2010 (0118 0141 0182 0186); DoDI 8330.01; DoDI 4650.08 and DoDD 4650.05; DoDD 5141.02.
- Brief unclear: whether approval of a document a run reads stays live when the entry criterion does not test approval (flag above). 'Mixed x_existing' sits between the partly-held rule and the another-body rule when the other clause binds a run persona (0212 PM). Brief otherwise held.

## DODI5000.90

- Shares: noise 61/156 = 39%, under 50%. Retired 21/156 = 13.5% (21/95 = 22% of non-noise), under 25%, nothing to flag.
- Source conflicts: 0080 says 'In accordance with DoDI 8510.01' for the 3-year limit, and the 8510.01 text holds no such limit (WI-25 already says so). 0086 says the ATO 'certifies' effectiveness; 8510.01 and SP 800-37 never use that for an ATO. 0117 'see Table 2' means Table 1. Page 18 captions the Table 2 continuation 'Table 3'. 0019 cites 'DoDI 5000.UH', in no reference list; my inference that it is 5000.82 is unconfirmed. 5000.90 calls the strategy an annex; a sibling decision records another document calling it an appendix. Text typo 'CYBERSECURTIY' at 3.1.
- Library gaps: DoDI 5000.02T, 5200.44, 5200.39, 5205.13, 5205.02E; 10 U.S.C. 2223, 2339a (now 3252, from memory); NDAA FY13 s.933, FY14 s.937; FAR and DFARS clauses; CMMC; USD(R&E) Critical Technology List; April 3, 2018 DOT&E memo; T&E Guidebook. 5200.44 matters most: 0122 and 0127 lean on it, and WI-31 cannot close on its content without it.

## DODI5400.11

- Source conflicts: 0093 makes OSD Component SCOPs advisory, yet 3.1.b(1) and (4) have SCOPs approve; the PER-PRIV card holds approval. 5400.16 names the DCMO where this names the CMO and DO&C. Not resolved.
- Library lacks: DoD 5400.11-R, DoD Breach Preparedness and Response Plan, OMB A-130, A-108, A-19, M-16-24, M-17-09, M-17-12, DoDI 1000.30, DoDD 5205.16, DoDM 5240.01, DoDM 6025.18, 32 CFR 310, Privacy Act, E-Government Act section 208.

## DODI8500.01.p1

- Source conflicts: 0219 says six RMF steps, the framework has seven with Prepare (SP 800-37r2). 0192 cites SP 800-30 as Reference (bx); Enclosure 1 has (bx) as the Unified Command Plan, (by) as SP 800-30. 0138 cites Section 2222 of Reference (aa), Title 44; section 2222 looks like Title 10. Typos: 0022 'beach', 0180 'CHNSS'.
- Shares (FLAG): noise 70 of 296, 24%, under 50%. Retired 92 of 226 real entries (85 not-applicable, 7 x_defer), 41% on this part; 93 if 0140 goes not-applicable. Part 2 has 150 entries, so the document stays over 25% unless nearly all of part 2 is real and none retired: expect a user-approved retirements record. Most of it is Enclosure 2 sections 1 to 12 and 14 to 15, offices above a run.

## DODI8500.01.p2

- Source conflicts: 0331 cites Section 811 as Reference (dd); Enclosure 1 has (da), and (dd) is SP 800-88 (right at 0336). 0344 cites DoDI 5000.64 as (de); Enclosure 1 has (df), and (de) is DoDAF. Section numbering: sections 12 to 21 are roles inside 'Enclosure 3: Procedures', after the DoD Component heads of Enclosure 2.
- Shares (FLAG): this part noise 18 of 150, 12%; retired 28 of 132 real, 21% (26 not-applicable, 2 x_defer). Document with part 1: noise 88 of 446, 20%, under 50%; retired 120 of 358, 34%, over 25%, so a user-approved retirements record is needed; 121 if 0140 goes not-applicable.

## DODI8510.01.p1

- Source conflicts: Table 8 'UR | ISO' (0306) against 0236 (SO appoints) and 0063 (information SOs); the acronym list on p. 32 gives ISO as information security officer. 0087 says the Prepare step is done by the Component CIO, PAO and JCA CPM, while Tables 1 name the Head of Agency, SAORM, SO and others, and Table 1 titled 'Organization' holds system tasks P-8 to P-18. 0074 (USSPACECOM assigns AOs) against Table 8 (Component head or PAO). 0235 and 0069 lean on JCIDS, now disestablished (WI-33). Typos: 0027, 0030 'National Security Service'; 0060 'maintain authorized DoD systems are maintained'; 0121 'Assessment are reviewed'; 0123 repeats its bullet.
- Shares: noise 59 of 294, 20%. Retired 40 (39 not-applicable, 1 x_defer), 17% of 235 real entries, 14% of 294. No flag: under 25% and under 50%, and part 2 has only 11 entries. The not-applicable set is DoD-level staff work: DoD CISO, DISA, USD(A&S), USD(R&E), NSA, RMF TAG, JCA CPM, and RMF TAG participation at each level.

## DODI8510.01.p2

- Shares, document total 305: noise 68 = 22%; retired 41 (40 not-applicable, 1 x_defer) = 13% of entries, 17% of 237 real. No flag.
- Source conflicts: none. Unread reference behind a live entry: the RMF KS, behind a CAC, as part 1.

## DODI8530.01.p1

- FLAG: over 25% retired, and over half with noise, so FW-REQ-004 needs a retirements record approved by the user. The cause is real: Enclosure 2 is 168 entries (0041 to 0208), most of them duties on OSD, agencies and commands with no run touchpoint. Noise is under 50%.
- Source conflicts: 0186 calls CJCSI 6510.01F Reference (bo), Enclosure 1 lists it as (bp). Figure 1 cites Reference (q) for CSSP services, body cites (p). Reference (p) is DoD O-8530.1-M, not in the library. Stale by date, as written: USSTRATCOM's cyber role, DSS, USD(AT&L), JCIDS (see WI-33).

## DODI8530.01.p2

- Source conflicts: reference letters. Enclosure 4 body gives FAR 4.4 as (cj), 8582.01 as (ck), DFARS as (cl), 5220.22-R as (ci), where Enclosure 1 has (ci), (cj), (ck), (ch). So 'Reference (ch)' in 0296 and 0300 reads as the Industrial Security Regulation by the list and as the DISN Connection Process Guide by the body's shift; I took the Guide, as 0289 names it, and it is cited as (cg) on p37. 0303's '(ci)' has the same doubt. Reference (bv) is SP 800-37 Rev. 1; Reference (p) is not in the library. USSTRATCOM stale, as part 1.

## DODI8531.01

- FLAG: over 25% retired and over half with noise, so FW-REQ-004 needs a retirements record approved by the user. The cause is real: Section 2 is 109 of the entries and most are VEP and VDP staffing and oversight by OSD, NSA, DC3, CJCS and USCYBERCOM. Noise is under 50%.
- Source conflicts:
- Severity scales: CVSS None to Critical, with 'catastrophic' at High and 'cataclysmic' at Critical, against FIPS 199 and the SP 800-30 `level` enum in sar-results and poam-items. A record must carry both.
- 3.6.d 'monthly' scans of 'previously affected systems' against CNSSI 1253 RA-5 'at least every 30 days'.
- 3.4.b(2)(a)-(d) say 'minimum CVSS score of 0.1 and 3.9'; Table 1 shows ranges. Read as ranges.
- Figure 1 says 'Remediation or Mitigation', the text 'Remediation and Mitigation'. No effect.

## DOWI8430.01

- FLAG, retired share: 82 of 199 real entries, 41%, over the 25% limit. It needs a `retirements` record with `approved_by: user`. Noise 73 of 272 = 27%, under 50%.
- Source conflicts: (1) 0185 reads evidence from all software through the 'Assess Only Construct', which the framework holds only as a note (WI-28). (2) 0244: 'SaaS offerings must meet FedRAMP' with no DoD PA, while 0021 has DISA issuing PAs; cloud-cso holds both. (3) 0188's timeframe and 0143's formats are on a Knowledge Service page, not stated. (4) 2.7.d to f and 2.8.h to j repeat the same words on two subjects, both kept.
- Not in references/: DoDIs 5200.44, 5200.48, 5000.76, 5000.95, 5000.97, 5000.98, 5015.02, 8115.02, 8140.02, 8310.01, 8582.01; DoDMs 5000.96, 5000.103, 8140.03, 8180.01; DoDDs 8115.01, 5205.02E; DoWI 8000.02; DoD AI Cybersecurity Tailoring Guide; CSP SRG; Activities and Tools Guidebook; January 28, 2021 memo; EOs 14028, 14144, 14306; Public Law 118-187; Joint SAP Implementation Guide.

## DTM-24-001

- Source conflicts: (1) 0193 'A DoW or commercial entity must perform DODIN UAM' against Table 1 row 0058, IL 6 DoW only. (2) Table 1 Intrusion Assessment is DoW or commercial, but 0249 lists intrusion assessments under Incident Response Analysis, CSSP only. (3) 0192's last sentence moves IaaS and PaaS enclave monitoring to a capable CSSP against the circle on row 0057. (4) 0239 and 0241 put the same LE notice on both the CSSP and the mission owner.
- Library gaps the entries lean on: DoD Cloud Computing SRG, DoDM 8530.01, DoDI 8530.03, CJCSM 6510.01, CNSSP 32, NSD 42, EO 14028, NSM-08, DoDI 8330.01, DoDI 5205.16, DoDI 5200.48, DoDI 8582.01, DoDD 5106.01, DFARS 204.73, USCYBERCOM 5200-13, JFHQ-DODIN OPORD 17-0217.

## FIPS199

- Shares: noise 20 of 32 = 62%. FLAG: over 50%. Foreword and FISMA background 8, level definitions 3, Examples 4 and 5 and footnote 5 5, Table 1 4: the standard is short and most of it is definition and example. Needs a noise record with approved_by user; policy.yaml has none for FIPS199 (rules.py: 20 over max(10, 16)). Retired 0.
- Source conflicts: FIPS 199 leaves out national security systems (0008) and DoDI 8510.01 categorizes every DoD system under CNSSI 1253; the forms match, so x_existing rests on C-2. CNSSI 1253 0046 keeps three levels for the system value, consistent with 0019 and 0020; WI-13's enum change must go to infotypes.schema.json only, not facts.schema.json.

## FIPS200

- Source conflicts
- High water mark, real for one class of fork. 0015 and 0035 want one overall level and one of three baselines. FIPS 200 excludes NSS (0004), and CNSSI 1253 Section 1.2 drops the concept for NSS, so a NSS has no conflict. DoDI 8510.01 page 8 puts every DoD system on CNSSI 1253, including a non-NSS one, which FIPS 200 still binds. On a non-NSS M-L-L system the per-objective union can fall below the moderate baseline (cp-6 is .XX on A only), and baseline.py refuses high-water-mark unless CNSSI 1253 is degraded, so that fork cannot follow FIPS 200 literally. Kept as x_existing, as REQ-SP800-53B-0026 was, because the DoD instruction governs a run; this is the one call in this job the user may want to see.
- Catalog and PDF differ: the pin for SP800-53R5 is the PDF of 12-10-2020, the OSCAL catalog is Rev 5.2.0. 0040 asks for the most current version; recorded on that entry.

## SP800-128.p1

- Shares: part 1 noise 155/303 = 51%, over 50%, flag: a guideline of definitions, lists and sample forms; needs a `noise` record unless part 2 pulls it down. Retired 2/148 = 1%, nowhere near 25%.
- Source conflicts: 0003, p15, says the guidelines exclude national security systems and may be used for them 'with the approval of appropriate federal officials', while the framework cites SP 800-128 for NSS runs and no step records that approval. 0211 says impacts go 'to the CCB and to the AO'; 2.4 and ART-CMP send only what the criteria select. Decided as held, noted.

## SP800-128.p2

- Shares, whole document with part 1: noise 229/392 = 58%, OVER 50%, flag: needs a `noise` record. Retired 2/163 = 1%. Part 2 alone: noise 74/89 = 83%.
- Source conflicts: none in these pages. Table 6's note misnames itself 'Table 5' (0360), a typo in the source.

## SP800-137

- Source conflicts: the document cites SP 800-37r1 and 800-53r3, and 0159's AC-2 lettering is the old one; A-130 Appendix III (0013) is its 2011 state. 0084 calls the guidelines 'not prescriptive' while 0200 says 'must'. Page 35 puts frequencies in the SAP; the framework puts them in ART-CONMON, which I counted as held because it is in the package. P-7 RACI makes only PER-RE responsible while 0209 names four primaries; SP 800-37r2 follows the RACI, so x_existing.
- Library gap: SP 800-55 (metrics, cited at 0035, 0141, footnote 43), NISTIR 7756 (architecture example, p36), SP 800-92 and OMB M-11-33: none is in references/index.yaml or sources.yaml. The metrics entries under WI-15 lean on 800-55.

## SP800-137A.p1

- FLAGS, both exceed whatever part 2 decides:
- Noise: part 1 217/307 = 71%. Document at least 217/357 = 61%, over 50%: needs a `noise` record. Cause is real: front matter, audience, attribute names, example tables and rules, scoring NIST calls optional.
- Retired: part 1 47/90 = 52%. Document at least 47/140 = 34%, over 25%: needs a `retirements` record approved by the user.
- The 47 are the mechanics of the assessment engagement (judging, combining, plan, kick-off, team preparation, evidence gathering). I retired them because a run needs only the result: section 3.1 says the decision 'may impact authorization decisions'. If the user wants the assessment modelled, these 47 become a new optional task and artifact instead. That is a decision for the user.
- Source conflicts: 0201 says Figure 7 shows the overall process; Figure 4 does, 7 is the Report crop. p32 says elements are 'not tailored out' while 0087 and 0095 allow limited scope and tailoring.
- Library gap: the [Catalog] spreadsheet (128 elements, 'the minimum set', 0095) is not in the library. Only seven elements appear in text (0088-0094) and seven in Figure 2. I kept 0088-0094 real although the page calls them examples; a strict reading of the brief would make them noise.

## SP800-137A.p2

- FLAGS:
- REQ-SP800-137A-0329 (p24, status candidate) is in neither decisions file: page 24 belongs to part 1, which skipped it, and it is outside my range, so I did not decide it. Part 1 keys jump 0328 to 0330. Statement reads as a note on how catalog elements were written, likely noise, but page 24 needs reading. The register's 96 candidates are 43 live from part 1, 52 from this job, and 0329.
- Noise: part 2 42/52 = 81%; document 259/359 decided = 72%, over 50%, needs a `noise` record.
- Retired: part 2 8/10 = 80%; document 55/100 = 55%, over 25%, needs a `retirements` record with `approved_by: user`. Part 1's 34% estimate assumed all of part 2 live; it is not. Shares are as `rules.retired_share` counts them, taking 0329 as noise for the denominator.
- Source conflicts: 0289 says 'all three assessment methods' while page 53 and Table 5 name only Examine and Interview. 0324 'elements are tailored out of the catalog' repeats the conflict part 1 found with p32's 'not tailored out'.

## SP800-137A.p3

- FLAG: 0329 was not missed. It is `removed: true`, a retired ID, and its words stand as a `no-marker` rejection on p24, which part 1 read. `rmf conformance page` does not list it. `register.mark` raises 'no live entry' on a removed ID, so a `status` key would stop apply_decisions.py on that file; the decisions file holds x_ keys only, applying 0 of 1. Nothing to do. Part 2's report called it status candidate; every removed entry shows `candidate`, and there are 160 across the register, so a check for candidates should skip `removed`.

## SP800-160V1R1.p1

- Flags:
- Noise 82.2% of this part, over the 50% line. Expected: these are foreword, concepts and definitions. The document total depends on parts 2 to 5.
- Retired 8.4% here (deferred 25, no not-applicable), but the process appendices will defer heavily. The document will likely pass 25% retired and need a user-approved `retirements` record in conformance/policy.yaml.
- Sentences with 'should' as 'if' (0144, 0162, 0184) carry the word in the reason as the check requires.
- Source conflicts:
- 0015: the document excludes national security systems unless federal officials with policy authority approve use. A DoD fork should read every live entry with that condition. I found no such approval; lead to decide if the document needs a note in sources.yaml.
- 0157 and 0162 set likelihood aside, while ART-RA keeps it under SP 800-30. Marked noise, with that said.
- References leaned on, not in the library: OMB policy [8] (2018, Strengthening the Cybersecurity of Federal Agencies; 0016, HVA); [30] and [31], ISO/IEC standards (assurance cases; 1389), and INCOSE guide [32].

## SP800-160V1R1.p2

- Flags:
- Noise 234/291 = 80.4% of this part, over 50%. Document so far, p1 plus p2: 478/588 = 81%. FLAG: needs a `noise` record. Expected: Appendix E is advisory, and p1 was concepts.
- Retired 52/57 = 91% of this part. Document so far: 77/110 = 70%, over 25%. FLAG: needs a user-approved `retirements` record in conformance/policy.yaml. Parts covering Appendices H to K will add to it.
- Source conflicts:
- Page 98 says principles are not rules; sa-8 and its enhancements make them controls in the NSS baseline, and 0467 says composition 'must include' two principles. Followed page 98 for this document; sa-8 stands on its own source.
- 0015 from part 1 applies to the live entries here too: the document excludes NSS unless approved.
- References leaned on, not in the library: [4] ISO/IEC/IEEE 15288, behind Appendices G to K; [30] on assurance cases (0486, 0488 to 0491); [2] and [37], quoted at 0465 and 0313. No live entry rests on one.

## SP800-160V1R1.p3

- Flags:
- Retired 167/263 = 63.5% of this part, over 25%. Document so far, p1 to p3: 244/373 = 65.4%. FLAG: needs a user-approved `retirements` record in conformance/policy.yaml.
- Noise 32/295 = 10.8% here. Document so far: 510/883 = 57.8%, over 50%. FLAG: needs a `noise` record, driven by parts 1 and 2.
- Source conflicts: 0015 from part 1 applies here too, the document excludes NSS unless approved. SN-2.4 and SN-4.1 are word for word the same task. AR-2.7 and AR-2.9 differ by one word. 'EVALUTE' is a typo in the DE-3 heading on p143.
- Scope defect: none new. References leaned on, not in the library: [4] ISO/IEC/IEEE 15288, behind every process here; [30] and [31], ISO/IEC standards, on SN and SR. No live entry needs their text.

## SP800-160V1R1.p4

- Flags:
- Retired 134/230 = 58.3% of this part, over 25%. Document, all five parts: deferred 534 of 775 non-noise = 68.9%. FLAG: needs a user-approved `retirements` record in conformance/policy.yaml.
- Noise 66/296 = 22.3% here. Document: 620/1395 = 44.4%, under 50%; part 3's expected `noise` record is no longer needed on these figures.
- Source conflicts: 0015 from part 1 applies here too, the document excludes NSS unless approved. 'Casual events' at RM-1.1 reads as 'causal'; 'being meet' at PA-2.7's note. No effect on a decision.
- Scope defect: none new. References leaned on, not in the library: [4] ISO/IEC/IEEE 15288, behind every process here. No live entry needs its text.

## SP800-160V1R1.p5

- Flags:
- Retired 156/172 = 90.7% of this part, over 25%. Document, all five parts: 534/775 = 68.9%. FLAG: needs a user-approved `retirements` record in conformance/policy.yaml.
- Noise 44/216 = 20.4% here. Document: 620/1395 = 44.4%, under 50%.
- Source conflicts: 0015 from part 1 applies here too. MS-2.1 with MS-2.2, and MS-2.3 with MS-2.4, differ by a word; 1239 and 1241 near identical. 1167 is held and 1168 deferred on that one word, 'security-relevant' data against data in general.
- Scope defect: none new. References leaned on, not in the library: [4] ISO/IEC/IEEE 15288, behind every process here. No live entry needs its text.

## SP800-161R1.p1

- Flag: cscrm-governance is at 23 of 25 and later parts will add; split it into roles and council or PMO if so. WI-04 has 31 here: it is an existing item, and its plan, strategy and supplier content may want splitting at p11.
- Source conflict: 0277 runs supplier risk assessment after the impact level, while the framework has P-14 before C-2 (C-2 takes ART-RA). The home must settle it; recorded in x_note.

## SP800-161R1.p2

- FLAG: noise exceeds NOISE_DOC_SHARE (50%) in this part and across parts 1 and 2, so the document will need a reviewed `noise` record in policy.yaml unless parts 3 to 5 pull it under: their 838 entries would have to run at 39% noise or less. Cause is the source: 177 noise entries are Appendix C's example framework, sample form and six fictional scenarios, and 44 are Appendix D's Sample Text, sample tables and gerund items.
- Source conflicts: 0344 says 'Enabling' where Section 3.4 says 'Enhancing'. Section 2's 'Appendix C provides example templates' means Appendix D; the source's letters are stale there and in many Appendix A cross-references. Scenario tables disagree with their prose on control tags and costs (Table 9 SA-9 against SA-11, Table 12 $100,000 against $80,000 plus $60,000); no effect, all noise.

## SP800-161R1.p3

- FLAG: noise exceeds NOISE_DOC_SHARE (50%). To reach 50% across the document, parts 4 and 5 would have to run at 13% noise (72 of 549), which their appendix text will not, so plan on a reviewed `noise` record in policy.yaml. Cause is the source: 101 entries are the Table 26 questionnaire, and nearly all the rest are Sample Text.
- Source conflicts: 0614 reads 'the C-SCRM policies the C-SCRM roles and responsibilities within the enterprise define', out of order in the PDF too. 0723 says 'system security plan' under the C-SCRM Plan Approval heading. D.3.1.4 has 'Sample Text' above an instruction. 0847 High repeats Critical's 'imminent'. 0852 says 'threat levels' in the vulnerability section. Page 232 has 'C-SCRAC-SCRA'. Footnote 45's 'Appendix D's Assess section' means Appendix C. 0676 sets scope by FIPS 199 levels and a DoD run has CNSSI 1253 values; the home must map them.

## SP800-161R1.p4

- FLAG: noise exceeds NOISE_DOC_SHARE (50%) here and across the document, so the reviewed `noise` record in policy.yaml that part 3 foresaw stands. Causes here: Figs. 14 and 15 (52), Tables 31 to 36 (27), Sample Text. Nothing near 25% retired.
- Source conflicts: 1034 and 1035 say 'SP 809-37'. 1050 says Figure 12 for the Frame figure, which is Fig. 15. 0941 cites a 'Table E-2' that does not exist. Table 31 and rejected p271 text use stale appendix letters (Appendix B for C, G for C). 0951 'longer 90 days'. 1152 'One the primary methods'. 0930 has a stray closing quote. Footnote 54 ends 'kk'. 1079 uses FIPS 199 levels; a DoD run has CNSSI 1253 values.

## SP800-161R1.p5

- FLAG: noise exceeds 50% across the document, as parts 3 and 4 said, so the reviewed `noise` record in policy.yaml stands. Causes here: Figs. 18 to 20 (86), Tables 37 to 39 and Fig. 17, example and option lists. Nothing near 25% retired.
- Source conflicts: Fig. 19 has Levels 1 and 2 'Document C-SCRM controls in POA&Ms', while 1305 and 1308 say a Risk Response Framework. 1263 says those frameworks exist at all three levels, while Table 39 and 1306 give Level 3 the plan. Stale pointers: 1219 'Fig. 17'; 1233 'Fig. D-4'; 1395 'Table D-6'; 1329 'Appendix C' for the plan template, which is Appendix D; footnotes 66, 71, 75 'Appendix C' for the process, which is here in Appendix G; footnote 72 'Appendix B', where the term does not occur. Typos: 1175 'manifest different', 1324 'guide the develop', Fig. 17 'C-SRCM'. 1221, 1260 and 1324 use FIPS 199 levels; a DoD run has CNSSI 1253 values.

## SP800-18R1

- Source conflicts: (1) R1 says at least every three years for reauthorization (0001) and annual plan review (0157); R2 dropped both figures. The three years lives through DoDI 5000.90; the annual figure has no later source, so plan-review-records should take an organization-defined schedule. (2) 0093 condition (i) limits compensating controls to the catalog; SP800-53B 0076 allows other sources; later text governs. (3) 0012, 0174, 0199 use major application, GSS and minor application, deprecated by R2 p27; none may set a value for system-type. (4) 0049 interim authorization to operate is gone from R2 and DoDI 8510.01; held as AD-ATOC, not AD-IATT. (5) 0134 to 0136 name single SP 800-53 baselines; a run selects per objective from CNSSI 1253. (6) 0070 puts risk acceptance on the owner; in DoD it is the AO's.
- References leaned on that the library lacks: SP 800-47 (0125), SP 800-70 (footnote 16, rejected), OMB A-11 (0105), the Privacy Act of 1974 (0132).

## SP800-18R2.p1

- Source conflicts: (1) p27 says 'general support system', 'major application' and 'minor application' are deprecated following A-130; DoDI 8500.01 and the system-type slug still use major application. DoD governs; system-type must not cite this document for that value. (2) 0240 requires a DIAS in the package for federal systems; DoDI 8510.01 never mentions one and SP 800-63-4 is not in the library, so p11 must decide how it applies to an NSS. (3) 0428 selects from SP 800-53B; a run selects from CNSSI 1253.
- Shares: this part retired 0.3%, noise 48.2%, together 48.5%. FLAG: the document passes 50% noise only if part 2 runs above about 54% noise. Section 3.3 is the cause: nearly every sentence is 'can' or 'may'.

## SP800-18R2.p2

- Source conflicts: (1) Table 2's column says SP 800-37r2, but rows P-15, P-17 and S-4 add C-SCRM and M-2 adds 'updated supplier assessments', none in 37r2; p11 should treat these as 18r2's reading, not 37r2's. (2) 0305 and 0311 speak of FIPS 199 and SP 800-53B; a run uses CNSSI 1253. (3) 0335 makes the C-SCRM plan 'not required but recommended' in the package; 0307 says it is generally developed for high and moderate systems. WI-04 needs both as conditions.
- References leaned on that the library lacks: SP 800-47 (0350), SP 800-88 (0310, 0359), OMB A-130 (0319), SP 800-63-4 (0398, as part 1), NARA records guidance (0358), Zero Trust Data Security Guide (0310).
- Shares: this part retired 0%, noise 66.9%. Document: retired 1 of 437 (0.2%), noise 235 of 437 (53.8%). FLAG: over the 50% noise line. Without Table 2's 53 rows it is 182 of 384 (47.4%). The crosswalk is the cause, as is section 3.3 from part 1. Scoping pages 59 to 63 out with the reason 'crosswalk of SP 800-37r2 outputs' would bring it under; that is the lead's call.

## SP800-30R1

- Source conflicts: (1) Chapter 3 tasks are imperative, but p31 says 'there are no specific requirements' on rigor, method or format, fn 43 says other procedures may be used, and fn 57 calls Appendix K 'informative and exemplary only'. I kept tasks and Appendix K items live because ART-RA names SP 800-30 as its method; evidence may want to test intent, not form. (2) 0006 says the guidelines exclude NSS unless approved by officials with policy authority; the framework cites SP 800-30 for every run, including NSS forks. (3) Appendix K cites Table F-1 and F-2 for adversarial and non-adversarial risks (0274, 0275); the risk tables are I-5 and I-7. (4) R-2 hard-codes Table I-2, which the source calls exemplary; no conflict for a run, but tailoring of scales has no home other than ra-risk-model.
- References leaned on and missing: none. Footnotes name SP 800-64, 800-65, 800-117, 800-126 and DHS FCD 2, and no live entry depends on them.

## SP800-34R1.p1

- Expected shares, part 1: noise 174/299 = 58%, over 50%, needs a `noise` record unless part 2 pulls it down. Retired 10/125 = 8%. FLAG noise.
- FLAG, S-4 step 5 contradicts the template: it says ART-CP is a 'minimal stub' with one '## Plan summary', its Outputs table says 'skeleton stub', and the example's ART-CP has only that section. Every x_existing on an ART-CP heading rests on templates/artifacts/ART-CP.md, which no step tells a run to fill. Those 53 entries are held only once S-4 step 5 moves to the template (WI-16's headings rule alone will not do it).
- FLAG, scope defects in conformance/sources.yaml, SP800-34R1: (a) 'Appendix F restates the SP 800-53 CP controls' is false: that is Appendix E (p131 to 138); Appendix F (p139 to 142) is contingency planning in the SDLC, unread. (b) [83, 131] says 'Appendices A to E are sample ... templates', but C is FAQ (p123), D personnel considerations (p127, cited by 0229) and E controls. (c) scope note 'chapters 1 to 5' for [13, 82] is wrong: Appendix A starts p73, so part 2 holds sample template text with {system name}, which the brief calls instruction text or Sample Text.
- Source conflicts: p27 puts the BIA 'before the systems are categorized', p29 and p30 make the FIPS 199 availability category 'a basis of the BIA'. p20 uses the FIPS 199 high-water mark, a run uses CNSSI 1253 per objective (0035, noise). p28 develops ISCPs in Initiation, p34 integrates strategy in Development/Acquisition, S-4 is PH-TMRR. The guide is on SP 800-53 Rev. 3: CP-7(5) and CP-10(3) are withdrawn in the run's catalog, and footnotes 27 and 28 cite an Appendix I that Rev. 5 lacks. Broken cross-references on p18, p25, p34, p37, in the source.

## SP800-34R1.p2

- Expected shares: part 2 noise 78/151 = 52%, retired 7/73 = 10%. Document: noise (174+78)/450 = 56%, FLAG, over 50%, needs a `noise` record. Retired 17/198 = 9%.
- FLAG: every x_existing on an ART-CP heading here carries x_gap to cp-full-plan, 0 without. Part 1's 53 ART-CP claims have no such gap; adding them takes cp-full-plan to about 65, past the 25 cap, though it is one fix to one step. Yours to rule.
- FLAG, scope defects in conformance/sources.yaml, SP800-34R1, adding to p1's three: (d) [13, 82] stops inside A.1: the A.1 suggested appendices are p83 to p86, with 'are recommended' and instruction text ('Provide contact information'), excluded as 'sample ... templates'. (e) A.2 (p87) and A.3 (p103) are excluded while A.1 is scoped, so the brief's 'instruction text is live' applies to the low template only; A.2's Plan Approval repeats A.1's, and I did not read the rest. The exclusion's 'ART-CP's required content is work item WI-16' is not enough, because S-4 step 5 overrides the template.
- Source conflicts: 0351 and 0352 trigger on FIPS 199 moderate or high, a run's ia-2.1, ia-2.2, ac-18.1 apply at every level, stricter. 0353's four e-authentication levels are SP 800-63 of that date. Table 5-1 lists load balancing though no paragraph asks for it. p61 foot sentence is cut in the source. COOP sentence in 0347 is class-bound, noted, retired class as p1's 0132.
- References leaned on, not in the library: SP 800-63 (0353), SP 800-111 (footnote 39), SP 800-97 (footnote 41), OMB M-04-04 (footnote 42).

## SP800-37R2.p1

- Source conflicts:
- 0207 'requires organizations to first apply the high-water mark' against fn 62 (0211). P-6 entry_criteria carries the FIPS wording unqualified for NSS.
- 0729 fn 43 and the C-2 expected output say one high-water mark; 0279 and CNSSI 1253 give one value per objective. The repo follows CNSSI 1253.
- fn 66 hangs on a Supporting Role line but speaks of a primary role.
- Shares: retired 0%. Noise 56% of this part. FLAG: over 50% here, from Chapters 1 and 2, the Figure 3 sample and the tips box. The document stays under 50% only if parts 2 and 3 run below about 45% noise, so a noise record may be needed.

## SP800-37R2.p2

- Source conflicts: (1) 0422 makes registry tracking 'at the organization's discretion'; the R-5 pin expects the registry annotation. (2) 0422 limits reporting to authority delegated below the head of agency; Task R-5 is unconditional. (3) 0350, 0357, 0479 make the SAOP the privacy assessor; the A-3 pin has Control Assessor primary, SAOP supporting. (4) 0377 says no POA&M entry for accepted deficiencies; the repo is stricter, as DoD requires (SAR-POAM-001). (5) Task M-4 is 'AUTHORIZATION PACKAGE UPDATES' in the source, 'Authorization Updates' in framework/tasks/M.yaml.
- Shares: this part retired 6%, noise 22%. Document so far (603 of about 723): retired 3%, noise 39%. Part 1's 50% noise flag clears: part 3 cannot lift noise to half. Noise plus retired reaches half only if over 90% of part 3 is either. No flag.

## SP800-37R2.p3

- Source conflicts: (1) 0629 puts reauthorization at the AO's discretion; AD-ATO's three-year update (DoDI 5000.90) is stricter, and the framework follows DoD. (2) 0589 gives an ATU no termination date; AD-ATO has atd_required true, so WI-01 needs a decision type of its own, not an ATO variant. (3) 0621, 0632 make the SAOP the privacy assessor, against the A-3 pin (part 2 conflict 3 again). (4) 0659's facility authorization issues a common control authorization, and 0658's type authorization ends in an ATU, so WI-10 depends on WI-01. PDF typos on page 164, noted on 0589: 'even-driven', 'to notifies'.
- Shares: this part retired 1%, noise 44%. Document, all three parts, 727 live entries: retired 2.8%, noise 39.8%, together 42.5%. No limit exceeded, no flag.

## SP800-39

- Source conflicts:
- 0149 says residual risk is within the organizational tolerance, 'not the individual risk tolerances of those authorizing officials'; 0175 says acceptable residual risk rests on organizational tolerance 'and the specific risk tolerances of particular decision makers'. R-2 follows 0149.
- 0002 scopes out NSS unless federal officials approve, yet framework tasks cite the publication for a CNSSI 1253 run.
- 0308 cites SP 800-53 Appendix E, absent from the pinned Rev. 5; the statement is cited as read.
- 0172 says self-initiated risk transfer is generally not possible in the public sector, while R-3's purpose and rar.yaml offer transfer plainly.
- Framework defect found: R-3 and M-3 do not list ART-ORG-CONTEXT though 0167 makes the strategy an input (held under risk-response-strategy).

## SP800-53AR5.p1

- Shares: retired 7 of 129 real entries here, about 5%. Noise FLAG: 173 of 337 live entries in the document, 51%, over the 50% line before part 2 adds to either side. Over half of the noise is Figures 1 to 6 (58 rows) and Appendix C definitions and labels (34). It needs a noise record with approved_by user unless part 2 brings the share under.
- Source conflicts, repo against source:
  - assessment-batching step 5 says `satisfied` needs evidence for every objective; 0328 says assessors disregard a non-applicable requirement and still find satisfied.
  - A-2 step 4 says do not list methods by hand; 0181, 0187 and 0337 make the selection and its rationale the quality of the assessment.
  - SAR-COV-001 asks a determination of every scoped control; 0188 and 0194 say common controls are not reassessed at system level, only the inheritance is verified.
  - 0219 reassesses before the final report; A-5 runs after A-4 and adds an addendum. I took it as held, as 37r2 A-5 describes it.
  - Inside the source: p28 prose names CA-03(01)_ODP[01] where Figure 5 shows CA-03_ODP[01]. No effect.
- Partly held, kept x_existing with the gap in x_note: 0205 (clause on unexpected events has no field). Every 'security and privacy' entry with x_existing is held for security only; the privacy half rests on WI-02 and WI-03, stated in the file header and on entries that name a privacy plan or report.
- Brief, wrong or unclear:
  - The job count of 297 leaves out removed entry 0120; the brief does not say whether a removed entry takes a key. I gave it none.
  - A permission ('organizations may') fits no disposition. Where it names an actor and an act no run performs (0040, 0044, 0046, 0227) I used not-applicable; where it only describes, noise.
  - Summary tables and figures restate prose. I kept Outcomes rows live (0134, 0167, 0210, 0224), as a table of outcomes states what a step yields, and made Figure 8 noise, with the live IDs named. The brief does not settle this; a reviewer could rule either way.
  - Reads and timing paths: brief says reads/<REF>.txt, and two parts share a REF, so I used the job name.

## SP800-53AR5.p2

- Source conflicts: none. Text on p732 has 'compromised of' for 'comprised of'; no effect.

## SP800-53B

- Source conflicts
- High water mark: SP 800-53B 2.2 (0026, 0029) against CNSSI 1253 Section 1.2, which does not adopt it for NSS. CNSSI governs a run; the entries are held by the degraded fallback.
- Compensating controls: 0073 speaks of controls 'tailored out ... by necessity'; CNSSI 1253 Section 2.6 says controls may not be tailored out for inability to satisfy them. S-2 follows CNSSI.

## SP800-53R5

- Expected shares: noise 55 of 81, 68%, over the 50% line. Retired 0%. Flag: Chapters 1 and 2 are mostly description, definitions, audience and outline, and Table 1 alone is 10 rows.
- Source conflicts: 0006 says the controls "are recommended for use by organizations"; 0012 says their use "is mandatory for federal information systems". Footnote 12 reconciles them.

## SP800-60V1R1

- Shares expected: retired 1/202 = 0.5%. Noise 133/202 = 65.8%, OVER 50%, FLAG: needs a `noise` record. Executive summary, publication lists, BRM areas, FIPS 199 tables, examples, Figure 3 and the 'may consider' list account for it. Without promotions 133/198 = 67.2%.
- Source conflicts: (1) 0012 excludes national security systems, but the framework cites this document at P-12 and C-2 for every run. CNSSI 1253 brings section 4.4.2 back by name; the rest rests on C-2's method. (2) 0167, 0201 (iv) and 0068 set one overall level; CNSSI 1253 Section 1.2 does not adopt that, so a default run has none, as for REQ-FIPS200-0015. (3) WI-13 will make system value derive from type values, while 0150, 0154 and 0155 require upward adjustment past the high water mark: its rule must accept a recorded adjustment, or it blocks system-categorization-adjustment. (4) Table 3 gives Step 2 to the ISSO, the P-12 raci gives it to PER-PM and PER-IO; act held, role differs. (5) 0069 makes categorization an input to the risk assessment; the framework runs P-14 before C-2 on ART-INFOTYPES' provisional levels and has C-2 read ART-RA. (6) C-2 step 4 forbids editing infotypes.yaml, so `selected` and `adjustment_justification` have no writer at C-2; adjustments land in ART-CAT only.
- References leaned on and missing: HSPD 7 (0161, superseded; the current directive is not in the library); OMB M-03-22 (0163); Volume II Appendix E is outside the catalog's scope.

## SP800-60V2R1

- Shares: noise 10/11 = 91%, OVER 50%, flag: an executive summary of a catalog; needs a `noise` record. Retired 0%.
- Source conflicts: none. Brief: clear for catalog mode; the job says page 6, sources.yaml scopes 6 to 7, sparse.

## SP800-61R3

- Expected shares: noise 117/246 = 47.6%, under 50%, close. Retired 1/129 = 0.8%. No flag on either limit.
- Row sets, each one way. Table 1 (0031 to 0034), crosswalk: all noise. Profile: a Subcategory row is a live outcome, with or without an R, because p18 calls the Profile a baseline of outcomes, p19 says low rows are 'not unnecessary', and sources.yaml names the rows as requirements. A Function or Category row with no R only defines its group: noise pointing at its Subcategories. One carrying an R is live: 0091, 0096, 0191, 0198, 0209, 0224, 0229. N and C items are advisory and make nothing live. FLAG: this is a judgment. 55 live rows have no R; read as noise instead, noise becomes 172/246 = 70%, over the 50% limit.
- Of the 46 x_existing without a gap, 38 rest on a control in the CNSSI 1253 baseline, the rest on an artifact or task. FLAG: no task after I-2 outputs ART-IRP, so ir-8 c has no later step that refreshes the plan (WI-07 at 0155).
- Library lacks: CSF 2.0, CSWP 32, SP 800-84, SP 800-92r1, SP 800-150, SP 800-184, SP 800-216, SP 800-218, IR 8286, CISA playbooks. All are pointers from notes; no live entry's duty needs their text.
- Source conflicts: none. sources.yaml exclusions true: p1 to 8 front matter and contents, p44 to 48 references to change log. The framework's section 2.1 and 2.3 citations show with `rmf refs show`.
