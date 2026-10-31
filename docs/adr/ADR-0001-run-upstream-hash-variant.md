# ADR-0001: record which upstream_hash variant a run carries

Date: 2026-10-29 · Status: accepted · Phase: 6 · Schema: `framework/schema/run-config.schema.json`

## Context

`run.yaml:upstream_hash` (plan §4.4) records which upstream files a run was produced
against. `rmf run init` computes it in one of two ways:

- **union**: the plain `rmf run init`, over `AGENTS.md`, `framework/**`, `playbooks/**`,
  `personas/**`, `templates/**` and the tool sources `src/**/*.py`, `src/**/*.yaml`,
  `src/**/*.json`, `src/**/*.j2` (`rmf_tool.run.upstream_hash.UNION_GLOBS`, amended in
  phase 8, see below);
- **scenario**: `rmf run init --scenario FILE`, over the scenario's own `hash_globs`
  (only the files that scenario reads, so the agent-lane result stays current when an
  unrelated playbook changes).

RUN-STALE-001 warns when a run's hash differs from the current hash. To recompute it, the
rule needs to know which variant the run carries, but run.yaml stored only the digest. The
Phase 3.5 skeleton result (`tests/agent/results/skeleton/run`) carries a scenario hash,
which can never equal the union hash.

## Decision

Add one optional key to run.yaml, stamped by `rmf run init` after `upstream_hash`:

```yaml
upstream_hash_basis: {variant: union}
upstream_hash_basis: {variant: scenario, scenario: tests/agent/scenarios/skeleton.yaml}
```

- `variant` is `union` or `scenario`. `scenario` (a path relative to the repository root)
  is required for the scenario variant and forbidden otherwise.
- RUN-STALE-001 recomputes the union hash, or the scenario's `hash_globs` hash. If the
  scenario file is gone, the rule warns that it cannot recompute the hash.
- The key is optional. A run without it is treated as union, which is what every
  `rmf run init` without a scenario produced before this change.

## Consequences

- Existing run.yaml files stay schema-valid. Runs created before this ADR from a scenario
  (the committed skeleton result) show a RUN-STALE-001 warning until they are re-run. The
  warning never affects the error count.
- `rmf run init` stamps the key on every new run, so new runs never hit the fallback.
- The scenario variant ties a run to a file under `tests/agent/`. A fork that deletes the
  agent lane gets the "cannot recompute" warning on such runs, never an error.

## Amendment (phase 8): the tool sources are hashed

The CLI, its rules and its schemas decide what a run's findings mean, but the hash covered
only prose and data, so a rule change left every run looking current. The union hash and
each scenario's `hash_globs` now include `src/**/*.py`, `src/**/*.yaml`, `src/**/*.json`
and `src/**/*.j2` (`upstream_hash.SRC_GLOBS`).

- The globs name suffixes on purpose. `expand()` skips only dot-prefixed path parts, so a
  bare `src/**` would hash `__pycache__/*.pyc` and make every run stale after a test run or
  a Python upgrade. `test_python_caches_cannot_enter_the_hash` pins this.
- Existing runs and agent-lane results carry the old digest, so RUN-STALE-001 and AGENT-001
  warn on them until they are re-run (planned for the final phase). Both are warnings
  before the release gate, and the committed fixtures are re-stamped by the test helpers.
