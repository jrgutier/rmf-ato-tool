---
interview_id: INT-073
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [ca cm cp assessment evidence, compliance check, inventory, backups, contingency plan]
---
# INT-073 — A-3 — PER-ISSO

### Q1 {#INT-073.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ca-7, ca-7.1, ca-7.3, ca-7.4, ca-7.5, ca-7.6
What monitoring runs on the stations today, and what records show it?

**A1 {#INT-073.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#logging]] [[product/test-results.md#dt-1]]
> The start-up and pre-upload compliance check runs and logs drift on every station; I can show
> its log on station 3. The enclave reviews forwarded workstation and router records daily.
> The system-level monitoring strategy is written, but none of its activities have run yet:
> no independent ongoing assessment, no trend analysis, no effectiveness or change metrics,
> no dashboard. They start with the first monitoring cycle after authorization. Planner and
> GDT logs are still not forwarded, so nothing monitors them.

### Q2 {#INT-073.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: cm-2, cm-2.2, cm-2.3, cm-6.1, cm-8, cm-8.1, cm-8.2, cm-8.3, cm-12, cm-12.1
Show the baseline, the drift check and the inventory on a station.

**A2 {#INT-073.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/hw-sw-inventory.md#items]] [[product/test-results.md#stig-scan]]
> All six test stations run release 2.3.0. On station 3 the compliance check compared the
> image to the 2.3.0 baseline at start-up and logged no drift; a test setting I changed was
> reported as drift at the next start-up. The installer's version record matches the
> inventory, with GDT firmware 5.1.8. A USB device not in the inventory was blocked and
> logged, and a test mission file outside the mission folders was reported. The integrator
> holds the 2.2.x and 2.3.0 baselines for rollback. Router settings were checked by the
> 2026-09-15 scan.

### Q3 {#INT-073.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: cm-5, cm-5.1, cm-5.5
Who can change configuration, and can each change be tied to a person?

**A3 {#INT-073.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/conops.md#limitations]]
> Only the admin role, maintainers and the GDT vendor administrator account can change
> settings; a standard user's attempt was refused. Changes are logged, but the ones made
> under the shared `gcsmaint` account show only that account name, and five maintainers
> share it. The single GDT vendor administrator account is under my password control.

### Q4 {#INT-073.Q4}
Asked of: PER-ISSO · Task: A-3 · Control focus: cp-2, cp-2.1, cp-2.3, cp-2.8, cp-3, cp-4, cp-4.1
Show the contingency plan, its coordination, training records and test results.

**A4 {#INT-073.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]] [[product/test-results.md#dt-1]]
> The plan summary names the strategy, the 4-hour restore on a spare kit, the essential
> functions and the critical assets, and I coordinated it with the brigade continuity plan
> and the enclave incident response plan; the brigade S6 reply is on file. The full plan with
> roles, contacts and step-by-step recovery is not written yet. Nobody has been trained on the
> swap and restore, and the plan has never been tested or exercised; the first tabletop with
> the brigade is still being scheduled. Lost-link return worked on 6 of 6 DT-1 flights.

### Q5 {#INT-073.Q5}
Asked of: PER-ISSO · Task: A-3 · Control focus: cp-6, cp-6.1, cp-6.3, cp-7, cp-7.1, cp-7.2, cp-8, cp-8.2, cp-9, cp-9.1, cp-9.5, cp-9.8, cp-10, cp-10.2
Show backup records, the spare kits and a restore.

**A5 {#INT-073.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#network]]
> The backup log shows a backup after the 2.3.0 install and weekly since on all six test
> stations, written encrypted to platoon media, with a copy logged into brigade stock. The two
> spare kits are listed in brigade stock away from the platoon area and reachable by road.
> In September the maintainer reimaged station 5 from the signed bundle and restored its
> latest backup; it was flying the simulator inside 3 hours. During DT-1 an uplink outage
> queued products, which transferred when the link came back. Each station has one GDT and
> one router; a failed one is replaced from the spare kit.
