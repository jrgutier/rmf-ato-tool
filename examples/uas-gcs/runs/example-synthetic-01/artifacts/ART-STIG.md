---
artifact_id: ART-STIG
run_id: example-synthetic-01
produced_by_task: I-1
touched_by: [I-1, A-3]
sources: [product/test-results.md#stig-scan, product/test-results.md#vuln-scan, product/test-results.md#account-review, product/conops.md#limitations, INT-060.A1, INT-060.A2, INT-060.A3, INT-060.A4, INT-061.A2, ASM-010, INT-091.A1, INT-091.A2, INT-092.A1, INT-092.A2]
---
# STIG and SRG summary

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## Applicability

The workstation image INV-002 is configured to the Windows STIG (BM-01) and the station
router INV-008 to the Network Device STIG (BM-02) [[product/test-results.md#stig-scan]]
[[INT-060.A1]]. The Application Security and Development SRG (BM-03) applies to the mission
planner INV-004, which has no STIG and was hardened by hand against the SRG
[[product/conops.md#limitations]], and to the integrator's flight control (INV-003) and
video (INV-005) applications, which have not yet been checked against it [[INT-060.A4]].
The ground data terminal firmware INV-007 and the mission map package INV-010 have no
applicable benchmark: the firmware has no DISA STIG or SRG and is covered by the
vulnerability scan and signed vendor releases, and the map package is data, not code
[[INT-060.A4]] [[INT-061.A2]]. Benchmark releases and rule IDs are placeholders
[[ASM-010]]. The records live in `artifacts/data/stig-summary.yaml`.

## Scan results

An SCA-witnessed STIG compliance scan of all six stations ran on 2026-09-15 against BM-01
and BM-02; it found no CAT I rules open and one open CAT II rule on each benchmark (STG-001,
STG-002) [[product/test-results.md#stig-scan]] [[INT-060.A2]]. BM-03 was not scanned: the
planner's hardening (STG-003) and the two integrator applications (STG-004, STG-005) are
`not-reviewed` [[product/conops.md#limitations]] [[INT-060.A4]]. Totals: 0 CAT I, 2 CAT II
open, 3 CAT II not-reviewed, 0 CAT III.

The same-day vulnerability scan is separate evidence, not a STIG result: 3 medium findings on
the workstation and router (fixes in the 2026-10 bundle), the high-rated ground data terminal
management service flaw (fixed in firmware 5.2.1, not yet fielded), and 2 medium findings in
the planner's bundled library with no vendor fix date [[product/test-results.md#vuln-scan]].

## Open findings

There is no open CAT I finding [[INT-060.A2]]. STG-001 (workstation) and STG-002 (router),
both CAT II and mapped to ia-2: the shared `gcsmaint` maintenance account cannot be tied to a
person [[product/test-results.md#account-review]]. Planned fix: per-maintainer local accounts
with offline CAC sign-in in release 2.4, planned 2027-02 [[product/conops.md#limitations]].
STG-003 to STG-005 (cm-6) are not reviewed; the planned action is the assessor's review of the
planner hardening in A-3 and an SRG checklist run on INV-003 and INV-005, with a replacement
planner evaluated for release 3.0 [[product/conops.md#limitations]] [[INT-060.A4]].

## Accepted deviations

The configuration control board approved one deviation with the 2.3.0 baseline: cached CAC
sign-in on the workstation lasts 7 days instead of the benchmark's shorter cached-logon
limit, because platoons operate disconnected from the brigade directory for days; DT-1 tested
the 7-day case [[INT-060.A3]] [[product/test-results.md#dt-1]].

## Assessor verification (A-3)

The assessor reused the SCA-witnessed 2026-09-15 STIG compliance scan of all six stations for
BM-01 and BM-02 rather than re-running it [[product/test-results.md#stig-scan]]. STG-001 and
STG-002 are confirmed open: the account review and the ISSO's records show `gcsmaint` still
shared by several maintainers on every workstation and router, with actions not attributable
[[product/test-results.md#account-review]] [[INT-091.A2]]. The STIG scan settings for
malicious code protection, data execution prevention and address randomization were
confirmed at baseline [[INT-091.A2]] [[INT-092.A1]]. STG-003 to STG-005 stay `not-reviewed`:
no SRG check of the planner, flight control or video applications was run during A-3, which
the assessment records as findings FND-021, FND-061 and FND-068 [[INT-092.A2]]
[[product/conops.md#limitations]]. The 2026-10 bundle is installed on all six stations but
no rescan has confirmed its fixes [[INT-091.A1]]. No finding status changed, so
`artifacts/data/stig-summary.yaml` is unchanged.
