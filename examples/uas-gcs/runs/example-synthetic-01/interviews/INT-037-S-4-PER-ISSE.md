---
interview_id: INT-037
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [ac family, access enforcement, flow control, remote and wireless access]
---
# INT-037 — S-4 — PER-ISSE

### Q1 {#INT-037.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-3, ac-3.4, ac-5, ac-6, ac-6.1, ac-6.2, ac-6.5, ac-6.8, ac-6.10
How do the components enforce access and least privilege?

**A1 {#INT-037.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#users]]
> The workstation image maps the directory groups to OS and application roles: operators fly
> and plan, the commander approves plans and releases products, admins and maintainers change
> configuration. Applications run as standard users; only the `admin` role and `gcsmaint` hold
> local administrator rights, and admins use a separate non-privileged sign-in for routine work.
> Operators cannot run privileged tools; OS file permissions protect mission data. The router
> and the GDT accept configuration only from their administrator accounts.

### Q2 {#INT-037.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-4, ac-3.9, ac-17, ac-17.1, ac-17.2, ac-17.3, ac-17.4, ac-17.6, ac-17.9, ac-21
How are information flows and remote access controlled?

**A2 {#INT-037.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> The router denies everything except outbound TLS to the intelligence system's product drop,
> syslog over TLS, LDAPS, and inbound remote administration over SSH from the brigade S6
> management subnet only; there is no IP route from the aircraft link to the uplink. Remote
> administration needs the `admin` role, is logged by the router, and S6 or the platoon can drop
> it by disabling the uplink port. Products leave only after the mission commander releases
> them. The router configuration is not published outside the program.

### Q3 {#INT-037.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-7, ac-8, ac-10, ac-11, ac-11.1, ac-12, ac-12.1, ac-12.2, ac-2.5, ac-14
What do the sign-in and session settings enforce?

**A3 {#INT-037.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-1]]
> Three failed sign-ins lock a local account for 15 minutes on the workstation, router and GDT;
> the workstation screen locks after 15 minutes idle behind a blank pattern-hiding screen, and
> idle router and GDT management sessions end after 15 minutes. The workstation allows one
> interactive session per user; users can sign out at any time and are told when a session
> ends. All three show the DoD consent banner before sign-in. Without sign-in the station only
> keeps the aircraft on its lost-link route; no user action is possible.

### Q4 {#INT-037.Q4}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-16, ac-16.3, ac-16.6, ac-16.7, ac-18, ac-18.1, ac-18.3, ac-18.4, ac-19, ac-19.5, ac-20, ac-20.1, ac-20.2, ac-20.3, ac-22, ac-23, ac-3.14
What about markings, wireless, mobile use, external systems and public content?

**A4 {#INT-037.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#physical]] [[product/conops.md#information]]
> The video application stamps the handling marking on every clip and still and keeps it when
> products are exported; the intelligence system reads the same marking scheme. The only radio
> is the GDT-aircraft link, encrypted with keys loaded before each mission, and users cannot
> change its settings; workstation Wi-Fi and Bluetooth are disabled in firmware and the GDT has
> no other radio. The laptop disk is fully encrypted. The station connects only to the enclave
> and the intelligence system; only platoon-controlled removable media are used and personal
> devices are prohibited. ETGCS publishes nothing publicly, holds no data store open to search
> by outsiders, and keeps no personal data beyond account names.
