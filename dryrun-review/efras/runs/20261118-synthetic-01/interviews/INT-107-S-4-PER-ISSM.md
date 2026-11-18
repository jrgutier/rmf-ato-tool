---
interview_id: INT-107
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-11-18
topics: [system risk assessment upkeep, vulnerability scanning and remediation times]
---
# INT-107 — S-4 — PER-ISSM

### Q1 {#INT-107.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: ra-3
Where are the risk assessment results documented, who receives them, and how often are they reviewed and updated?
**A1 {#INT-107.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[ART-ORG-CONTEXT]] [[INT-037.A1]]
> The system risk assessment report, ART-RA, written at P-14. It covers threats, vulnerabilities,
> likelihood and impact, and the privacy risk to individuals, and it takes the Component's risk
> frame and the organizational risk assessment as inputs. I review the results at least
> annually and at each major release, and update the report at R-2 with the assessment findings,
> after a significant change to the system or its environment, after a significant change in
> threat, and at least annually. It goes to the AO, the AODR, the product manager and the
> privacy representative, under CUI rules.

### Q2 {#INT-107.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: ra-5
How often is EFRAS scanned, with what, how fast are findings fixed, and who hears about them?
**A2 {#INT-107.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#stig-scan]] [[product/conops.md#limitations]] [[INT-072.A1]]
> Inside the account we scan weekly: an authenticated scan of the worker nodes and the
> database against the STIGs and the vulnerability feeds, using SCAP content, CVE and CVSS. Every
> pipeline build runs the dependency and image scans, and we rescan when the CSSP or the
> software factory alerts us to a new vulnerability. The scanners pull new signatures daily. The
> ERST engineers and I analyze the results; critical and high findings are due within 30 days,
> moderate within 90 and low within 180, from discovery. The two high findings in the
> report-rendering image, found on 2026-10-20, miss that: the fix waits on the factory's base
> image and ships in 1.5.2 on 2026-12-10. Results go to the ISSO, the CSSP and the software
> factory, which shares base image findings with its other tenants.
