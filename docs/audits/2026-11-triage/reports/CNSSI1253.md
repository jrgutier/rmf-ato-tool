figures: {none: "pdfimages and pymupdf list no image on pages 5-16, 22-24, 161; each page has 0 to 3 vector rules (footnote lines, underlines); page 23, the one with 3, rendered and opened: no figure, no requirement"}

# CNSSI1253 triage report (tier 1, statement mode)
- Pages read: 16 (5-16, 22-24, 161), plus page 25 for the table layout. Tables D-1 to D-20 are excluded and pinned by rmf_tool.cnssi1253 (`--check`: current).
- Entries: 109 (108 given, 1 promoted). All decided; the file parses, reasons are unique, duty words are in every noise reason.
- Counts: not-a-requirement 53; x_existing 35 (17 with x_gap); work_item 17 (2 with x_gap); x_new_work_item 4; not-applicable 0; x_defer 0; x_unsure 0.
- Work items bound: WI-32 ten, WI-17 two, WI-13 two, WI-20 two, WI-22 one.
- Expected shares: noise 53/109 = 49%, under 50% by one entry. Retired 0/56 live = 0%.

Misses promoted (1)
- 0109, p15: 'b. Apply scoping considerations:', the verb over the six nouns, rejected as a lead-in.

Cut pairs: 0043 with 0044, cut at 'SP 800-' / '37.', both live and cross-referenced. Seven statements span two pages (0007, 0015, 0018, 0041, 0060, 0090, 0105); x_note says so. 0105's anchor is the bare 'If the'.

Row sets: 0082 to 0085, the subscript legend, decided one way, live under WI-32: Appendix D checkmarks carry those numbers.

New work items (5)
- assurance-tailoring: 0074. S-2 step 3. The Assurance column is untranscribed and rmf catalog show does not surface contributes-to-assurance.
- system-categorization-adjustment: gap in 0051. C-2 step 5, SP 800-60 V1 Section 4.4.2 factors.
- pii-impact-adjustment: gap in 0049. C-2 step 4.
- overlay-conflict-raci: gap in 0062. S-2 raci gains PER-RE, step 3 names the three roles.
- control-sufficiency-recheck: gap in 0040. M-1. No M task or playbook names categorization, overlays or tailoring.
- Reused: baseline-assumptions (0020, 0030), tailoring-specification-info (0071); as gaps compensating-control-record (0068), tailoring-legal-floor (0041, 0109), objective-downgrade (0109), tailoring-tradeoffs (0072), tailoring-approval (0077). WI gaps: WI-02 (0041, 0075, 0076, 0077), WI-05 (0014), WI-17 (0039, 0040, 0048, 0061), WI-20 (0007, 0069), WI-21 (0034, 0061), WI-22 (0034, 0036, 0061).

What is transcribed: only the X, +, -- and blank cells, the Classified add list and the four Privacy sets. Parameter Value, Privacy Implementation Considerations, Justification, Assurance, Resiliency, ATT&CK, Space, CDS and Intelligence are not, so no x_existing rests on them.

Defect found while checking homes: FACTS-001 tests `approved.value` only, and facts.schema.json takes any PER-* as approved_by. playbooks/C/C-2.md step 7 says FACTS-001 holds the approver to the AO or AODR, and the x_note of SP800-37R2 0282 repeats it. Neither is true. 0054 stays held by C-3's steps; the rule needs a fix.

Source conflicts
- WI-13 asks for NA in the enum. 0046 'Retain the three impact levels' and 0007's precedence keep c, i, a at low, moderate, high for NSS, so NA can stop at the information type at most. Decide before WI-13 changes facts.schema.json.
- Footnote 23 sends the reader to 'the different impact levels of PII' in the Privacy Overlays; the attachment's privacy risk analysis 'replaces the analysis to determine a privacy confidentiality impact level'. pii-impact-adjustment must rest on that analysis.
- High water mark: Section 1.2 rejects FIPS 200's, 3.1.2 requires one per objective. Not a conflict; C-2 follows it.
- Section 3.2.2 applies overlays at S-2; the tool decides them at C-2 before C-3. 0061 notes it, and S-2 step 3 revisits them.

Brief and scope
- Lines 89 and 109 disagree when a lead-in was rejected and half its nouns are entries. I promoted the verb and pointed the nouns at it, so gaps sit on one entry.
- 0016 'It is essential' kept live, though 0017 is its firmer form: a duty never sits in a noise entry.
- Judgment for the audit: 0044 'It is advantageous' kept live as a soft duty the RACI carries; 0104 'may consider' is noise; WI-13 bound on 0050 and 0051 on the WI-17 precedent, prose in a playbook with no rule reading the data.
