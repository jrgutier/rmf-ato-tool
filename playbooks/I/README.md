# Step I · Implement

Implement the controls in the plans and record how they are employed in the system and its
operating environment. Implement runs through EMD: designed in by the CDR and updated to
the as-built state before test readiness (`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| I-1 | Control Implementation | [I-1.md](I-1.md) | authored | ART-STIG (produces) |
| I-2 | Update Control Implementation Information | [I-2.md](I-2.md) | generated | ART-SSP, ART-SD, ART-INV, ART-CMP, ART-CP, ART-IRP |

## Running the step

- **The agent records, the program builds.** I-1 documents how the controls were
  implemented and the STIG/SRG state of every inventory item, from the developer's and
  engineers' answers and the product material.
- **Plan changes go through I-2.** I-1 leaves the SSP alone; I-2 updates the SSP family
  files, the system description, the inventory and the three plans to the as-implemented
  state. Rewrite each SSP family file whole (`_shared/ssp-batching.md`).
- **STIG-001** needs every software, operating-system, database, firmware and
  virtual-machine inventory item mapped to a benchmark or given a not-applicable rationale.
- **Session unit:** one session for the step; I-2 over a large SSP may need more.

## Citations

- SP 800-37r2 §3.4 (Implement): `uv run rmf refs show SP800-37R2 --section "3.4"`.
- DoDI 8510.01 §3.2.d and Table 4:
  `uv run rmf refs show DODI8510.01 --page 16 --anchor "Implement the controls and describe how the controls are employed"`.
