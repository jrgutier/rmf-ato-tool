---
interview_id: INT-159
run_id: 20261118-synthetic-01
task: A-3
persona: PER-PM
date: 2026-11-20
topics: [information exchange agreements, EMIS memorandum, program response to weaknesses]
---
# INT-159 — A-3 — PER-PM

### Q1 {#INT-159.Q1}
Asked of: PER-PM · Task: A-3 · Control focus: ca-3
Show me the agreement for each of the three exchanges and say where the EMIS memorandum stands.
**A1 {#INT-159.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/conops.md#limitations]] [[ASM-016]]
> The supply status service agreement of 2026-06-30 and the identity broker's onboarding
> approval of 2026-05-12 are signed; each names the interface, the security requirements, the
> responsibilities and the impact level, and the supply agreement has a privacy paragraph saying
> no PII is exchanged. The EMIS memorandum is still with legal; the connection runs on the EMIS
> ISSM's interim e-mail of 2026-09-15, which names the nightly signed extract over mutual TLS but
> says nothing of privacy requirements, breach notification or each side's responsibilities. We
> target signature by 2026-12-31. Agreements are reviewed annually and on an interface change;
> none has reached its first annual review yet.

### Q2 {#INT-159.Q2}
Asked of: PER-PM · Task: A-3 · Control focus: ca-5, ca-7
How will the program respond to the weaknesses found, and when does the POA&M exist?
**A2 {#INT-159.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[ART-SSP]]
> Every finding goes into the POA&M the ISSM builds after the report, with the fix release dates
> we already hold: 1.5.2 on 2026-12-10, 1.6 on 2027-01-15, the failover test in 2027-02 and the
> EMIS signature by 2026-12-31. The first monitoring cycle and its reports start after the
> decision.
