figures: {none: "pages 5-9 are ruled tables; pdf image lists are empty on every in-scope page"}

# CNSSI1253E-ATT5-CLASSIFIED triage report (no tier 1)
- Pages read: 1-9, 41-43, plus excluded 2 and 10. Entries: 43 (42 given, 1 promoted). All decided; parses; duty words checked; reasons unique.
- Counts: not-a-requirement 16; x_new_work_item 16; work_item 7 (WI-32 5, WI-22 2); x_existing 4; 6 entries carry x_gap; deferred 0; not-applicable 0; x_unsure 0.
- Expected shares: retired 0%, noise 16/43 = 37%. No flag.

Misses promoted (1): 0043 p2, 'does not include control specifications for cross domain solutions ... refer to the appropriate overlay'.

Cut pairs: 0011 with 0041, at 'These procedures'; both live and cross-referenced.
Row sets: legend 0021 to 0024 live (0021 held by the add list, 0022 and 0023 overlay-control-specifications, 0024 WI-32 with V as gap). Implications 0025 to 0028 live under WI-32, as CNSSI1253 0082 to 0085.

Class rule: the add list is transcribed, so a classified fork gets those controls at S-1. Duties beyond it:
- classified-conditional-controls (7, new): 0029, 0033 to 0038. S-2 step 3. Five controls Table 2 selects on a condition: ac-18.1, ac-18.5, ac-19.5, sa-9.8, si-20. In no add list.
- overlay-control-specifications (3): 0022, 0023, 0032 (SR-12 value).
- baseline-assumptions (4): 0013 to 0016: SAP, clearance, U.S. citizens, facility. Extended from CNSSI1253; gaps WI-22 (0013), foreign-access (0015).
- tailoring-legal-floor (0001): an overlay control 'should not be tailored out without significant justification'; tailoring.yaml treats it like any other removal.
- CLASSIFICATION-HANDLING (0041, gaps on 0011, 0017): no classification fact, and a spill is not separated from design.
- WI-02 gap on 0040: the privacy plan.
WI-32 closure must cover Table 1's Privacy Implementation Considerations column here as well as Appendix D's.

Scope defects, conformance/sources.yaml
- Excluded 10-40 says 'control text reaches a run through the baseline at S-2'. False: catalog text does; this overlay's Justification, Guidance and Parameter Value text does not, and only the IDs are pinned. No open item held them until overlay-control-specifications.
- Page 10's lead holds two rules for every overlay: enhancements need the base control, and care in tailoring. Template 0080 carries the same boilerplate.
- Excluded page 2 says Section 2 only; its first paragraph ends Section 1 (0043).
- Scope 41-43 note 'Sections 7 and 8': page 41 begins with Section 6's tail, so 0030 to 0032 are per-control text in scope by accident.

Source conflicts
- 0007 cites the template as August 2013; the library's attachment is December 2022.
- 0043's third class, networks with non-US persons, names no overlay the library or WI-22 holds. See 0015.
References the library lacks: CNSSD 504, 505, CNSSP 15, 17, 18, 25, 26, 32, CNSSI 1001, EO 13526, EO 13873, NSM-8, CDS Overlays and Intelligence Overlay (WI-22).
Brief: SR-4 and SR-7 justifications are noise as they report an EO; SR-12's value is live.
