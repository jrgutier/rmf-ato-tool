figures: {none: "pymupdf lists 0 images on pages 2 to 11; pages 5, 7 and 10 hold hairline rules and nothing else, so no page needed opening for a figure"}

# FIPS200 triage report (tier 1, statement mode)
- Pages read: 2 to 11, plus 1 and 12 to check the scope. No FIPS200 line in either audit file.
- Entries: 44, all decided, none promoted. The file parses, reasons are unique, and every MODAL or SHOULD word is in its reason.
- Counts: not-a-requirement 12; x_existing 28 (1 of them with x_gap); x_new_work_item 3; not-applicable 1 (0006); x_defer 0; work_item 0; x_unsure 0.
- Expected shares: noise 12/44 = 27%; retired 1/32 live = 3%. Neither limit is near.

Misses promoted: 0. Every rejection read: labels, leaders, footnotes that define or point, background.

Figure rows: none. Cut pairs: 0013 (live) with 0014 (noise, the formula after the colon).
Lead-in with bare nouns: 0044 has its own verb but is a completed act of Congress on NIST, so it and 0009 to 0011 are all noise.

New work items: none opened. Entries extend existing slugs.
- ref-edition-currency (2 + 2): 0007, 0040. Home: new REF rule on references/index.yaml. 0007 adds the one-year window from final publication.
- tailoring-legal-floor (4 + 1): 0008. Home: S-2 step 4 and an exit criterion. No waiver of a mandatory FIPS.
- tailoring-approval (gap): 0043, with REQ-SP800-53B-0056. Home: S-6 inputs gain ART-BASELINE.

Source conflicts
- High water mark, real for one class of fork. 0015 and 0035 want one overall level and one of three baselines. FIPS 200 excludes NSS (0004), and CNSSI 1253 Section 1.2 drops the concept for NSS, so a NSS has no conflict. DoDI 8510.01 page 8 puts every DoD system on CNSSI 1253, including a non-NSS one, which FIPS 200 still binds. On a non-NSS M-L-L system the per-objective union can fall below the moderate baseline (cp-6 is .XX on A only), and baseline.py refuses high-water-mark unless CNSSI 1253 is degraded, so that fork cannot follow FIPS 200 literally. Kept as x_existing, as REQ-SP800-53B-0026 was, because the DoD instruction governs a run; this is the one call in this job the user may want to see.
- Catalog and PDF differ: the pin for SP800-53R5 is the PDF of 12-10-2020, the OSCAL catalog is Rev 5.2.0. 0040 asks for the most current version; recorded on that entry.

Judgment for the audit
- 0036 to 0038 'minimum assurance requirements': held by the baseline's assurance-related controls, with no x_gap. The pinned Rev. 5 has no per-baseline list (Section 2.5, Appendix C; sa-4 part c). implementation-assurance stays a further record. An auditor who reads the clause as needing its own record would add that slug as x_gap on 0035 to 0038.
- 0008 has no duty word and is kept live as a legal limit. 0006 is a spent deadline, so not-applicable rather than noise.
- 0014 is noise: its 'acceptable values' repeat 0013's three levels.
- 0028 clauses ii and iii and 0026 'timely' rest on controls that start at moderate availability; 0005 makes the baseline the standard's own minimum, so these are held.

Brief and scope
- The brief's lead-in rule says the piece with the verb is live; 0044 needed the exception above, since its verb is history.
- Nothing else was unclear.
