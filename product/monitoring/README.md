# Monitoring data for M-2

Task M-2 (assess controls on the monitoring strategy's frequencies) reads operational
monitoring data from this directory (EXT-MONITORING). `rmf check` reports RUN-CFG-001 for
M-2 when the run includes M-2 and this directory holds no file other than this one. A run
that stops before M-2 (`lifecycle_stop`) does not need it.

Add one Markdown file per monitoring cycle, for example `cycle-YYYY-MM.md`. Give each record a
`{#anchor}` heading so the run can cite it as `product/monitoring/<file>#<anchor>`, and say who
produced it, its scope and its result. Typical records:

- configuration compliance checks and drift;
- STIG and vulnerability scans after releases or updates;
- log and event reviews;
- account and privilege reviews;
- incidents in the cycle and how they were handled;
- threat and vulnerability updates.

Describe the system at an unclassified level unless the host, machines and LLM endpoint are
authorized (AGENTS.md INV-7).
