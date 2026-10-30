---
interview_id: INT-111
run_id: example-synthetic-01
task: M-2
persona: PER-ISSO
date: 2026-10-29
topics: [boundary rules, flaw remediation, monitoring coverage, kit seal checks]
---
# INT-111 — M-2 — PER-ISSO

### Q1 {#INT-111.Q1}
Asked of: PER-ISSO · Task: M-2 · Control focus: sc-4, sc-5, sc-7, sc-23.3, sc-39
Did the router rule set, host firewall and session settings hold through the cycle, and where does the GDT management service stand?

**A1 {#INT-111.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-10.md#config-checks]] [[product/monitoring/cycle-2026-10.md#stig-scan]] [[product/monitoring/cycle-2026-10.md#vuln-scan]]
> The start-up and pre-upload checks showed no drift on the router or the workstation image at
> any of the 41 start-ups and 37 uploads, apart from the etgcs-p3-ws screen-lock setting, so the
> rule set and host firewall policy stayed as approved. The witnessed STIG scan on 2026-10-24
> after the 2026-10 bundle found the image and router at baseline with only the known deviations.
> The GDT management web service is still vulnerable at firmware 5.1.8 on all six stations and
> still reachable only from the station internal network; 5.2.1 waits for the 2026-12 bundle.

### Q2 {#INT-111.Q2}
Asked of: PER-ISSO · Task: M-2 · Control focus: si-2, si-2.2, si-3, si-4, si-4.14, si-4.19, si-16
What do the bundle level, malware protection and monitoring records show for the cycle?

**A2 {#INT-111.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-10.md#config-checks]] [[product/monitoring/cycle-2026-10.md#stig-scan]] [[product/monitoring/cycle-2026-10.md#vuln-scan]] [[product/monitoring/cycle-2026-10.md#log-reviews]] [[product/monitoring/cycle-2026-10.md#account-review]]
> The 2026-10 bundle is installed on all six stations and the start-up check shows that level
> on every one; the 2026-10-24 rescan confirmed the three medium workstation and router fixes.
> The STIG scan shows malware protection and the memory protections at baseline. The GDT
> web service vulnerability and the two planner library findings are still open. GDT and planner
> logs still stay on the stations; I looked at them by hand in each weekly review, but that only
> covers the six test-range stations and nothing correlates them. The weekly review now ran every
> week, yet gcsmaint is still shared by five maintainers, so the 2026-10-14 change on etgcs-p3-ws
> could not be tied to a person.

### Q3 {#INT-111.Q3}
Asked of: PER-ISSO · Task: M-2 · Control focus: pe-3, pe-6, pe-16
What did the tamper-seal and kit checks show at the setups in the cycle?

**A3 {#INT-111.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-10.md#incidents]]
> The setup log has a seal and kit inventory check at all 22 kit setups in the cycle, with no
> exception recorded, so there was nothing to report to the CSSP.
