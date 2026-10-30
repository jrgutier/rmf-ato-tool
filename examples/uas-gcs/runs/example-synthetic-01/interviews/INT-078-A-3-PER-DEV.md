---
interview_id: INT-078
run_id: example-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [ia built-in mechanisms, ma remote maintenance settings]
---
# INT-078 — A-3 — PER-DEV

### Q1 {#INT-078.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: ia-2.8, ia-2.12, ia-3, ia-3.1, ia-5.2, ia-5.7, ia-5.14, ia-7, ia-9
Show me the settings and build evidence behind CAC sign-in, device authentication and the cryptographic modules.

**A1 {#INT-078.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]], [[product/test-results.md#dt-1]]
> The image enforces smart card sign-in with Kerberos PKINIT; the trust store holds only the
> DoD roots and is part of the baseline, changed only by the signed bundle. The workstation
> binds to the directory over LDAPS with its machine certificate and the router sends syslog
> over TLS with its device certificate. FIPS mode is on in the OS policy, and the CAC middleware
> and GDT link modules are on their vendors' validated-module lists. The build scan from the
> 2026-10 bundle found no embedded clear-text secrets. In DT-1 an unkeyed terminal's commands
> were rejected, and the flight control application only opens its session with the mission key.

### Q2 {#INT-078.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: ma-4, ma-4.4, ma-4.6, ma-4.7
How is remote administration restricted, encrypted and timed out?

**A2 {#INT-078.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> The router ACL admits SSH and the workstation remote session only from the S6 management
> subnet, after CAC sign-in, on encrypted protocols; idle sessions drop after 10 minutes and the
> end is logged. The GDT has no remote administration; it is managed on the station network only.
