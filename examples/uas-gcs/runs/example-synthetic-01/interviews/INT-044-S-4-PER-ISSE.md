---
interview_id: INT-044
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [ia family, CAC sign-in, shared maintenance account, device authentication, authenticators]
---
# INT-044 — S-4 — PER-ISSE

### Q1 {#INT-044.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-1, ia-2, ia-2.1, ia-2.2, ia-2.5, ia-2.6, ia-2.8, ia-2.12, ia-4, ia-4.4, ia-4.9, ia-11, ia-12, ia-12.1, ia-12.2, ia-12.3
How are users identified and authenticated on the station, and where does it fall short?

**A1 {#INT-044.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#users]] [[product/conops.md#limitations]] [[product/test-results.md#dt-1]] [[product/test-results.md#account-review]]
> Policy comes from the Component cybersecurity program. Operators, commanders and remote
> administrators sign in to the workstation with their CAC against the brigade directory, which
> the enclave runs; the CAC is a separate PKI device with a PIN, so sign-in is multifactor and
> replay resistant (Kerberos with PKINIT). Identity proofing and identifier issuance happen at
> CAC issuance; the ISSO adds a user to the `operator`, `commander` or `admin` group only on a
> supervisor's signed request, and the directory carries the user's status and attributes.
> Users re-authenticate after the 15-minute screen lock and on privilege elevation. The gaps:
> field maintainers share the local `gcsmaint` account on the workstation and the router with a
> password only, so maintainer actions cannot be tied to a person and privileged maintenance
> is single-factor; the GDT management service has one vendor administrator account with a
> per-station password. Per-maintainer accounts with offline CAC sign-in come in release 2.4
> (planned 2027-02). The sealed break-glass account per station is held by the platoon leader.

### Q2 {#INT-044.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-3, ia-3.1, ia-7, ia-9
How do devices and services authenticate each other?

**A2 {#INT-044.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-1]]
> The workstation authenticates to the brigade directory with its domain machine certificate
> over LDAPS, and the router presents its device certificate for syslog over TLS to the enclave
> collector. The GDT and the aircraft authenticate each other with the link keys loaded before
> each mission; DT-1 showed commands from an unkeyed terminal are rejected. The flight control
> application opens its command session to the GDT only with the mission key. The workstation
> image runs the OS cryptographic modules in FIPS mode, and the CAC middleware and the link
> encryption use the validated modules the vendors document.

### Q3 {#INT-044.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-5, ia-5.1, ia-5.2, ia-5.6, ia-5.7, ia-5.8, ia-5.13, ia-5.14, ia-5.16, ia-6, ia-8, ia-8.1, ia-8.2, ia-8.4
How are authenticators managed, and are there non-organizational users?

**A3 {#INT-044.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#updates]] [[product/conops.md#limitations]] [[product/conops.md#users]]
> CAC certificates are validated against the DoD PKI trust store built into the image and
> updated through the signed quarterly bundle; cached credentials expire after 14 days
> disconnected. Password fields mask input. The integrator's build scan checks that no
> application or script carries an embedded clear-text password. The `gcsmaint` password is
> shared by the platoon's maintainers, changed every 60 days and is the same account on the
> workstation and the router; the GDT vendor administrator password is set once at installation
> and has no change cycle. Both go away or get per-person handling in release 2.4. There are no
> non-organizational users: intelligence analysts receive products on the brigade network and
> never log in, so no external credentials or federation profiles are accepted.
