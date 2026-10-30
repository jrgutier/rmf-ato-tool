---
artifact_id: ART-CMP
run_id: example-synthetic-01
produced_by_task: S-4
touched_by: [S-4, I-2, M-1]
sources: [INT-107.A1, INT-107.A2, INT-108.A1, product/architecture.md#configuration, product/architecture.md#updates, INT-055.A1, INT-060.A3, INT-063.A2, INT-064.A1]
---
# Configuration management plan

## Plan summary

The plan covers every station kit, which shares one configuration baseline: the workstation
image built to the Windows STIG, the router built to the network device STIG, and the hand
hardening of the mission planner, with deviations recorded in the STIG summary
[[product/architecture.md#configuration]]. Baseline changes go through the SUGS-PO
configuration control board. Changes reach the stations only as the integrator's signed
quarterly update bundle, whose signature is checked before install
[[product/architecture.md#updates]]. A compliance check runs at every start-up and before each
mission upload and reports drift to the local log, which the ISSO reviews [[INT-055.A1]]. The
full plan with roles, configuration items and procedures is written before the assessment.

## Update Control Implementation Information (I-2)

The as-implemented baseline is release 2.3.0 on all six test stations, with the versions in
the inventory (GDT firmware still 5.1.8; 5.2.1 waits for regression testing in the 2026-12
bundle) [[INT-064.A1]]. The STIG summary records the benchmarks, the open shared-account
findings STG-001 and STG-002 and the one deviation the board approved with the 2.3.0
baseline, 7-day cached CAC sign-in [[ART-STIG]] [[INT-060.A3]]. The full plan is drafted and
under ISSM review, to be signed before A-2 [[INT-063.A2]].

## System and Environment Changes (M-1)

In the first monitoring cycle the board handled two requests, each with an ISSO security
impact analysis reviewed by the ISSM: CR-2026-10 (2026-10 bundle) approved for the test
stations with a signature check at install and a scan before the next mission upload, and
CR-2026-12 (GDT firmware 5.2.1) approved for regression testing only [[INT-107.A1]]
[[INT-108.A1]]. Neither was significant, so neither went to the AO. The plan now names the
significant-change path: release 2.4 maintainer accounts and the release 3.0 planner
replacement go to the AO through the ISSM before installation [[INT-107.A2]]. The change log is
ART-CHG.
