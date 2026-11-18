---
interview_id: INT-071
run_id: 20261118-synthetic-01
task: S-1
persona: PER-CCP
date: 2026-11-18
topics: [common controls available, full or partial inheritance, provider authorization status]
---
# INT-071 — S-1 — PER-CCP

### Q1 {#INT-071.Q1}
Asked of: PER-CCP · Task: S-1
Speaking for Example GovCloud IL4 region: which of your controls in EFRAS's selected set may the system inherit, fully or in part, and is your authorization current?
**A1 {#INT-071.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-013.A1]] [[product/architecture.md#leveraged]] [[product/architecture.md#physical]]
> For Example GovCloud IL4 region. Of the controls in your set, PE-3 and MP-6 are ours whole:
> nobody from your program enters our data centers, and we sanitize every drive before it leaves
> our control. SI-2 and CP-9 are partial: we patch the hypervisor, the Kubernetes control plane
> and the database engine, and we keep the storage durable, but you patch your worker images and
> containers, and you set and test your own database backups and point-in-time recovery. Our DoD
> provisional authorization at IL4 is from 2024-09-18 and current; our monthly deliverables go to
> the Component portal.

### Q2 {#INT-071.Q2}
Asked of: PER-CCP · Task: S-1
Speaking for Example Enterprise Cloud Access Point: what may EFRAS inherit?
**A2 {#INT-071.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-013.A2]] [[product/architecture.md#network]]
> For Example Enterprise Cloud Access Point. SC-7 and SI-4, both partial. We protect the boundary
> between NIPRNet and the cloud and inspect the traffic at that point. Everything inside your
> virtual network is yours: subnets, security groups, the WAF rules on your load balancer, and
> your egress allow-list. Our ATO is from 2025-01-10 and current.

### Q3 {#INT-071.Q3}
Asked of: PER-CCP · Task: S-1
Speaking for Example Software Factory: what may EFRAS inherit, and what is open on your side?
**A3 {#INT-071.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-013.A3]] [[INT-012.A3]] [[product/conops.md#limitations]]
> For Example Software Factory. Of your set, SA-11, SR-3 and SR-11, all partial. We run the
> static, dependency, image and dynamic scans in the pipeline, we sign the images and we vet the
> upstream sources of our hardened base images. You own your code, your dependencies, your test
> cases and fixing what the scans find, and your cluster's admission policy must refuse unsigned
> images. We also offer SA-10, SA-15 and CM-14, which your dry-run set does not hold. Our ATO is
> from 2025-10-01 and current, with one open POA&M item: the hardened base image that carries the
> image-processing library fix is late, which is your limitation 2.

### Q4 {#INT-071.Q4}
Asked of: PER-CCP · Task: S-1
Does any provider offer a control in EFRAS's set as a full common control that the system could inherit without doing anything itself?
**A4 {#INT-071.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A1]] [[INT-071.A2]] [[INT-071.A3]]
> Only the cloud region's PE-3 and MP-6. Everything the access point and the factory offer needs
> your side configured, so do not write those down as fully inherited.
