# Spike: trestle authoring flow for the SSP (decision B4)

- **Date:** 2026-10-29. **Time box:** 4 h; about 30 minutes were used.
- **Tool:** compliance-trestle 5.2.0 (`trestle version`: "v5.2.0 based on OSCAL version
  1.2.1"), from the project venv.
- **Question (plan §2, decision b):** should the SSP be authored with
  `trestle author ssp-generate` → per-control Markdown → `trestle author ssp-assemble`
  instead of the B1 builder?
- **Adoption criteria:** the round-trips are clean *and* the Markdown is agent-editable.
  Adoption also must not break the plan's invariants: deterministic uuid5 IDs, a
  byte-identical rebuild (GEN-STALE-001), and one home per fact.
- **Outcome: B4 is not adopted.** B1 stays. Both criteria are technically met, but B4
  fails the determinism invariant and saves no builder work. Details below.

## Procedure

The spike ran in a throwaway workspace (the session scratchpad, not the repo):

```sh
trestle init
trestle import -f references/oscal/catalog/NIST_SP-800-53_rev5_catalog.json -o nist53
# The profile's import href is a back-matter "#uuid" link; it is rewritten to
# trestle://catalogs/nist53/catalog.json in a copy.
trestle import -f moderate.json -o moderate
trestle author ssp-generate -p moderate -o ssp_md        # 287 files, about 1 s
# edit ssp_md/ac/ac-2.md: "This System" prose + "Implementation Status: implemented"
trestle author ssp-assemble -m ssp_md -o spike_ssp       # about 1.5 s
uv run python -c '...schema_validate.validate(...)'      # NIST v1.2.1 schema
trestle author ssp-assemble -m ssp_md -o spike_ssp2      # fresh assemble
trestle author ssp-assemble -m ssp_md -n spike_ssp -o spike_ssp  # in-place reassemble
trestle author ssp-generate -p moderate -o ssp_md        # regenerate over edited MD
```

## Results

| Check | Result |
|---|---|
| Import the oscal-content v1.6.0 catalog (OSCAL **1.2.3**) without restamping | **Works.** In trestle 5.2.0 the `OscalVersion` validator has `strict_version = False` and accepts any version. The plan's claim that trestle rejects 1.2.2/1.2.3 is wrong (L-0011). |
| `ssp-generate` from the MODERATE profile | 287 Markdown files, one per control or enhancement, in 18 family folders. No component definitions are required. |
| Edit prose + status in one file, then `ssp-assemble` | The edit lands in `implemented-requirements[ac-2].by-components[0]` (`description`, `implementation-status.state`). |
| Assembled SSP vs the NIST v1.2.1 schema (regex + FormatChecker) | **0 errors.** It is stamped `oscal-version: 1.2.1`. |
| Round-trip MD → JSON → regenerate MD | Clean. The edited prose and status survive `ssp-generate` over the existing folder. |
| In-place reassemble (`-n spike_ssp`) | Byte-identical JSON. UUIDs and `last-modified` are kept. |
| **Fresh assemble** from the same Markdown | **Different random UUIDs** for the SSP and every implemented requirement. |
| `system-characteristics` | Placeholders (`system-ids: [{id: REPLACE_ME}]`, `system-name: REPLACE_ME`, ...). Nothing in the per-control Markdown fills them. |
| Size of one control file (`ac-2.md`) | About 200 lines. Of these, about 75 are a YAML header of parameter placeholders, about 110 are statement, objective and guidance text copied from the catalog, and the agent edits only about 3 lines. |

## Why B4 is not adopted

1. **Determinism.** B4 cannot do a fresh, deterministic build.
   - GEN-STALE-001 compares the committed OSCAL with a fresh `rmf build`. A fresh
     `ssp-assemble` assigns new random UUIDs, so that check would always fail.
   - The workaround is to always reassemble in place from the committed JSON. That makes
     the committed JSON an input as well as an output, which violates Principle 1
     (one home per fact).
   - The plan's uuid5 scheme (`uuid5(NAMESPACE_RMF, system/model/entity)`) cannot be
     applied.
2. **No builder work saved.**
   - `system-characteristics`, users, components, inventory and leveraged
     authorizations still need the B1 mapping (§6.6). The flow fills only
     `control-implementation`.
   - SAP, SAR and POA&M have no trestle authoring flow at all.
   - B4 would therefore add a second authoring paradigm for one quarter of one model.
3. **Context cost.**
   - Each control file repeats catalog text that the agent already gets from
     `rmf catalog show`.
   - A 30-control batch is about 6,000 lines of mostly read-only Markdown, against
     about 30 compact YAML entries in `ssp/controls/<fam>.yaml` (PM-4).
4. **Fragile conventions.** The agent must preserve trestle's header keys, the
   `## What is the solution...` and `### This System` headings, and the
   `#### Implementation Status:` line. Any drift is silently dropped on assembly.

## What carries forward

- trestle stays as the **second validator** (OSCAL-002: trestle 5.2.0 model load) and as
  the pydantic model layer in the B1 builders. Both are confirmed to work on 1.2.1
  output.
- Reading 1.2.x inputs through trestle would work in 5.2.0. We still read them as raw
  JSON (L-0004's rule stands): it keeps us independent of a version validator that a
  future trestle could make strict.
- Revisit B4 only if trestle gains deterministic UUIDs, or a hook to seed them, and an
  SAR/POA&M authoring flow.
