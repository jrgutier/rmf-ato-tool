figures: {13: "opened PDF: Figure 1 repeats 4.1 and 4.2 and adds that privacy enhancing controls are selected as appropriate and that controls with privacy implementation considerations are identified at Refine; both are held in entries 0003 and 0042 or WI-32", 94-98: "no figure, ruled tables"}

# CNSSI1253F-ATT6-PRIVACY triage report (no tier 1)
- Pages read: 1-3, 7-28, 94-98, plus 29 and 93 for the scope defect. Entries: 76 (74 given, 2 promoted). All decided; parses; duty words checked against MODAL and SHOULD; reasons unique.
- Counts: not-a-requirement 40; x_existing 11 (9 with x_gap, counted across the entry types); x_new_work_item 24; work_item 1 (WI-17); deferred 0; not-applicable 0; x_unsure 0.
- Expected shares: retired 0%. Noise 40/76 = 53%: OVER 50%, needs a user-approved noise record. All true noise: 13 references, 1 heading, 20 PII examples, 6 footnotes and lead-ins.

Misses promoted (2): 0075 p97, factor 6 'Coordination with privacy and legal offices is necessary' (factor 7 p98 repeats it). 0076 p95, factor 2 'lower quality data ... should be accounted for'. The scope reads pages 94-98 with tables false, and the seven factors are table cells. Promote leaves trailing ' | | |' on both; statements are otherwise exact.

Row sets: legend 0052 to 0058, live one way: 0052 held by the + transcription, the rest overlay-control-specifications.
Cut pairs: none. 0062 lead-in with 0063, 0064 all live (values sit in the items; a duty never sits in noise), cross-referenced; h.3, i and j are on excluded page 29.

New work items, merged
- privacy-risk-analysis (8, gaps on 0047, 0067, 0070): C-2 step 6 and ART-CAT '## Overlays': seven factors, levels, weighting, overall level. No field or section holds a privacy risk level today.
- overlay-control-specifications (12 here, 3 Classified, gaps on 0042 and Classified 0024): S-2 and S-4: E, G, V, R marks, -- cell and * column of the Privacy and Classified overlays reach a run. Only + cells do today.
- pii-identification-basis (1, gap on 0021): P-12: what was examined, combinations, PII after processing.
- Reused: baseline-assumptions (0045), pii-impact-adjustment (0051), privacy-legal-applicability (0075). WI-17 gaps: 0001, 0003, 0046, 0050, 0067, 0070 (the SAOP consultation and approval, nothing records them).

Scope defects, conformance/sources.yaml
- Excluded 29-93 says 'Section 5, per-control specifications: work item WI-32'. False three ways: those pages are Section 6 (Section 5 is the summary on 13-28); WI-32's title is the Privacy Implementation Considerations, not per-control text, so no open item held the text until overlay-control-specifications; and page 93 holds Section 7, the very source of WI-32: 'Selection of these controls requires coordination with the SAOP, or designee'. Rescope 93 and promote it. I did not promote from 93.
- Scope 7-28 note 'Sections 3 and 4' is also wrong: page 7 ends Section 2, 13-28 are Section 5, and 28 opens Section 6, so 0060-0064 are half a control. The list breaks mid-h.
- Excluded 4-6 is fine. Section 6 holds real values (AC-2 j at High: quarterly for privileged accounts), and they stay outside the register.

Source conflicts
- 0067 cites 'Appendix D provides system risk analysis use cases'; this document has one Appendix and no use cases.
- Page 12 says the risk level replaces the PCIL; CNSSI 1253 footnote 23 and the template's sample still use PII impact levels. See 0049.
- Page 11: no control set for PHI; pii-phi-issuances should know.
- WI-13 NA and overlay removal: none here; AC-2(8) is the only -- row and sits in no NSS baseline, so nothing is removed.

References the library lacks: CNSSI 1015, CNSSP 11, 15, 17, 25, 26, the FPC Collaboration Index, OMB M-17-12, A-130.

Brief: Lines 89 and 111 pull apart on items holding bare values; I kept them live.
