---
interview_id: INT-023
run_id: example-synthetic-01
task: C-1
persona: PER-IO
date: 2026-10-29
topics: [user groups, privileges, information release]
---
# INT-023 — C-1 — PER-IO

### Q1 {#INT-023.Q1}
Asked of: PER-IO · Task: C-1
**A1 {#INT-023.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> Five groups. Two air vehicle operators and one mission commander per station sign in locally
> with CAC and hold no administrative rights. Field maintainers, about four per platoon, are
> privileged but share the local `gcsmaint` account, so their actions cannot be tied to a person.
> Two brigade S6 administrators per brigade administer stations remotely with CAC. The platoon
> leader holds the sealed break-glass administrator account.

### Q2 {#INT-023.Q2}
Asked of: PER-IO · Task: C-1
**A2 {#INT-023.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/data-flows.md#top]]
> Intelligence analysts are the main consumers of the information but never log in: they
> receive products only on the brigade intelligence system. Information leaves a station only
> when the mission commander releases products over DF-4 to that system; audit records go to the
> enclave log collector over DF-5.
