# Tagging and traceability

Every claim in a run traces to evidence (INV-5): an interview answer, a product file, an
artifact, or a tagged assumption. This file is the one home of the trace-token grammar and
of where tokens go.

## Steps

1. **Before you write a claim, find its evidence**: an answer you recorded, a product
   passage, or an input artifact. If there is none, ask (`_shared/interviewing.md`) or
   record an assumption (step 4).
2. **Write the token** where the claim is (see "Where tokens go").
3. **Use only tokens that resolve.** The answer anchor, product file and anchor, artifact or
   assumption must exist on disk when you run `rmf check` (TRACE-002).
4. **Record an assumption** by adding an entry to `assumptions.yaml` (whole-file rewrite,
   INV-8) and citing its ID:

   ```yaml
   assumptions:
     - id: ASM-001
       statement: The CSSP retains ESG audit records for at least one year.
       rationale: The architecture names the CSSP as the long-term log store but gives no period.
       task: S-4
       persona: PER-CCP
       tag: ASSUMPTION
       sources: [product/architecture.md#logging]
   ```

   Number assumptions globally (`ASM-001`, `ASM-002`, ...). A prefix names a family of
   policy-driven assumptions that a playbook defines (for example `ASM-BASELINE-001` under
   the degraded-reference policy); do not invent new prefixes. `tag` is always `ASSUMPTION`.
5. **Run `rmf build`, then `rmf check`.** Build regenerates `reports/assumptions.md`
   (HYB-002); check runs TRACE-001, TRACE-002 and HYB-001.

## Token grammar

| Token | Form | Resolves to |
|---|---|---|
| Interview answer | `INT-###.A#` (e.g. `INT-007.A3`) | the `{#INT-007.A3}` anchor in `interviews/INT-007-*.md` |
| Assumption | `ASM-###` or `ASM-<PREFIX>-###` (e.g. `ASM-012`, `ASM-BASELINE-001`) | an `id` in `assumptions.yaml` |
| Product file | `product/<path>` or `product/<path>#<anchor>` (e.g. `product/architecture.md#identity`) | a file under the run's product directory, and the heading anchor in it |
| Artifact | `ART-<NAME>` (e.g. `ART-ORG-CONTEXT`) | `artifacts/ART-<NAME>.md` in the run |

Exact patterns: `INT-\d{3}\.A\d+`, `ASM-(?:[A-Z]+-)?\d{3}`,
`product/[^\s#]+(?:#[A-Za-z0-9_.-]+)?`, `ART-[A-Z]+(?:-[A-Z]+)*`. Nothing else is a token:
not a URL, not a reference ID, not a question anchor (`INT-007.Q3`).

## Where tokens go

- **Artifact front-matter `sources`:** the tokens the whole artifact rests on.
- **Artifact prose:** write `[[TOKEN]]` right after the claim, for example
  `Accounts are reviewed every quarter [[INT-007.A1]].` TRACE-001 splits the body at
  every heading (any level, `#` to `######`): each part that holds any text, including the
  text between the H1 and the first `##`, needs at least one `[[TOKEN]]`. Tables and block
  quotes count as text. The CLI-owned facts block (between `<!-- BEGIN rmf:facts -->` and
  `<!-- END rmf:facts -->`) and HTML comments are ignored.
- **Structured YAML:** each record's `sources:` list (bare tokens, no brackets). Records
  without a `sources` field inherit the file-level `sources`.
- **Interview answers:** ` · basis: [[TOKEN]] [[TOKEN]]` on the answer header.
- **Facts:** the optional `sources:` list on each `facts.yaml` field; give it whenever the
  value came from an interview.

## Tags

| Tag | Where | Meaning |
|---|---|---|
| `SIMULATED` | interview answer header | the agent answered in character (all answers in synthetic mode; role-played personas in hybrid mode) |
| `HUMAN` | interview answer header | a person named in `run.yaml:humans` answered (hybrid only) |
| `ASSUMPTION` | `assumptions.yaml` entry | the agent supplied the claim without an answer or a product source |

An answer without a tag, or an assumption without `tag: ASSUMPTION`, fails HYB-001.

## Citations

- SP 800-37r2 §2.6 (requirements traced to controls):
  `uv run rmf refs show SP800-37R2 --section "2.6 REQUIREMENTS AND CONTROLS"`.
- SP 800-53Ar5 §2.3 (an assurance case built from evidence):
  `uv run rmf refs show SP800-53AR5 --section "2.3 BUILDING AN EFFECTIVE ASSURANCE CASE"`.
