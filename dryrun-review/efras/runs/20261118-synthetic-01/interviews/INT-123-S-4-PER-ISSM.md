---
interview_id: INT-123
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-11-18
topics: [SecCM tools and records, break-glass bypass, plan structure and review schedule, C-SCRM plan, telework, E-Authentication]
---
# INT-123 — S-4 — PER-ISSM

### Q1 {#INT-123.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: cm-2, cm-6 (configuration management plan)
Which tools monitor configuration, are they SCAP-validated, how are false positives handled, what can no tool reach, and which records are kept for how long?
**A1 {#INT-123.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-093.A1]] [[INT-094.A1]] [[product/test-results.md#stig-scan]] [[product/architecture.md#configuration]]
> The STIG and SRG compliance scanner the SCA witnessed on 2026-10-22 is a SCAP-validated
> scanner run from the Component's enterprise scanning service against the nodes and the
> database. The hourly drift scan compares the deployed account with the templates; no SCAP
> validation exists for that kind of tool, and its false positives (provider-managed tags,
> autoscaling) are suppressed by a reviewed allow-list the ISSE keeps in the repository. The
> software factory's image and dependency scanners have no SCAP validation either; their
> false positives are marked in the factory with a justification the ISSO approves. What no
> tool reaches inside our account: the managed notebook service of the sandbox (INV-014)
> exposes no scan interface, so the ISSO reviews its settings by hand monthly against the
> templates; the managed load balancer and WAF (INV-001) are checked by the drift scan only, and
> the WAF rule set is reviewed by hand at each release. Records: change requests, impact
> analyses, board minutes, approved baselines and scan results are kept in the repository and
> the issue tracker for the life of the system plus one year, access limited to the program,
> and deleted under the Component records schedule after that.

### Q2 {#INT-123.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: ia-2, ac-2 (bypass of a cybersecurity mechanism)
Is any cybersecurity mechanism bypassed by procedure, and who coordinated and approved it?
**A2 {#INT-123.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-097.A1]] [[product/conops.md#limitations]] [[product/architecture.md#identity]]
> Yes, one: the two sealed break-glass console accounts sign in with a FIDO2 key instead of
> CAC through the identity broker, used only when the broker is down. The procedure (two
> people unseal, the on-call engineer and the ISSO are paged, every action is logged, the key
> is resealed and the use reviewed the next working day) was written with the ISSO, and I
> approved it in writing today, 2026-11-18. The deviation from CAC still goes to the AO with
> the package.

### Q3 {#INT-123.Q3}
Asked of: PER-ISSM · Task: S-4 · Control focus: pl-2
Are the security, privacy and C-SCRM plans kept together, how detailed is each element, and how often are the plans reviewed?
**A3 {#INT-123.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-103.A1]] [[product/stakeholders.md#governance]]
> One consolidated plan: ART-SSP with its family files holds the security plan, the privacy
> plan and the C-SCRM plan as sections and records, because one small team maintains all three
> and the controls overlap (PT and RA-8 with the PIA, SR with SA-11). Common elements — the
> system description, boundary, inventory, roles and the open items — exist once and the other
> plans point to them. Detail: one statement per control with components, parameters and
> evidence; the plan records hold the values a reviewer checks. The plans are reviewed annually
> and with each major release, per the tailored PL-2 value and the Component RMF policy.

### Q4 {#INT-123.Q4}
Asked of: PER-ISSM · Task: S-4 · Control focus: sr-3, sr-11, sa-9 (system C-SCRM plan)
How are the suppliers watched after award, who approved the C-SCRM plan, and who must hear of an urgent supply chain threat?
**A4 {#INT-123.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-110.A1]] [[INT-116.A1]] [[INT-039.A2]] [[INT-053.A1]]
> The two critical suppliers are watched after award: ERST through its monthly deliverables,
> the per-release attestation and the factory's gate results; the cloud region through its
> customer responsibility matrix, its monthly continuous monitoring deliverables in eMASS and
> its provisional authorization status. Each is checked for compliance with the contract,
> effectiveness of what it delivers, and change (ownership, key staff, a new sub-provider, a
> lost authorization), at least annually and on any trigger. The two open-source projects and
> the software factory are watched through the factory's scanners and advisories. Both
> critical suppliers take part in our contingency, incident response, recovery and their
> tests. I drafted the plan with the Component C-SCRM program office (it is matrixed), which
> coordinated it, and the PM approved it on 2026-11-18. A report goes to the PM and the AO quarterly; an urgent
> mission threat we cannot address goes at once to the MDA, the AO and, through the Component
> CIO, to the DoD CIO.

### Q5 {#INT-123.Q5}
Asked of: PER-ISSM · Task: S-4 · Control focus: ac-17, ia-2
Do users reach EFRAS from non-government equipment, and was an E-Authentication risk assessment performed?
**A5 {#INT-123.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> No telework from non-government equipment: every user signs in with CAC over NIPRNet from a
> government-furnished workstation, and engineers use government privileged access
> workstations. No separate E-Authentication risk assessment was performed: every user
> authenticates with CAC at the enterprise identity broker, so the assurance level is set by
> the enterprise service, not by EFRAS.
