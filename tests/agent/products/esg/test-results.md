# ESG developer and developmental test results {#top}

> **FICTIONAL.** Invented for testing the `rmf` tool; no real test is described.

Results the program offers the assessor for reuse (DoDI 8510.01 Task A-3 asks assessors to
reuse developer and developmental test results). Test events ran on the twelve pre-production
units at the test sites.

## Developmental test event DT-2 (2026-08-18 to 2026-08-29) {#dt-2}

| Test | Result |
|---|---|
| Sign-in through the identity service with DoD PKI for `admin` and `auditor` roles | pass; users without an approved group claim were refused |
| Local sign-in lockout after 5 failures | pass |
| Session lock after 15 minutes idle | pass |
| Audit events for sign-in, account change, configuration change and update installation reach the SIEM within 1 minute | pass (12 of 12 units) |
| Host firewall: port scan from the installation network and from the maintenance port | pass; only the documented ports answered; no routing between ports |
| Collector rejects messages from an unpaired sensor node | pass |
| Buffer replay after a 6-hour IODS outage | pass; no loss, oldest first |

## Configuration compliance scan (2026-09-30) {#config-scan}

The nightly configuration check and an assessor-witnessed SRG/STIG scan of 12 units found the
approved baseline in place on all units, with the deviations listed in the program's STIG
summary. No unit drifted from its approved baseline during August and September 2026.

## Vulnerability scan (2026-09-30) {#vuln-scan}

- 10 of 12 units ran the 2026-09 update bundle.
- 2 units (`esg-north-01`, `esg-ridge-01`) ran the 2026-07 bundle, 63 days old at scan time,
  because their quarterly site visit had not yet happened. On those two units the scan
  reported 4 vulnerabilities rated high and 9 rated medium, all fixed in later bundles.
- No vulnerability was found on the 10 current units.

## Account review record (2026-09-12) {#account-review}

The ISSO's quarterly review compared the console account list with the access request
records: 3 administrator and 2 auditor identity-service accounts, all approved; 1 break-glass
account (`esgadmin`, unused since 2026-06); 1 shared local account (`fieldtech`) used by the
10 field technicians. The review noted that `fieldtech` sign-ins cannot be attributed to a
person and referred it to the program office (see `conops.md#limitations`).
