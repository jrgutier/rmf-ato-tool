# ADR-0004: Scenarios that resume a copy of an existing run

Date: 2026-10-29 · Status: accepted · Phase: 8 · Schemas: `framework/schema/scenario.schema.json` (two optional fields)

## Context

The plan's `cold-start-resume` agent-lane scenario (§4.4) copies a finished run, deletes
`artifacts/sar/results/ac.yaml` and `oscal/`, and has an agent with AGENTS.md as its only
guidance restore the run until `rmf check --final` reports 0 errors. A scenario could only
start an empty run with seeds.

## Decision

- `scenario.schema.json` gains two optional fields:
  - `base_run`: a run directory, relative to the repository root, that `rmf run init
    --scenario` copies instead of creating an empty run.
  - `remove`: run-relative files or directories deleted from the copy. It requires
    `base_run`; absolute paths and `..` segments are rejected by the schema, and a path that
    is missing from the base run is an error.
- The copy keeps the base run's `mode` and `as_of` (its journal times must not go back),
  and its humans, deferrals and lifecycle fields. The stamped identity is new: `run_id`,
  `product` (recomputed for the new location), `upstream_hash` with
  `upstream_hash_basis: {variant: scenario, ...}`, `git_sha`, `framework_version`,
  `oscal_version`. `scope`, `seeded` and `control_subset` come from the scenario, as for
  any scenario; seed paths are checked against the base run.
- Every Markdown front-matter `run_id` in the copy is rewritten to the new run ID.
- `scripts/agent-run.sh` copies the base run into its work copy only for `rmf run init`
  (committed results are otherwise excluded) and deletes `tests/agent/results/` again
  before the first session, so the agent cannot read any result. It puts the base run back
  before the final `rmf build` / `rmf check`, because the scenario hash covers it (L-0037).

## Consequences

- `cold-start-resume` uses `base_run: tests/agent/results/skeleton/run`; its `hash_globs`
  include that run, so re-running `skeleton` makes the cold-start result stale (AGENT-001).
- The schema change makes every scenario whose `hash_globs` cover
  `framework/schema/*.json` stale, which Phase 8 re-runs anyway.
