# FW-PER-002 negative fixture

A miniature repository root for `rmf_tool.framework.personas_check`, checked against the
personas of `tests/fixtures/framework_mini/`. Every persona has a card, so FW-PER-001 stays
quiet, and each card has one defect:

- PER-AO has no `## Red lines` section;
- PER-PM has an empty `## Typical concerns` section;
- PER-ISSM cites an anchor that is not on the cited page;
- PER-IO's `## Citations` section has no `uv run rmf refs show` command.
