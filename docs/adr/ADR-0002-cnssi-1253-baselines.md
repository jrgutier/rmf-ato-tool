# ADR-0002: CNSSI 1253 Appendix D as structured framework data

Date: 2026-10-29 · Status: accepted · Phase: 6 · Schemas: `framework/schema/baselines.schema.json` (new), `framework/schema/baseline.schema.json` (origin enum)

## Context

Task S-1 for a national security system selects controls per CNSSI 1253 §3.2.1 (p14). The
system takes the NSS security control baseline "corresponding to the security
categorization of the system (i.e., the impact levels determined for each security
objective)" and adds the NSS privacy control baseline, "which is a default for all NSS".
Appendix D (Tables D-1 to D-20, PDF pages 25 to 160) gives, for every SP 800-53r5 control,
an X, a + or a -- in the privacy column and in nine security columns (C, I and A, each at
low, moderate and high).

Phase 3.5 used the SP 800-53B profile at the high-water mark of C/I/A, labelled
`method: high-water-mark`, because the tables were not machine-readable.
`references/text/CNSSI1253.md` drops empty table cells, so the column a symbol sits in
cannot be recovered from the text alone.

## Decision

- Add `framework/baselines/cnssi-1253.yaml`. Each Appendix D row becomes
  `{id, privacy, c, i, a}`, using OSCAL control IDs. `c`/`i`/`a` are three characters
  (low, moderate, high), each X (800-53B and NSS), + (NSS addition), - (`--`, 800-53B only)
  or . (blank). A withdrawn row is `{id, withdrawn: true}`.
- Rows are grouped per table and per PDF page. Every page block carries
  `citation: {ref: CNSSI1253, page, anchor}`, where the anchor is the table title on the
  table's first page and the first row ID on later pages. The file also lists the
  Appendix E overlays by reference ID. Only `CNSSI1253E-ATT5-CLASSIFIED` (Table 1, a plain
  add-list) is transcribed, with its own page citations. The others have
  `transcribed: false`.
- `framework/schema/baselines.schema.json` validates the file. `rmf validate` reads
  `framework/baselines/*.yaml` (except `*.overrides.yaml`) and applies two rules:
  FW-SCHEMA-001 for schema errors and FW-CITE-001/002 for every block citation. The blocks
  are not framework entities, so no ID rules apply.
- The file is generated, never hand-typed: `uv run python -m rmf_tool.cnssi1253 [--check]`.
  - Cell values come from the PDF's word geometry: each symbol goes to the nearest L/M/H
    header, and a continuation page reuses the previous page's header.
  - Each row's ordered symbol sequence must equal the sequence in the text extraction.
  - Every ID must exist in the 800-53r5 catalog.
  - A row that cannot be read goes in `framework/baselines/cnssi-1253.overrides.yaml`,
    with a reason. An override that changes nothing fails. None are needed today: all 1,189
    rows match the text.
- `rmf baseline resolve` selects the union of the rows whose cell for each objective at
  that objective's own level is X or + (origin `baseline`) and the rows whose privacy cell
  is X or + (origin `privacy-baseline` when no security column selects them). It then adds
  the overlay controls (origin `overlay`), applies `tailoring.yaml`, and applies
  `control_subset`.
- The privacy baseline is unconditional. CNSSI 1253 says so on three pages:
  - p14 (§3.2.1): "Include the NSS privacy control baseline contained in Appendix D Tables
    D-1 through D-20, which is a default for all NSS."
  - p10 (§2.5.1): "All systems will implement the NSS privacy control baseline to manage
    organizational PII risks."
  - p22 (Appendix D): "Controls indicated with an "X" or a "+" in this column are required
    for all NSS."

  Only the Privacy Overlay depends on PII: p6 says PII-specific controls "have been removed
  from the NIST privacy control baseline and incorporated into the Privacy Overlays", and
  that determination needs SAOP approval. So the overlay follows
  `categorization.overlays`, and the privacy baseline follows no flag. The three quotes are
  page+anchor citations in the YAML.
- `baseline.schema.json` gains the origin value `privacy-baseline`, so a reader of
  `baseline.json` sees why a control that no security objective selects is in the set.
  - `baseline.json` records `method: cnssi1253`, the value the frozen `baseline.schema.json`
    already reserved, and a `baseline_id` of the form `CNSSI1253-M-M-L[-SUBSET-n]`.
  - The method is the `categorization.method` fact. `--method` must agree with it.
  - `high-water-mark` is refused unless the CNSSI1253 reference is `degraded` (plan §7.6).
  - An overlay that is not transcribed, or is unknown, fails with a message naming it.

## Consequences

- `baseline.json` keeps its keys. The values of `method`, `baseline_id` and `sources`
  change, and `origin` can be `privacy-baseline`. For M/M/L the full selection is 466
  controls (35 of them `privacy-baseline`), against 287 in the 800-53B moderate profile: CNSSI adds 200 and drops 21 (availability-moderate controls when A is
  low, and IA-12(5), which CNSSI marks `--`).
- Fixtures and runs resolved with the high-water mark go stale under GEN-STALE-001 until
  they are re-resolved: `valid_minimal` here, and the committed skeleton agent result,
  which keeps its recorded check.json.
- The 2022 tables mark SA-15 and SC-7(8) (moderate) and SI-4(22) (high) with `+`, because
  a later 800-53B release added them to its profiles. The generator reports this
  difference, and a test pins it.
- The 5.2.0 catalog has seven controls with no CNSSI row (IA-13 and its enhancements,
  SA-15(13), SA-24, SI-2(7)). They can enter only through tailoring.
- The Space Platform and Privacy overlays select controls by condition. They have to be
  transcribed before a run can list them in `categorization.overlays`.
