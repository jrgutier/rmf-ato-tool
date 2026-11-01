# CNSSI1254 triage report
figures: {}
No figure on any page: `pdfimages -list` shows images on pp. 1 and 2 only, the seals, both out of scope.

Pages read: 4-28 (25 pages, whole text plus `conformance page`). Pp. 7-10 are excluded in sources.yaml and hold no entries; read anyway. Table layout on pp. 13, 16, 17 checked with pdftotext.
Entries: 148 (145 plus 3 promoted), all decided; file parses; keys match the register exactly; duty-word and duplicate-reason checks run.
Counts: not-a-requirement 24; x_existing 55, 26 of them with x_gap; x_new_work_item 53; work_item 16 (WI-18 12, WI-29 3, WI-09 1); not-applicable 0; x_defer 0; x_unsure 0.
Table C-1 rows decided one way: every element row is a requirement under 8.b's 'must be captured' (0012), so each is held or bound. Only heading rows 0027, 0103 and tail 0059 are noise.
Misses promoted: 3. REQ-0146 p. 26 'Provides status updates of the RMF activities'; REQ-0147 p. 26 'Resolves any security issues raised'; REQ-0148 p. 28 'Provides a copy of implementing documentation'. All were rejected for no marker. Other rejections read: definitions, footnotes, lead-ins, labels, no duty.
Cut pairs: 0058 with 0059 (row 20 split by the page break, 0058 live); 0025 with a rejected fragment (both noise). Entries cited on one page and running to the next: 0012, 0123, 0141, noted.
Lead-ins noise with live items: 0020, 0113, 0119, 0126. Own verb over live sub-items: 0128 over 0146, 0147; 0136 over 0137-0139; 0141 over 0142, 0148. Definitions: 0009 over 0010, 0011.
Shares: retired 0 = 0%. Noise 24 = 16%. Nothing near a limit.

Proposed new work items, merged, 7 (g = x_gap on an x_existing entry):
- core-doc-facts (6): 0029 0035 0036 0058 0037g 0131g. Home: C-1 step 4, facts.schema.json, rmf:facts block through facts.LABELS; A-3 sets the assessment date.
- ssp-status-section (5): 0040 0041 0043 0055 0054g. Home: S-4 step and a new ART-SSP section, rewritten by R-5 and M-6.
- sar-assessment-record (4): 0062 0063 0065 0066. Home: A-3 step 6, a new ART-SAR section.
- poam-cnssi-fields (7): 0100 0093g 0095g 0097g 0098g 0099g 0101g. Home: A-6 step 5, M-3, R-3, poam-items.schema.json, POAM-FLD-001.
- sd-nss-characteristics (4): 0051 0052g 0060g 0061g. Home: C-1 steps 5 and 8, ART-SD, users.schema.json.
- data-element-crosswalk (4): 0003 0012 0006g 0039g. Home: R-1 step, a new rule beside PKG-001, the map under framework/.
- aodm-fields (2): 0105g 0108g. Home: R-4 step 6, ART-AODM.
Reused: receiving-assessment +9, 20 of 25; receiving-deployment +6, 16; granting-package-sharing +5 with 0116g, 16; reciprocity-agreement +3, 19; granting-requirements-coordination +3; granting-notifications +2; system-type +2 with 0057g; authorize-consultations, CLASSIFICATION-HANDLING, cloud-cso, control-requirement-trace, receiving-sustainment, reciprocity-refusal, ref-edition-currency +1 each. By x_gap only: ccp-package 0054g, ra-external-risk 0044g, SAP-TAILORING 0067g, ASSESSMENT-REUSE 0071g.
Extended beyond their wording, lead to confirm: inventory-asset-system (0056, 0045g, model, serial, owner, CNSSP 11, software category); connection-cds (0046g, interface fields); role-government-personnel (0053g, title, organization, contact columns); nsa-crypto-approval (0042, FIPS answers, key management); DETERMINATION-RECORD (0068g, a not-evaluated value).
Bound: WI-18 0072 0073 0076 0079 0080 0081 0084 0085 0086 0089 0090 0092, plus 0077g. WI-29 0122 0124 0125, no slug covers a system taken over from another organization. WI-09 0050.

FLAG: the x_existing on RAR rows reads ART-RA and ART-RAR together as the RAR. ART-RA is `package: supporting`, ART-RAR `core`, and threat events and vulnerabilities live only in ART-RA. If the lead wants them in the core document, 0074 0075 0078 0082 0083 move to WI-18.
FLAG: 0114 is held by the shape of decision.yaml, one object per run. No rule tests it. 0114 is my weakest x_existing.

Source conflicts:
- 'must be captured' (8.b, 0012) against 'provide guidance' (Annex C para 2, 0019; para 5, 0005). I took must: the cover says the Instruction prescribes minimum standards.
- Annex D 2.d (0117) says a receiving AO issues no new ATO; 3.b (0121) says the AO may issue a separate authorization; 5.f (0141) has an authorization to connect; DODCIO-RECIPROCITY has an ATU. Decision type stays with WI-01.
- 0104 limits the decision to ATO or DATO; 0040 lists five statuses, including IATT and no determination. Neither fits AD-* exactly.
- 0118 gives a refusal 'upon request'; DoD's 10 business days is stricter, not a conflict in effect.

Extraction defects: context and locator read REFERENCES on all of Annexes C and D (the markdown heading on p. 7), the WI-54 class though this document is not in that item. Six rows have the next section heading glued to their number: 0035 0036 0038 0061 0071 0092. Para 5's subject is a rejected lead-in, so items a to i have no subject in the register.
Brief: BRIEF.md and slugs.txt changed during this job (10:22). I re-read both and merged 11 draft slugs into 7 before writing. x_gap has no field for a slug's description, so aodm-fields is described inside 0105's x_gap.
