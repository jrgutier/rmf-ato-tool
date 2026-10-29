# Step C · Categorize

Describe the system and categorize it in accordance with CNSSI 1253 from the impact of a
loss of confidentiality, integrity and availability. The AO-approved categorization is due
by Milestone A (`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| C-1 | System Description | [C-1.md](C-1.md) | authored | ART-SD (produces), ART-BND |
| C-2 | Security Categorization | [C-2.md](C-2.md) | authored | ART-CAT (produces) |
| C-3 | Security Categorization Review and Approval | [C-3.md](C-3.md) | authored | ART-CAT |

## Running the step

- **Facts are written here.** C-1 writes the system identity facts, C-2 the categorization
  and C-3 its approval, all in `facts.yaml` (INV-4); each fact has one writer.
- **The approval gates Select.** `rmf baseline resolve` refuses an unapproved
  categorization, and FACTS-001 fails before S-1 until C-3 approves it.
- **Hybrid runs:** the categorization approval is a decision reserved for a human when
  `run.yaml:humans` names the approver (`_shared/hybrid-mode.md`).
- **Session unit:** one session for the step.

## Citations

- SP 800-37r2 §3.2 (Categorize): `uv run rmf refs show SP800-37R2 --section "3.2"`.
- DoDI 8510.01 §3.2.b and Table 2: `uv run rmf refs show DODI8510.01 --section "b. Categorize"`.
