---
interview_id: INT-091
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [si flaw remediation evidence, malicious code protection, monitoring coverage, alerts]
---
# INT-091 — A-3 — PER-ISSO

### Q1 {#INT-091.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: si-1, si-2, si-2.2, si-2.3, si-2.4, si-2.6, si-5
Show the flaw remediation records: bundle levels per station, fix-to-install times, open flaws and the alerts you handled.

**A1 {#INT-091.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]], [[product/architecture.md#updates]]
> The start-up compliance check log on all six stations shows the 2026-10 bundle installed; that
> bundle carries the fixes for the three workstation and router medium findings, but no rescan has
> run since 2026-09-15. My flaw tracker lists each vendor fix with its release and install dates.
> Still open: the GDT management web service vulnerability (vendor high) waiting for firmware
> 5.2.1 in the 2026-12 bundle, and the planner's two medium library findings with no vendor fix
> date. The CSSP alert log shows each alert assessed; none needed an out-of-cycle bundle this year.
> The installer log shows superseded packages removed and the previous GDT image replaced.
> The Component integrity policy cover page shows a review within the last year.

### Q2 {#INT-091.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: si-3, si-3.10, si-4, si-4.1, si-4.2, si-4.4, si-4.5, si-4.10, si-4.11, si-4.12, si-4.16, si-4.19, si-4.20, si-4.22, si-4.23, si-4.24
Show the malware protection status and the monitoring records: what reaches the collector, the local alerts and your reviews.

**A2 {#INT-091.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]], [[product/test-results.md#dt-1]]
> Real-time protection is on in the STIG scan of every workstation and signatures are at the
> 2026-10 bundle level; one test detection during DT-1 was quarantined, logged and sent to the
> CSSP. The collector holds workstation and router events, including privileged activity and the
> router's inbound, outbound and denied traffic; drift and malware alerts show in the local alert
> log. Planner and GDT logs stay local and are not in the collector. My weekly station report
> exists only for the test-event weeks; between events nobody reviews station activity, and
> gcsmaint actions cannot be tied to a maintainer. CSSP indicators arrive with the signature updates.

### Q3 {#INT-091.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: si-12, si-12.1, si-12.3, si-18, si-18.1, si-18.3, si-18.4, si-18.5
Show retention, sanitization and the source of user names.

**A3 {#INT-091.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]], [[product/conops.md#information]]
> Local logs roll at 90 days by the image setting; product transfers are logged before deletion.
> No station has been retired yet; the Component sanitization procedure is on file. User names
> come from the directory name attribute at each CAC sign-in, and corrections go to the directory owner.
