# AGENT-001 negative fixture

A miniature repository root for `rmf_tool.check.agent_lane.check`:

- scenario `missing` has no committed result;
- scenario `stale` has a result whose check.json reports an error, does not match
  meta.yaml `check_sha256`, and whose `upstream_hash` is not the scenario's current hash.
