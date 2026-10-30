# Agent lane

Evidence that a headless agent can follow the playbooks cold (plan §4.4, decision E3). The
lane runs **locally only**, under the operator's own Claude Code login; CI never runs it and
holds no secret. Its committed results are **self-attested**: `rmf ci` checks that they
exist, report 0 errors and are current (AGENT-001: a warning under `rmf ci`, an error under
`rmf ci --release`), but cannot reproduce them.

## Layout

| Path | What it is |
|---|---|
| `scenarios/<s>.yaml` | a scenario (schema `framework/schema/scenario.schema.json`): product, scope, seeds, control subset, and the `hash_globs` its `upstream_hash` covers |
| `prompts/<s>.md` | the prompt each session starts with; the harness appends `Current step: <STEP>. Start with: uv run rmf status` |
| `products/esg/` | the fictional Example Sensor Gateway: CONOPS, architecture, data flows, inventory, test results, `profile.yaml` |
| `seeds/esg-skeleton/` | seeded artifacts for the skeleton scenario, at their run-relative paths |
| `results/<s>/` | committed evidence: `check.json` (from `rmf check --final --format json`) and `meta.yaml` |
| `test_agent_lane.py` | re-hashes `check.json` against `meta.yaml:check_sha256` and checks errors == 0 and a current `upstream_hash` |

## Running a scenario

```sh
scripts/agent-run.sh --dry-run skeleton   # prints the plan and argv; no agent, no cost
scripts/agent-run.sh skeleton             # real run: costs credits under your login
```

The harness copies the repository to `$TMPDIR/rmf-agent-<scenario>`, initializes the run
from the scenario (`rmf run init --scenario ...`), then starts one `claude -p` session per
RMF step in scope, with only `--allowedTools "Bash(uv run rmf:*)" Read Edit Write Glob Grep`,
`--setting-sources project` (so the operator's global settings and hooks do not leak in),
and `--max-budget-usd`. Two sessions in a row without progress stop the loop (PM-7). It
then runs `rmf build` and `rmf check --final`, and writes `results/<s>/check.json` and
`meta.yaml`. Only the operator runs the real lane, and only after reviewing the dry run.

`scripts/agent-run.sh --run-dir DIR <name>` drives an existing run instead (the example
fork run, Phase 7): no `rmf run init`, the prompt is `prompts/<name>.md`, the finished run
is copied back over `DIR`, and `results/<name>/` gets `check.json` and `meta.yaml` only.
Such a result has no scenario file, so AGENT-001 does not track it; its run is checked by
the p7 `rmf ci` step instead. `AGENT_TOTAL_BUDGET_USD` stops the loop once the sessions so
far cost that much; a resumed run's `meta.yaml` covers only its own sessions.

```sh
AGENT_TOTAL_BUDGET_USD=80 AGENT_BUDGET_USD=3 AGENT_MAX_SESSIONS=70 \
  scripts/agent-run.sh --run-dir examples/uas-gcs/runs/example-synthetic-01 example-uas-gcs
```

codex (`codex exec`) is a documented, **unsupported** alternative: the playbooks are
agent-agnostic, but no codex lane or result is maintained.

## The skeleton scenario

- 12 tasks (P-10, P-11, C-1, C-2, C-3, S-1, S-4, A-2, A-3, A-6, R-2, R-4) on ESG, synthetic
  mode, baseline restricted to ac-2, au-2, cm-6, ia-2, sc-7, si-2.
- Seeds stand in for the out-of-scope producers (plan §7.3), plus ART-REQ, which C-1 and S-1
  read and whose producer P-15 is out of scope:

  | Artifact | From task | Seed files |
  |---|---|---|
  | ART-ORG-CONTEXT | P-1 | `artifacts/ART-ORG-CONTEXT.md` |
  | ART-STAKE | P-9 | `artifacts/ART-STAKE.md` |
  | ART-INFOTYPES | P-12 | `artifacts/ART-INFOTYPES.md`, `artifacts/data/infotypes.yaml` |
  | ART-BASELINE | S-2, S-3 | `artifacts/data/tailoring.yaml`, `artifacts/data/allocation.yaml` |
  | ART-STIG | I-1 | `artifacts/ART-STIG.md`, `artifacts/data/stig-summary.yaml` |
  | ART-RA | P-14 | `artifacts/ART-RA.md` |
  | ART-REQ | P-15 | `artifacts/ART-REQ.md` |

  ART-PKG is not seeded: the agent runs `rmf package` before R-2.
- Non-vacuity: the product discloses a shared privileged maintenance account and late
  patching on fielded units, and the seeded STIG results carry two open CAT II findings, so
  an honest run produces other-than-satisfied determinations, findings and POA&M items.

## Changing seeds or the product

- Keep the product's `CMP-*` and `INV-###` IDs: seeded allocation and STIG data refer to
  them.
- Seed Markdown carries `run_id: esg-skeleton`; `rmf run init` rewrites it to the actual run
  ID when it copies the seed.
- Every seeded data file must validate against its schema and every seeded artifact must
  pass `rmf check` on a fresh run: initialize a scratch run from the scenario and run
  `uv run rmf build <run>` and `uv run rmf check <run> --rules RUN-CFG-001,RUN-FM-001,TRACE-001,TRACE-002`.
- Any change to the files in a scenario's `hash_globs` makes its committed result stale
  (AGENT-001) until the lane is run again.
