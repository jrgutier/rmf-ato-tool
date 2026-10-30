---
interview_id: INT-088
run_id: example-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [sa development and configuration management evidence, sc built-in mechanisms, ground data terminal firmware and mission planner status]
---
# INT-088 — A-3 — PER-DEV

### Q1 {#INT-088.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: sa-3, sa-3.1, sa-3.2, sa-4.1, sa-4.2, sa-4.9, sa-8, sa-8.14, sa-8.28, sa-10, sa-10.1, sa-10.3, sa-10.7, sa-11.1, sa-15, sa-15.3
Show the development and configuration management records for the current release.

**A1 {#INT-088.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]]
> The release package has the control functional description and the design and implementation
> documents, and the ports, protocols and services list the router rules are built from. The
> design review minutes show the security review, the criticality analysis and the ISSE's
> acceptance against the risk assessment. Our change board minutes list the ISSE at every meeting.
> The static analysis reports for the flight control and video applications are attached to each
> build record. The test data set is synthetic routes, test keys and range imagery. Every bundle
> is signed and the install log shows the signature check; a bundle with a broken signature was
> refused in our own test. Hardware ships with numbered tamper seals recorded on the packing list.

### Q2 {#INT-088.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: sc-4, sc-8, sc-8.1, sc-8.2, sc-13, sc-16, sc-16.1, sc-16.2, sc-18, sc-18.1, sc-18.2, sc-18.3, sc-18.4, sc-23, sc-23.1, sc-23.3, sc-23.5, sc-28, sc-28.1, sc-28.3, sc-39, sc-47
Show how the built-in protection mechanisms are configured and tested.

**A2 {#INT-088.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]]
> The image settings show full-disk encryption on with the key in the TPM, the FIPS mode setting
> on, and the operating system and router running their validated modules; the validation
> certificates are in the documentation set. Uplink TLS is mutual, with DoD PKI certificates and a
> trust store holding only DoD roots. Sessions are invalidated at sign-out. The application
> control policy allows only integrator-signed components and blocks and logs anything else;
> there is no browser or mail client in the image. The video export runs the marking check and
> signs the package; an export with a missing marking is refused, which our test log shows.
> DT-1 shows commands from an unkeyed terminal rejected and lost-link return on 6 of 6 flights.

### Q3 {#INT-088.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: sa-3.3, sa-5, sa-11, sa-22, sc-5, ra-5
What is the status of the ground data terminal firmware fix and the mission planner?

**A3 {#INT-088.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> Firmware 5.2.1 is in regression testing for the 2026-12 bundle; until then the management web
> service still has the published crash vulnerability and is reachable only from the station
> internal segment. For the mission planner, the vendor has not published a security guide, so
> our hand-hardening settings are a recorded list that nobody has tested against the SRG; DT-1 did
> not cover it either. Vendor support for Planner 7 ends in 2027-06 and no replacement is chosen.
