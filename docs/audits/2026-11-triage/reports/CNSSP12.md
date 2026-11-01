# CNSSP12 triage report
figures: {}
All 15 pages are scans. No in-scope page holds a figure; every in-scope page was opened as an image. The seal on p. 2 is out of scope.

Pages read: 5-11 (7 pages) from the PDF, plus pp. 2, 12, 14, 15 for context. Entries: 66, all decided; file parses, keys match the register, duty-word and duplicate-reason checks pass.
Counts: not-a-requirement 19; not-applicable 6; x_existing 21 (15 with x_gap); x_new_work_item 15; work_item 5 (WI-21 4, WI-31 1); x_defer 0; x_unsure 0.
Misses promoted: 0. Every numbered paragraph and lettered item on the seven pages is an entry. Rejections are tails with no verb, scan specks ('I') and the enclosure list.
Figure or crosswalk rows: none.
Cut pairs (live piece first, or both noise): 0018 with rejected CNSSP 8 title, p. 7; 0027 with rejected 'policies issued by...', p. 8; both noise: 0002 and its tail, 0014 and '100 kilometers'. 0010 runs to p. 6 and caught the running head.
Lead-ins noise, items live: 0020, 0033, 0038, 0046, 0047. Cross-referenced: 0013 with 0056; 0019 with 0059; 0024 with 0051; 0027 with 0061; 0039 with 0035, 0057; 0043 with 0058.
Shares: retired 6 of 47 real = 12.8% (0037, 0040, 0041, 0042, 0043, 0055). Noise 19 of 66 = 28.8%. Neither limit is near.

Work items: no new slug. New entries on existing slugs (g = x_gap):
- nsa-crypto-approval +6, +1g: 0034 0035 0039 0045 0057 0064, 0036g. Home S-4 step, sc-13 statement. Extended to SKMP, CSP, bypass approvals, the STP and a consultation before P-17. Lead to confirm.
- nsa-nss-assessment +4, +1g: 0026 0044 0054 0056, 0058g. Home new EXT entry, P-16. Extended by 0058g to status sent back to NSA, and by 0054 to 'periodically'. Lead to confirm.
- irp-reporting-paths +1, +2g: 0060, 0016g 0062g. Extended to reports to the intelligence authority and to the AO as a named recipient.
- ra-external-risk +1, +1g: 0012, 0013g. EXTERNAL-SYSTEM-ASSESSMENT +1: 0023. foreign-access +1: 0018. control-lifecycle-budget +1: 0052, with acquire and decommission added.
By x_gap only: org-crm-program 0021g 0048g; MISSION-PARTNER-AGREEMENT 0019g 0059g; sse-practices 0015g; cyber-degraded-exercise 0017g; control-requirement-trace 0028g; org-context-upkeep 0029g; sca-team-quality 0049g; WI-37 0049g; WI-21 0028g 0032g 0034g; fisma-reporting 0027g 0061g.
Bound: WI-21 0017 0030 0031 0036; WI-31 0025.
fisma-reporting is not in slugs.txt: DODI8510.01 named it only in x_gap, so it has no description or home yet.

FLAG, the class rule. The brief says a duty only one class of fork has is not-applicable. Every entry here is written for space NSS, so read literally that retires the document. I applied it this way:
- Substance every fork has, with space only as the subject (RMF, roles, core documents, FISMA, patching, incidents): held or slugged as for any fork. 0016 0021 0022 0024 0027 0032.
- Space-only and carried by a control the Space Platform Overlay adds: WI-21. 0017 0030 0031 0036. The controls are unselected today (I checked the baseline), and their guidance states the duty: SC-51 secure boot and root of trust, SI-4(7) on-orbit IDS, SC-8(3)/(4) TRANSEC, CP-12 and SI-17. This matches REQ-DODI8500.01-0355's x_gap, 'CNSSP 12 at WI-21', and overlay section 4 takes its scope from CNSSP 12.
- Space-only with no open item: not-applicable with the condition. 0037 (launch vehicles), 0055 (contracts against this policy).
If you want the rule literal, move 0017 0030 0031 0036 to not-applicable: retired becomes 10 of 47 = 21.3%, still under the limit.
FLAG: an overlay transcription binds these only if WI-21's closure tests that a space run selects those controls. Transcribing the overlay alone does not show a secure boot is built.
FLAG: CNSSI 1200 (Aug 2025), which holds the detailed space requirements and the exceptions to 14.a, is not in references/index.yaml. Nor are CNSSD 505, CNSSI 1010, CNSSP 11, 15, 31 or CNSSD 502. Entries 0026 0028 0034 0035 0037 lean on 1200; a space fork cannot read them from this repository.

Source conflicts:
- Reference letters in the body run one behind Annex B from s on: CNSSI 1253 is s in the body and t in Annex B, whose s is PL 114-113; CNSSI 1253F2 t and u; CNSSD 502 w and x; CNSSI 1010 x and y; CNSSP 15 y and z; CNSSP 11 z and aa.
- 14.c prints 'CNSSP 3 (Reference u)' (read at 200 dpi). Annex B has no CNSSP 3; CNSSP 31, the TRANSEC policy, is at v and CNSSI 1031 at w. Likely a printing error; the statement stands as printed.
- Annex A calls CNSSI 4009 Reference aa; para 17 and Annex B say bb.
- 13.b gives SP 800-37 the Revision 1 title; Annex B n says Rev. 2 with that same title.

OCR that changes a word, for anyone quoting evidence: 0026 'SA' for NSA and 'C SSI 1200'; 0021, 0029 'CNS SP 22'; 0024 'CNS SI 1254'; 0051 'CNSSI I 254'; 0062 'CNS SI 1010'; 0065 'CNSSl 4009'; 0045 'SK.MP'; 0043, 0058 'com pliancy'; 0003 'ational'. Locators wrong: 0022 'a.-', 0033 'h.(4).14', 0046 'g.16', 0012 to 0014 'c.5' to 'c.7'; each is the para number on the page.
Brief: the class rule has no case for a document wholly about one class. 'x_gap' is defined beside x_existing only; 0017, 0034 and 0036 use it beside work_item or x_new_work_item, as DODI8500.01-0357 does.
