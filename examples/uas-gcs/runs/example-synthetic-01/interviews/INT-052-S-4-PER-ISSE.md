---
interview_id: INT-052
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [sa family, life cycle, acquisition, engineering principles, external services, developer CM and testing]
---
# INT-052 — S-4 — PER-ISSE

### Q1 {#INT-052.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: sa-1, sa-2, sa-3, sa-3.1, sa-3.2, sa-3.3, sa-22
How are security resources, the development life cycle, test environments and technology refresh managed?

**A1 {#INT-052.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]] [[product/conops.md#limitations]]
> Acquisition policy comes from the Component. The program's budget carries a cybersecurity
> line for the RMF work, scanning tools and the integrator's security tasks. The integrator
> follows the program's development life cycle under the acquisition pathway, with security
> reviews at each design review and release, and with me and the ISSM named in it. The six
> pre-production stations at the test range are the preproduction environment: they connect
> only to a test instance of the brigade network and carry the same baseline. Tests use
> synthetic routes, test keys and range imagery, never operational mission data. Refresh is
> the open item: the mission planner's vendor ends support for version 7 in 2027-06 and the
> program has not chosen a replacement yet; it is being evaluated for release 3.0. Every
> other component is supported today.

### Q2 {#INT-052.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: sa-4, sa-4.1, sa-4.2, sa-4.7, sa-4.9, sa-4.10, sa-4.11, sa-4.12, sa-5, sa-9, sa-9.1, sa-9.2, sa-9.3, sa-9.6, sa-9.8
What does the contract require, what documentation exists, and how are external services handled?

**A2 {#INT-052.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]] [[product/architecture.md#network]] [[product/architecture.md#configuration]]
> The integrator's contract carries the security requirements allocated in P-17: the
> functional properties of the controls, design and implementation documentation for them,
> the list of functions, ports, protocols and services, use of products from the NIAP list
> where a protection profile exists for that product type, CAC readers from the approved
> products list, and government ownership of all mission and security data. The integrator
> delivers administrator and user guides and the STIG summary. For the mission planner there
> is no vendor security guide; the integrator's hand-hardening settings are recorded but not
> yet assessed. The only external service is the Brigade Tactical Network Enclave, used under
> its authorization through the enclave connection approval process, with the ports it uses
> documented in the router rules. The enclave is a DoD system in U.S. jurisdiction. The
> aircraft link keys are generated and loaded by the unit, never by a provider.

### Q3 {#INT-052.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: sa-8, sa-8.14, sa-8.22, sa-8.28, sa-8.33, sa-10, sa-10.1, sa-10.3, sa-10.7, sa-11, sa-11.1, sa-15, sa-15.3, sa-21
Which engineering principles apply, and how does the integrator control and test what it builds?

**A3 {#INT-052.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#physical]] [[product/test-results.md#dt-1]] [[product/conops.md#limitations]] [[INT-049.A3]]
> I apply the SP 800-160 principles at each design review: least privilege through the three
> directory roles and separate privileged accounts, minimization so the station holds only user
> names as personal data, and acceptable security judged against the risk assessment.
> Accountability is the gap: the shared gcsmaint account means maintenance actions cannot be
> tied to a person until per-maintainer accounts arrive in release 2.4 (2027-02). The
> integrator keeps the source and the baseline under its own configuration management, with
> my seat on its change board feeding the program CCB. Bundles are signed and the station
> checks the signature; hardware arrives with tamper seals checked at receipt and at each
> setup. The integrator runs static code analysis on the flight control and video
> applications at each build, and developer testing plus DT-1 cover the station; the
> planner's hardening has never been assessed. The integrator's staff are screened to the
> station roles under the contract, and a criticality analysis is part of each design review.
