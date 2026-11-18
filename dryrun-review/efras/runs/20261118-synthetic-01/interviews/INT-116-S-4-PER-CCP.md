---
interview_id: INT-116
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-11-18
topics: [software factory supply chain controls, anti-counterfeit, developer testing support]
---
# INT-116 — S-4 — PER-CCP

### Q1 {#INT-116.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: sr-3, sr-11, sa-11
Speaking for Example Software Factory: what supply chain and testing protections do you provide to EFRAS, and what must EFRAS do?
**A1 {#INT-116.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A3]] [[product/architecture.md#leveraged]] [[product/conops.md#limitations]]
> For Example Software Factory. We vet the upstream sources of our hardened base images with
> our supply chain team, mirror every approved package in our artifact repository, run the
> static, dependency, image and dynamic scans, and sign every image we build; our signing keys
> sit in our hardware security modules. Our anti-counterfeit procedure checks signatures and
> hashes on everything we ingest, and we report a counterfeit or tampered package to its source,
> to the Component's supply chain risk management office and to every tenant that pulled it.
> EFRAS must pull only through our repository, enforce signature verification at admission,
> pin its dependencies, and fix what our scans find in its code. Our open POA&M item is the late
> base image with the image-processing library fix; we expect it in early December.
