---
artifact_id: ART-PIA
run_id: 20261118-synthetic-01
produced_by_task: P-14
touched_by: [P-14]
sources: [INT-029.A4, INT-036.A1, INT-036.A2, INT-036.A3, ASM-011, ART-INFOTYPES, product/privacy.md#pia]
---
# Privacy impact assessment

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| Authorization boundary | EFRAS-BND-1 | P-11 |
<!-- END rmf:facts -->

## Determination

P-12 determined that a PIA is required: EFRAS is a new DoD information system holding PII about
federal personnel in electronic form, and the national security system exclusion is not used.
It is due before production deployment of release 1.5 (MVCR), no later than 2027-02-01
[[INT-029.A4]] [[ART-INFOTYPES]].

## Assessment

**Status: draft.** The PIA on DD Form 2930 is version 0.9 of 2026-09-30, with the Component
privacy office, and is not complete: the office's question on how the de-identified exports are
protected is open [[INT-036.A3]] [[product/privacy.md#pia]]. The draft, as recorded in
`artifacts/data/pia.yaml` `assessment`, finds the PII needed to show qualification coverage and
join actions to people; its risks are re-identification of the pseudonymized exports and the
training extract (demonstrated by the red team), breach exposure and alteration; the protections
in place are CAC sign-in, squadron scoping, encryption, export audit and the 5-year purge, and
salted, rotated pseudonyms with an export retention rule were chosen over the alternatives for
release 1.6 [[INT-036.A1]] [[INT-036.A2]].

## Coordination, reviews and approval

The PM coordinated the draft through the ISSM (2026-09-22), the records management office
(2026-09-28) and the privacy office (2026-09-30) [[INT-036.A3]]. **The reviews and the approval
have not happened.** The dates in `pia.yaml` for the PER-CISO cybersecurity policy review and the
PER-PRIV privacy policy review (2027-01-20) and for the Component CIO's approval (2027-01-25) are
the privacy officer's planned dates, recorded only because the PIA record cannot hold a draft
[[ASM-011]]. Until the approval is given, the unapproved PIA is an open weakness (VUL-07 in
`ra.yaml`), as the program itself discloses [[product/conops.md#limitations]].

## Submission, publication and updates

Planned: submission of the approved PIA to the DoD CIO and publication of section 1 on the
Component's public PIA page in the week of 2027-01-25, kept there while EFRAS holds PII; neither
has happened [[INT-036.A3]] [[ASM-011]]. No later review is recorded yet; release 1.6, which
changes the pseudonyms, is the first change expected to prompt one [[INT-036.A1]].
