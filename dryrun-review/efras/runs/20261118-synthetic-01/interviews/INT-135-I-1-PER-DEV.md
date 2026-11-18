---
interview_id: INT-135
run_id: 20261118-synthetic-01
task: I-1
persona: PER-DEV
date: 2026-11-18
topics: [STIG scan, benchmarks, open configuration items, build settings]
---
# INT-135 — I-1 — PER-DEV

### Q1 {#INT-135.Q1}
Asked of: PER-DEV · Task: I-1 · Control focus: cm-6, cm-2
Which secure configuration benchmarks did you apply to each inventory item, and which scans ran against them?
**A1 {#INT-135.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/architecture.md#configuration]] [[product/test-results.md#pipeline-1-5]]
> One compliance scan ran for release 1.5.0: the SCA-witnessed scan of 2026-10-22 on the
> pre-production cluster, built from the same templates as production, with the Component
> enterprise SCAP STIG scanner. The worker nodes were scanned against the Kubernetes STIG and
> came out 94% compliant; the open items are control plane checks the managed Kubernetes
> service does not expose to us, and the scanner records them as inherited. The managed
> PostgreSQL database was scanned against the PostgreSQL STIG and came out 88% compliant, with
> six open items. The containers run on the software factory's hardened base image; we take it
> as the factory delivers it and do not re-harden it. Our own containers and the two tracked
> open-source libraries get the pipeline gates at every build (static analysis, dependency
> scan, image scan, authenticated dynamic scan, policy checks), but those are vulnerability
> scans, not a configuration checklist. I cannot give you the STIG release numbers from memory;
> they are in the scan export, which the product material does not reproduce.

### Q2 {#INT-135.Q2}
Asked of: PER-DEV · Task: I-1 · Control focus: cm-6, au-2, ia-5
What are the six open PostgreSQL STIG items, how severe are they, and what is the fix?
**A2 {#INT-135.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/conops.md#limitations]]
> Four are settings the managed PostgreSQL service does not let a tenant configure; the scan
> marks them inherited and the provider answers for them. Two are ours: the connection logging
> verbosity is below the STIG value, and the password complexity of the local break-glass
> database role falls short of the STIG rule. Both are fixed in release 1.5.2, planned for
> 2026-12-10, and will be rescanned then. None of the six is CAT I; all six are CAT II in the
> scan export. No CAT I item is open on the nodes either.

### Q3 {#INT-135.Q3}
Asked of: PER-DEV · Task: I-1 · Control focus: cm-6, sa-11
Was any application or library checked against a STIG or SRG checklist?
**A3 {#INT-135.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#dt-2]]
> No formal checklist review of the application containers is recorded for 1.5.0. What we have
> is the pipeline gate record and the DT-2 results, which cover sign-in, session timeout,
> account disabling, audit forwarding and tampered-extract rejection. The libraries have no
> checklist of their own; they are covered by the dependency scan of the container that carries
> them, which is how the two highs in example-imagelib 2.9.1 were found.
