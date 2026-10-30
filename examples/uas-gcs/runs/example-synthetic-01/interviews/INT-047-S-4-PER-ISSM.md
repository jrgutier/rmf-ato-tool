---
interview_id: INT-047
run_id: example-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-10-29
topics: [pl family, security plan, rules of behavior, architecture, baseline]
---
# INT-047 — S-4 — PER-ISSM

### Q1 {#INT-047.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: pl-1, pl-2, pl-4, pl-4.1, pl-7
What is the state of the security plan, the rules of behavior and the concept of operations?

**A1 {#INT-047.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#top]] [[product/conops.md#users]] [[ART-ORG-CONTEXT]]
> Planning policy comes from the Component cybersecurity program. The security plan is being
> written now in S-4, family by family; it is reviewed and approved in S-6 and then kept up to
> date by the ISSO after each change. Every operator, commander, maintainer and S6
> administrator signs the station rules of behavior, which include the ban on posting mission
> information on social media or external sites, before the ISSO approves their directory group
> or adds them to the maintainer list. The program's concept of operations describes the
> mission, users, environment and limitations and is updated with each release.

### Q2 {#INT-047.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: pl-8, pl-8.1, pl-8.2, pl-9, pl-10, pl-11
How are the architecture, defense in depth, central management and the baseline handled?

**A2 {#INT-047.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#top]] [[product/architecture.md#network]] [[product/architecture.md#leveraged]] [[product/architecture.md#configuration]] [[ART-BASELINE]]
> The integrator's architecture description covers components, boundary, network, identity,
> logging and updates. Protection is layered: the enclave firewall and IDS, the station router
> that denies everything but four flows, the isolated internal segment, CAC sign-in and the
> encrypted disk. Those layers are separate devices under separate administration, but nobody
> has recorded whether they come from different suppliers; the integrator will add the
> supplier of each layer to the architecture before S-6. Accounts come from the brigade
> directory, logs go to the enclave collector, and every station runs the one baseline from the
> signed bundle under the configuration control board. The baseline was selected in S-1 and
> tailored in S-2 and is recorded in ART-BASELINE.
