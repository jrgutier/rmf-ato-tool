---
interview_id: INT-020
run_id: agent-skeleton
task: A-2
persona: PER-SCA
date: 2026-10-29
topics: [assessment methods, reuse of test results, independence, schedule, rules of engagement]
---
# INT-020 — A-2 — PER-SCA

### Q1 {#INT-020.Q1}
Asked of: PER-SCA · Task: A-2
**A1 {#INT-020.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[ART-BASELINE]]
> The whole tailored baseline is in scope: all six controls, ac-2, au-2, cm-6, ia-2, sc-7 and
> si-2, with no exclusion. Each is assessed against every SP 800-53A objective of the control,
> including the tailored parameter values. For the three hybrid controls (au-2, ia-2, sc-7) we
> assess the ESG part ourselves and examine the provider's authorization and agreement for the
> inherited part; we do not reassess the enclave, ICAM or the CSSP.

### Q2 {#INT-020.Q2}
Asked of: PER-SCA · Task: A-2
**A2 {#INT-020.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[product/test-results.md#top]]
> Methods per control: ac-2 examine (account list, access request records, the 2026-09-12 review
> record), interview (ISSO) and test (sign-in with the shared and break-glass accounts on a test
> unit). au-2 examine (event list and CSSP agreement), interview (ISSO, CSSP) and test (generate
> events and confirm they reach the SIEM). cm-6 examine (baseline, STIG summary and deviations)
> and test (witnessed SRG/STIG scan). ia-2 examine (federation settings), interview (ISSE) and test
> (PKI sign-in and maintenance-port sign-in). sc-7 examine (firewall rules) and test (port scan
> from both interfaces). si-2 examine (bundle level per unit, scan reports, board minutes),
> interview (ISSO, developer) and test (credentialed vulnerability scan). Depth is focused and
> coverage is representative: all twelve pre-production units for scans, two units for manual
> tests.

### Q3 {#INT-020.Q3}
Asked of: PER-SCA · Task: A-2
**A3 {#INT-020.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#config-scan]] [[product/test-results.md#vuln-scan]] [[product/test-results.md#account-review]]
> We reuse the DT-2 results (2026-08-18 to 2026-08-29) for ia-2 sign-in, au-2 event delivery and
> sc-7 port scans, because DT-2 ran on the same twelve pre-production units with documented test
> cases; we re-run one PKI sign-in and one port scan ourselves to confirm them. The 2026-09-30
> configuration scan was witnessed by an assessor, so we accept it for cm-6. The 2026-09-30
> vulnerability scan and the 2026-09-12 account review are program records: we examine them, but
> we repeat the vulnerability scan because si-2 rests on it. Reused results support a
> determination; they never replace our own test of a disclosed gap.

### Q4 {#INT-020.Q4}
Asked of: PER-SCA · Task: A-2
**A4 {#INT-020.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-STAKE]]
> The assessment is done by the Component assessment team under the CISO's delegation of the SCA
> role. I lead it; a second assessor runs the scans. Neither of us reports to RSSPO or ESIT, and
> neither designed or operates any ESG control, so the team is independent of the program.

### Q5 {#INT-020.Q5}
Asked of: PER-SCA · Task: A-2
**A5 {#INT-020.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> Schedule: kickoff on 2026-11-02; document examination and interviews on 2026-11-03 to
> 2026-11-06; scans and manual tests on 2026-11-09 to 2026-11-12; out-brief on 2026-11-20, with
> the draft SAR on the same day.

### Q6 {#INT-020.Q6}
Asked of: PER-SCA · Task: A-2
**A6 {#INT-020.A6}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]] [[product/conops.md#environment]]
> Rules of engagement: all testing is on the pre-production units at the test sites, which feed
> only the test instance of IODS; no testing on live networks or operational traffic. Scans run
> from the assessor laptop on the site switch port the enclave assigns, and from the maintenance
> port only with the field technician present. No denial-of-service or exploit testing.
> The ISSO and the enclave operations desk are told 48 hours before each scan, and the ISSO can
> stop any test that affects a unit. Findings are reported to the ISSM and the AODR, not fixed
> during the assessment.
