figures: {none: "pdf image lists are empty on pages 1 to 11; pages 6, 7, 11 are ruled tables and boxes"}

# CNSSI1253E-ATT1-TEMPLATE triage report (no tier 1)
- Pages read: 1-11 including excluded page 2. Entries: 77 (76 live, 1 promoted). 0011, 0053, 0054 and 0066 are `removed: true` and undecided. All decided; parses; duty words checked; reasons unique.
- Counts: not-a-requirement 65; x_new_work_item 12 (1 with x_gap); deferred 0; not-applicable 0; x_unsure 0.
- Expected shares: retired 0%. Noise 65/77 = 84%: OVER 50%, needs a user-approved noise record. Expected, the template is mostly examples. FW-REQ-004's combined share trips too.

Misses promoted (1): 0081 p2, Section 2's Guidance: version of SP 800-53, documents used, update events.

Rule applied: Guidance boxes are live, as they name what a fork writes when defining an overlay. Examples, sample tables, sample definitions and boilerplate legends are noise, with the duty word quoted. The same words bind in the overlay they came from, cross-referenced there.
Row sets, each one way: legend 0030 to 0034 noise under 0029; sample table 0039 to 0050 noise; PS-5 table 0051, 0052, 0076, 0077 noise. 0036 is mixed: the R row joined with a live note, 'these additional symbols should be used', and 0037, 0038 point at it.

Work items
- overlay-justification, extended (10, on top of SP800-53B's 1): P-4: 0001, 0010, 0023, 0029, 0035, 0036, 0055, 0065, 0072, 0081. P-4 lets an org publish overlays and says nothing of their content. If the lead prefers, rename it overlay-definition-content, since justification is now only part of it.
- baseline-assumptions (0078): a user of an overlay, at S-2.
- enhancement-needs-base (0080), gap tailoring-legal-floor.

Cut pairs: none.
Scope defect: excluded page 2 says 'Section 2, authoritative references' but opens with the end of a Section 1 example and holds Section 2's instruction. Rescope it.

Source conflicts
- 0029 says the Privacy Overlays have 3 columns; the current one has 4 sets and an optional column.
- 0051 and 0064's PII samples use the PCIL form, which the Privacy Overlays replaced.
- 0012 to 0022 are an older Space overlay than the August 2025 attachment.
- 0008 labels 45 CFR parts 'Federal Acquisition Regulations'.
Brief: line 115 settles examples; 'boilerplate information' is a third kind, text an overlay keeps. I split it: legends noise under 0029, 0078 and 0080 live, since they bind a user of any overlay.
References the library lacks: none needed beyond WI-22's CDS Overlays.
