# Step S · Select

Select and tailor the initial control set, allocate controls, and document the planned
implementations and the monitoring strategy in plans the AO approves. Select runs in TMRR
and is complete by the PDR and Milestone B (`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| S-1 | Control Selection | [S-1.md](S-1.md) | authored | ART-BASELINE (produces) |
| S-2 | Control Tailoring | [S-2.md](S-2.md) | authored | ART-BASELINE |
| S-3 | Control Allocation | [S-3.md](S-3.md) | authored | ART-BASELINE |
| S-4 | Documentation of Planned Control Implementations | [S-4.md](S-4.md) | authored | ART-SSP, ART-CMP, ART-CP, ART-IRP (produces) |
| S-5 | Continuous Monitoring Strategy—System | [S-5.md](S-5.md) | generated | ART-CONMON (produces) |
| S-6 | Plan Review and Approval | [S-6.md](S-6.md) | generated | ART-SSP |

## Running the step

- **One baseline, one home.** S-1 resolves `baseline.json` with `rmf baseline resolve`; S-2
  records tailoring in `tailoring.yaml` (whose add/remove actions the CLI applies) and S-3
  the allocation in `allocation.yaml`. Never edit `baseline.json` (INV-2).
- **S-4 works family by family** (`_shared/ssp-batching.md`), at most 3 families per
  session, so the step usually takes several sessions.
- **S-5 sets the monitoring frequencies** that M-2 assesses against; every baseline family
  needs one (CONMON-001).
- **S-6 is the AO's approval** (through the AODR); in a hybrid run with a human AO or AODR,
  the approval comes from that person.

## Citations

- SP 800-37r2 §3.3 (Select): `uv run rmf refs show SP800-37R2 --section "3.3"`.
- DoDI 8510.01 §3.2.c and Table 3:
  `uv run rmf refs show DODI8510.01 --page 15 --anchor "Choose an initial set of system controls"`.
