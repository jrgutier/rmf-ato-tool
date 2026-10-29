# Step P · Prepare

Set the organizational and system context and priorities for security and privacy risk
management before the system is categorized. The organization-level tasks (P-1 to P-7)
come before the program; the system-level tasks (P-8 to P-18) run in MSA and early TMRR,
most of them before Milestone A and the SRR. Requirements allocation (P-17) is finished by
the SFR (`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| P-1 | Risk Management Roles | [P-org-context.md#task-p-1](P-org-context.md#task-p-1) | authored | ART-ORG-CONTEXT (produces) |
| P-2 | Risk Management Strategy | [P-org-context.md#task-p-2](P-org-context.md#task-p-2) | authored | ART-ORG-CONTEXT |
| P-3 | Risk Assessment—Organization | [P-org-context.md#task-p-3](P-org-context.md#task-p-3) | authored | ART-ORG-CONTEXT |
| P-4 | Organizationally-Tailored Control Baselines and CSF Profiles (optional) | [P-org-context.md#task-p-4](P-org-context.md#task-p-4) | authored | ART-ORG-CONTEXT |
| P-5 | Common Control Identification | [P-org-context.md#task-p-5](P-org-context.md#task-p-5) | authored | ART-ORG-CONTEXT |
| P-6 | Impact-Level Prioritization (optional) | [P-org-context.md#task-p-6](P-org-context.md#task-p-6) | authored | ART-ORG-CONTEXT |
| P-7 | Continuous Monitoring Strategy—Organization | [P-org-context.md#task-p-7](P-org-context.md#task-p-7) | authored | ART-ORG-CONTEXT |
| P-8 | Mission or Business Focus | [P-8.md](P-8.md) | generated | none (interviews) |
| P-9 | System Stakeholders | [P-9.md](P-9.md) | generated | ART-STAKE |
| P-10 | Asset Identification | [P-10.md](P-10.md) | authored | ART-INV |
| P-11 | Authorization Boundary | [P-11.md](P-11.md) | authored | ART-BND |
| P-12 | Information Types | [P-12.md](P-12.md) | generated | ART-INFOTYPES |
| P-13 | Information Life Cycle | [P-13.md](P-13.md) | generated | ART-INFOTYPES |
| P-14 | Risk Assessment—System | [P-14.md](P-14.md) | generated | ART-RA |
| P-15 | Requirements Definition | [P-15.md](P-15.md) | generated | ART-REQ |
| P-16 | Enterprise Architecture | [P-16.md](P-16.md) | generated | ART-BND |
| P-17 | Requirements Allocation | [P-17.md](P-17.md) | generated | ART-REQ |
| P-18 | System Registration | [P-18.md](P-18.md) | generated | ART-REG |

Each playbook's header gives the exact outputs (produced or updated); this table is a map.

## Running the step

- **Organization first, often seeded.** P-1 to P-7 build the organization's context, which
  most forks already have: ART-ORG-CONTEXT is then seeded and the tasks deferred as
  `performed-externally` (`P-org-context.md`, "How these tasks run").
- **The system tasks build the inputs of everything after.** The inventory (P-10), the
  boundary (P-11, refined by P-16), the information types (P-12, P-13) and the risk
  assessment (P-14) feed categorization; the requirements (P-15, P-17) feed selection.
- **Session unit:** one session for the step, in the order `rmf status` gives; a long
  Prepare step may end after any CHECKPOINT and resume (`_shared/session-units.md`).
- **P-8 has no artifact output.** Its interviews are its record; P-9, P-10 and C-1 cite the
  answers.

## Citations

- SP 800-37r2 §3.1 (Prepare): `uv run rmf refs show SP800-37R2 --section "3.1"`.
- DoDI 8510.01 §3.2.a and Table 1 (Prepare):
  `uv run rmf refs show DODI8510.01 --page 13 --anchor "Prepare to execute the RMF from an organizational and system-level perspective"`.
