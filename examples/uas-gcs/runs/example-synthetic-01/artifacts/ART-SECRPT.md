---
artifact_id: ART-SECRPT
run_id: example-synthetic-01
produced_by_task: M-5
touched_by: [M-5]
sources: [ART-CONMON, ART-SAR, ART-POAM, ART-RA, INT-114.A1, INT-114.A2, INT-115.A1, INT-112.A1, INT-113.A1, INT-113.A2]
---
# Security and privacy posture report

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

## Reporting period and recipients

First report, covering monitoring cycle 2026-10 (2026-10-01 to 2026-10-28, six test-range
stations). Recipients are the AO, the AODR and the Component CISO, as `artifacts/data/conmon.yaml`
sets them; from here on the report is quarterly, with the ISSM's posture review of metrics and
POA&M status [[ART-CONMON]] [[INT-114.A1]]. Until the station is on the enclave dashboard
(POAM-018, due 2027-02-26) this report is the AO's only posture view [[INT-114.A1]].

## Posture summary

- **Control effectiveness:** the M-2 ongoing assessment reassessed the au, cm, ra, sc, si and pe
  controls due in the cycle. Configuration, boundary, malware protection and physical controls
  held: no drift at 41 start-ups and 37 uploads apart from one screen-lock change, the witnessed
  STIG scan at baseline, and seal checks at all 22 kit setups. The weaknesses found at A-3
  remain: shared `gcsmaint` and GDT administrator accounts, planner and GDT logs that are not
  forwarded or correlated, the GDT management-service flaw and two planner library flaws
  [[ART-SAR]].
- **POA&M:** 68 open items (38 moderate, 30 low; none high), 1 completed. No milestone fell due
  in the cycle and none is late [[ART-POAM]] [[INT-114.A1]].
- **Risk:** overall moderate, inside the AO's tolerance; no rating changed [[ART-RA]]
  [[INT-112.A1]].
- **Privacy:** risk to individuals low; the privacy threshold analysis still awaits the SAOP
  designee's signature (due 2026-12-15), so the pt and PII inventory items stay ongoing; no
  privacy incident or breach [[INT-115.A1]].
- **Supply chain:** the mission planner vendor confirmed end of support for 2027-06; no
  replacement is selected yet [[ART-RA]].
- **Incidents:** none reported to the CSSP in the cycle [[ART-SAR]].

## Changes since the last report

This is the first report, so changes are counted from the authorization decision
[[INT-114.A1]]:

- **Security plan:** no SSP statement changed [[ART-SAR]].
- **Assessment results:** one changed determination, ra-7 from other-than-satisfied to
  satisfied; FND-055 closed; no new finding. Progress without closure on FND-007 and FND-064
  (weekly hand review of planner and GDT logs now every week), FND-054, FND-062 and FND-063
  (workstation and router fixes confirmed by the 2026-10-24 rescan); FND-019 recurred on
  2026-10-14 [[ART-SAR]].
- **POA&M:** POAM-055 completed; progress or recurrence noted on POAM-007, POAM-019, POAM-032,
  POAM-054, POAM-062, POAM-063, POAM-064 and POAM-067; no item added and no date moved
  [[ART-POAM]].
- **Trend baseline:** with one cycle there is no trend yet; the next report shows open items by
  root cause and severity against these figures [[INT-114.A1]].

## Risks and planned responses

No new risk; every risk keeps the response `mitigate` [[ART-RA]] [[INT-112.A1]].

- RSK-001 (shared accounts, moderate): release 2.4 per-maintainer accounts fielded by
  2027-03-31; named custodian and new GDT administrator password by 2026-11-30 [[ART-POAM]].
- RSK-002 (local-only logs, moderate): interim weekly hand review now running; release 2.4
  forwarding by 2027-03-31 [[ART-POAM]].
- RSK-003 (GDT and planner flaws, moderate): GDT firmware 5.2.1 in the 2026-12 bundle and a
  rescan by 2027-01-15. The PM delayed the fix to that bundle while 5.2.1 is in regression
  testing, coordinated with the requirements sponsor's representative, the AODR and the CSSP;
  the GDT service stays reachable only from the station internal network. The planner library
  flaws stay under the AO's risk acceptance [[INT-113.A1]].
- RSK-006 (planner end of support, low/high): replacement selected by 2027-01-29, fielded by
  2027-06-30 under the requested extension [[ART-RA]] [[ART-POAM]].

## Matters for ongoing authorization

No ongoing authorization trigger in `conmon.yaml` was reached in the cycle: no significant
change, no new critical vulnerability, no late high-risk item, no incident, no lost or captured
kit and no threat change [[ART-CONMON]] [[INT-114.A2]]. For the AO's attention:

- Conditions due next: named custodian, GDT administrator password and log export (2026-11-30);
  IC-1 agreement and privacy threshold analysis (2026-12-15) [[INT-114.A2]].
- The delayed GDT firmware fix (2026-12 bundle) [[INT-113.A1]].
- The planner replacement selection (2027-01-29); a slip will be reported as a change in risk
  without waiting for the next quarterly report [[INT-114.A2]] [[INT-113.A2]].
