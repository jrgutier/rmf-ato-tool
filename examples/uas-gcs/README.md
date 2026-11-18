# Example fork: uas-gcs (FICTIONAL, SYNTHETIC)

> **FICTIONAL — FOR DEMONSTRATION. NOT AN AUTHORIZATION.** The Example Tactical UAS Ground
> Control Station (ETGCS), its program, units, vendors and people are invented. The run in
> `runs/example-synthetic-01/` is a **synthetic** run: an AI agent role-played every
> stakeholder (every answer is tagged `SIMULATED`). Its "authorization decision" (AD-ATOC),
> assessment results and risk acceptance were made by simulated personas and authorize
> nothing. Outputs of this tool are drafts and never replace a real SCA or AO
> (AGENTS.md, Purpose).

What this example shows: a template fork carried through the DoD RMF from Prepare to the
initial authorization (R-5) plus a simulated first monitoring cycle (M-1, M-2, M-3, M-5),
with a CNSSI 1253 baseline of 524 controls, an OSCAL 1.2.1 SSP, assessment plan,
assessment results and POA&M, and the seeded weaknesses carried honestly into findings and
POA&M items.

What this example does not show: it was produced on framework contract 0.1.0, before the
organization-level and system-level Prepare records existed, so it holds no
`org-context.yaml`, `scrm-org.yaml`, `bia.yaml`, `requirements.yaml`, `ra.yaml` or
`authorizations.yaml` ledger. For the shape of those records, read `templates/data/` (or
`uv run rmf schema template NAME`), the fixture run `tests/fixtures/runs/valid_minimal/`,
and the dry run `dryrun-review/efras/runs/20261118-synthetic-01/`, which goes through every
task on the current contract.

| Path | What it is |
|---|---|
| `product/` | the fictional product package the run read (`README.md` lists its files) |
| `runs/example-synthetic-01/run.yaml` | run configuration: `mode: synthetic`, `lifecycle_stop: R-5` |
| `runs/example-synthetic-01/journal.md` | every session's checkpoints, decisions, corrections and notes |
| `runs/example-synthetic-01/artifacts/` | the draft package artifacts (`ART-*.md`) and their data |
| `runs/example-synthetic-01/oscal/` | generated OSCAL documents |
| `runs/example-synthetic-01/reports/` | `rmf check`, `rmf status` and assumption reports |

How it was produced: `scripts/agent-run.sh --run-dir examples/uas-gcs/runs/example-synthetic-01
example-uas-gcs`, 31 headless sessions (provenance in
`tests/agent/results/example-uas-gcs/parts.yaml`). Two upstream defects the run surfaced
were fixed mid-run (L-0035, L-0036), which is why `rmf check --final` reports one
RUN-STALE-001 warning.
