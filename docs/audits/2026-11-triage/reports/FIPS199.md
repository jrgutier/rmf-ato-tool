figures: {}

# FIPS199: pages 1 to 10
- Pages read: 10 (job said 2 to 10; p1 is in scope and is the cover, p4 contents). No figure or image; Table 1 on p10 is live text, and FIPS199 is not in the I-4 list.
- Entries: 30 plus 2 promoted = 32. Counts: not-a-requirement 20; live 12: x_existing 8, of which 1 carries x_gap (0010); work_item WI-13 3 (0017, 0018, 0031); x_new_work_item 1 (0016). x_defer 0, not-applicable 0, x_unsure 0.
- Misses promoted, 2: 0031 p7 acceptable values with NOT APPLICABLE (cut from 0015 by a blank line); 0032 p5 footnote 1, information categorized by its type.
- Not promoted, read: the 'The potential impact is LOW if—' lines (lead-ins of 0011 to 0013); objective and loss definitions on p6; footnote 2; Examples 1 to 5 prose and values.
- Cut pairs: 0015 with promoted 0031, both live. 0011, 0012, 0013 each with the rejected line above.
- Row sets: Table 1, 0026 to 0029, noise, one row set. Levels 0011 to 0013 noise as definitions; the duty to apply them is 0010, and C-2 cites p10.
- Proposed new work items: system-information-type (1): 0016. Home P-12, ART-INFOTYPES. No existing slug holds it.
- Reused: WI-13 0017 0018 0031; gap on 0010 to system-categorization-adjustment, extended (CNSSI1253 0051 named it).
- Shares: noise 20 of 32 = 62%. FLAG: over 50%. Foreword and FISMA background 8, level definitions 3, Examples 4 and 5 and footnote 5 5, Table 1 4: the standard is short and most of it is definition and example. Needs a noise record with approved_by user; policy.yaml has none for FIPS199 (rules.py: 20 over max(10, 16)). Retired 0.
- Source conflicts: FIPS 199 leaves out national security systems (0008) and DoDI 8510.01 categorizes every DoD system under CNSSI 1253; the forms match, so x_existing rests on C-2. CNSSI 1253 0046 keeps three levels for the system value, consistent with 0019 and 0020; WI-13's enum change must go to infotypes.schema.json only, not facts.schema.json.
- Repo: C-2 step 7 and facts `impact` are correct for 0019, 0020. 0031 and 0017 are the real gap.
- Brief: nothing wrong. Definitions in a mandatory standard are noise by the brief, though C-2 rests on them; a reviewer might want them live with x_existing on C-2.
