figures: {1: "opened PDF: Figure 1, profile scope box around the space platform and link segment; ground and user segments outside. Agrees with 0001, no further requirement", 2: "opened PDF: Figure 2, SDLC coverage: primary focus on orbit check out, operation, decommissioning; design influence only. Scope, no requirement", 3-5, 7-14: "ruled tables, no figure"}

# CNSSI1253F-ATT2-SPACE triage report (no tier 1)
- Pages read: 1-14 including excluded page 2. Entries: 22 (20 given, 2 promoted). All decided; parses; duty words checked; reasons unique.
- Counts: not-a-requirement 13; work_item WI-21 7; x_existing 1; x_new_work_item 1; deferred 0; not-applicable 0; x_unsure 0.
- Expected shares: retired 0%. Noise 13/22 = 59%: OVER 50%, needs a noise record. A small document: headings, four describing items, rationale.

Misses promoted (2), both on page 2: 0021 'other overlays should be considered'; 0022 'defines a maximum control baseline'.

Class rule: nothing of this overlay is transcribed, so 7 entries bind WI-21 and name the controls. 0006 names Table 1's Associated Controls: closure must carry each removal's assumption, because an add and remove list cannot test 'if any vulnerability assumption is not valid'. 0013 is ra-external-risk: subject in personas, no control states it, same as CNSSP12 0012.
Row set: legend 0014 to 0016, live, WI-21.
Lead-in: 0008 live, items 0009 to 0012 describing noise. 0009 is cut, the rest of it is a rejection, 'Information; and/or'.
Cut pairs: none live. 0002 is a fragment across Figure 1.

Checked against WI-21: Table 2 has 83 +G and 262 -- rows, as the title says.
Conflict to settle in WI-21: 262 removals + 306 retained = 568, but framework/baselines/cnssi-1253.yaml selects 573 at High on any objective. Five controls are unreconciled; I did not find which.
Design points for WI-21: the overlay is 'not baseline independent' and defines 'a maximum control baseline'. baseline.py selects per objective, so a platform below H/H/H has no defined result. C-2 step 6 says 'applies to space systems', wider than platform plus link segment. Section 6 also has per-control G text.

Scope defects, conformance/sources.yaml
- Excluded page 2 says 'Section 2, authoritative references'. The page's first half is Section 1: Figure 2, the SDLC, baseline dependence, the maximum baseline. Rescope it, or 0021 and 0022 sit on an excluded page. `rmf conformance extract --check` stays current with them.
- Basis 'tables false' on pages 3-5 leaves Table 1 unread by the extractor; WI-21 must take it, since it pairs assumptions with controls.

New work items: none. Reused: ra-external-risk (0013).
References the library lacks: CNSSI 1200 (Applicability cites it), Aerospace TOR-2023-02161, SPARTA website.
Source conflict: none other than the 568 and 573.
Brief: nothing unclear.
