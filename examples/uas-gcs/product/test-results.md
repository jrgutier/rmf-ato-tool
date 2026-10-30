# ETGCS developer and developmental test results {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real test is described.

Results the program offers the assessor for reuse (DoDI 8510.01 Task A-3 asks assessors to
reuse developer and developmental test results). Events ran on the six pre-production
stations at the fictional test range.

## Developmental test event DT-1 (2026-07-13 to 2026-07-24) {#dt-1}

| Test | Result |
|---|---|
| CAC sign-in against the brigade directory for `operator`, `commander`, `admin` | pass; users outside the approved groups were refused |
| Cached CAC sign-in after 7 days disconnected | pass |
| Local account lockout after 3 failures; screen lock after 15 minutes | pass |
| Aircraft link: commands from an unkeyed terminal rejected | pass |
| Lost-link: aircraft returns on its pre-loaded route when the link drops | pass (6 of 6 flights) |
| Router: port scan from the uplink and the station network | pass; only documented ports answered |
| Audit events reach the enclave collector after reconnect | pass for workstation and router; planner and GDT logs are not forwarded (by design today) |

## STIG compliance scan (2026-09-15) {#stig-scan}

An SCA-witnessed scan of all six stations: workstation image (Windows STIG) and router
(network device STIG) at the approved baseline with the deviations in the STIG summary. The
mission planner has no STIG; the scan did not cover it (see `conops.md#limitations`).

## Vulnerability scan (2026-09-15) {#vuln-scan}

- Workstation and router: no high or critical findings; 3 medium findings with fixes in the
  2026-10 bundle.
- Ground data terminal: the management web service vulnerability fixed by firmware 5.2.1
  (vendor rating high; reachable only from the station internal network).
- Mission planner: 2 medium findings in a bundled library; the vendor has no fix date.

## Account review record (2026-09-08) {#account-review}

The ISSO's quarterly review of the six test stations: 14 CAC accounts, all approved; 6 sealed
break-glass accounts, none used; 1 shared `gcsmaint` account on each workstation and router,
used by 5 maintainers. The review noted that `gcsmaint` actions cannot be tied to a person and
referred it to the program office (see `conops.md#limitations`).
