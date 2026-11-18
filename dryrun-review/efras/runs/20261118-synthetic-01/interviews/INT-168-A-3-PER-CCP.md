---
interview_id: INT-168
run_id: 20261118-synthetic-01
task: A-3
persona: PER-CCP
date: 2026-11-20
topics: [physical access and media sanitization in the provider package, managed service patching]
---
# INT-168 — A-3 — PER-CCP

### Q1 {#INT-168.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: pe-3, mp-6
What in your package shows physical access control and media sanitization are in force for the region EFRAS uses?
**A1 {#INT-168.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#physical]] [[ART-SVCA]]
> The customer responsibility matrix under LA-01 assigns pe-3 and mp-6 wholly to us. Our IL4
> security plan and the third-party assessment report behind the 2024-09-18 authorization assess
> both with no open item, and the October monthly deliverable reports no change. The program has
> no hardware and no media in our facilities, so there is nothing for the customer to do beyond
> deleting its stores at decommission.

### Q2 {#INT-168.Q2}
Asked of: PER-CCP · Task: A-3 · Control focus: si-2
How is the managed services' patching shown to the program?
**A2 {#INT-168.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#leveraged]]
> We patch the hypervisor, the Kubernetes control plane and the database engine in announced
> windows, and the monthly deliverable lists what was applied and any late item; October listed
> none late. The hardened node image is published monthly. The application images are the
> program's and the software factory's, not ours.
