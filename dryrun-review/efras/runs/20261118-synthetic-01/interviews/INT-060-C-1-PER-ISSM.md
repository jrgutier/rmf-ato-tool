---
interview_id: INT-060
run_id: 20261118-synthetic-01
task: C-1
persona: PER-ISSM
date: 2026-11-18
topics: [leveraged authorizations, service agreements, CSSP alignment, privileged users, user access requirements, interconnection agreements]
---
# INT-060 — C-1 — PER-ISSM

### Q1 {#INT-060.Q1}
Asked of: PER-ISSM · Task: C-1
Which providers' authorizations does the system leverage, how does it inherit from each, and
under which agreement?
**A1 {#INT-060.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[ART-ORG-CONTEXT]] [[INT-013.A1]]
> Four, the same four the Component designated as common control providers at P-5. The cloud
> region (DoD provisional authorization IL4, 2024-09-18) is a commercial offering, so it is an
> external service under the Component's enterprise cloud contract, which carries the DoD
> security requirements. The access point (ATO 2025-01-10), the software factory (ATO
> 2025-10-01) and the CSSP (service agreement of 2026-04-01 under the CSSP's own authorization)
> are DoD services, each under a service-level agreement; the access point and CSSP agreements
> are Component enterprise agreements, the factory's is the factory's standard tenant SLA. We
> inherit from each as an approved common control provider; none is an Enterprise system
> boarded through the DSAWG. The identity broker and the two source systems are systems we
> exchange data with, not authorizations we inherit controls from.

### Q2 {#INT-060.Q2}
Asked of: PER-ISSM · Task: C-1
Which NOSC and CSSP is the system aligned to, and how is that recorded?
**A2 {#INT-060.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#environment]] [[ART-ORG-CONTEXT]]
> EFRAS is a GENSER system aligned to the Component's network operations and security center
> and to ECSSP as its CSSP. ECSSP offers GENSER services as authorized by USCYBERCOM after the
> DISA evaluation. The alignment is recorded in the Component's CSSP alignment register, the
> CSSP section of our eMASS record, with mission criticality "mission support" (not mission
> critical). The production account's private address range is 10.44.0.0/16 (fictional); it
> has no public addresses. The parts we operate sit in the provider's IL4 region and the ERST
> workstations are in the program's office space.

### Q3 {#INT-060.Q3}
Asked of: PER-ISSM · Task: C-1
What is the CSSP service agreement, and who approved and checked it?
**A3 {#INT-060.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#logging]]
> The ECSSP–ARSPO service agreement (fictional reference ECSSP-SA-ARSPO-01) took effect on
> 2026-04-01 and the AO approved it. It covers 24x7 monitoring of the logs we forward,
> incident response support and vulnerability alerts, for the cloud environment. I checked its
> roles, responsibilities, scope and applicability against our boundary on 2026-04-01. ECSSP
> was evaluated against the CSSP evaluator scoring metrics and authorized by USCYBERCOM; the
> date of that evaluation is on ECSSP's own record, which I have not seen.

### Q4 {#INT-060.Q4}
Asked of: PER-ISSM · Task: C-1
Who holds privileged access, are they qualified, and have they signed for it?
**A4 {#INT-060.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]] [[INT-055.A1]]
> Three privileged groups: the four application administrators (`app-admin`), the six ERST cloud
> operations engineers (named console roles), and the ISSO and me with the `auditor` role. The
> data scientists are privileged only inside the analytics sandbox. Every one of them holds the
> DoD 8140 qualification for their work role and has signed the privileged access agreement,
> our Statement of Acceptance of Responsibilities, before provisioning. The two break-glass
> console accounts are not a user group: they are sealed and used only by the cloud operations
> engineers when the broker is down.

### Q5 {#INT-060.Q5}
Asked of: PER-ISSM · Task: C-1
What clearance and citizenship do users need?
**A5 {#INT-060.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/conops.md#users]]
> No clearance: the system holds no classified information. Every user needs a CAC, which means
> a favorable background investigation, and U.S. citizenship; privileged users need the
> investigation for their privileged IT position. CUI training and the annual cyber awareness
> and privacy training are required before any account is provisioned.

### Q6 {#INT-060.Q6}
Asked of: PER-ISSM · Task: C-1
What do you hold on the interconnected systems' authorizations and the EMIS interim approval?
**A6 {#INT-060.A6}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/conops.md#limitations]] [[INT-058.A6]]
> I hold the ATO letters. EMIS and the supply status service are authorized by the Naval
> Aviation Systems AO's peer for maintenance and supply systems, whom I can name only by role:
> the maintenance and supply systems AO (fictional role label). The identity broker is authorized
> by the Component enterprise services AO (fictional role label). The EMIS ISSM's interim e-mail
> approval is dated 2026-09-15; it is not an agreement in the sense of the MOA and has no
> signature block. All three connections use HTTPS on 443 through our egress allow-list and the
> cloud provider's network; none crosses a security domain.

### Q7 {#INT-060.Q7}
Asked of: PER-ISSM · Task: C-1
The organization's list of external entities in a risk relationship names the cloud provider
as "Example GovCloud" and leaves out the cloud access point. Is the access point such a
relationship, and who accepted its risk?
**A7 {#INT-060.A7}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-013.A2]] [[INT-004.A4]]
> Yes. The access point is a DoD enterprise service we depend on for every user connection and
> inherit boundary protection from, so it is an actual relationship. It was left off the list by
> oversight. The AO accepted its ongoing risk together with the inheritance of its common
> controls, on the strength of its ATO of 2025-01-10, as for the other providers. The cloud
> entity is the Example GovCloud IL4 region offering, the name the common control record uses;
> one name should be used everywhere.
