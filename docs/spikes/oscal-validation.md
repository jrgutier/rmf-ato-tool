# Spike: OSCAL schema validation (Phase 2, PM-3)

- **Date:** 2026-10-29
- **Question:** Can the pinned NIST OSCAL v1.2.1 JSON schemas validate the documents this
  tool reads and generates, with formats enforced, using `jsonschema` in Python?
- **Outcome:** yes, with the `regex`-backed validator in
  `src/rmf_tool/oscal/schema_validate.py` plus `FormatChecker()`. The plan's design
  (PM-3, L-0005) holds; the details below are what the tests pin.

## Inputs

All fetched by `rmf refs fetch` and pinned in `references/index.yaml`:

- `references/oscal/schemas/oscal_{ssp,assessment-plan,assessment-results,poam,catalog,profile}_schema.json`
  from the `usnistgov/OSCAL` v1.2.1 release assets. Each schema's `$id` is
  `http://csrc.nist.gov/ns/oscal/1.2.1/oscal-<model>-schema.json`, and each declares
  JSON Schema draft-07.
- The 800-53 Rev. 5 catalog, the LOW/MODERATE/HIGH/PRIVACY profiles and their resolved
  catalogs, all from `usnistgov/oscal-content` v1.6.0. Every one of them is stamped
  `oscal-version: 1.2.3` and is catalog version `5.2.0`.
- The NIST example SSP (`examples/ssp/json/ssp-example.json` at v1.6.0), stamped
  `oscal-version: 1.2.3`.

## Findings

1. **The `re` module cannot compile the schemas.** All six schemas share nine distinct
   `pattern` values and have no `patternProperties`. One of the patterns
   (`TokenDatatype`, `^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$`) does not compile under `re`. A
   plain `Draft7Validator` raises `re.error: bad escape \p at position 2` on the first
   token it checks. `regex` compiles all nine (`test_all_schema_patterns_compile`).
2. **The validator** is `jsonschema.validators.extend(Draft7Validator, {"pattern",
   "patternProperties"})`, with both keywords evaluated through `regex.search` and
   compiled patterns cached.
   - `additionalProperties` still uses `re`, but only to match `patternProperties` keys,
     and the OSCAL schemas have none. If a later schema version adds them,
     `test_all_schema_patterns_compile` will still pass, and `additionalProperties`
     will then also need the `regex` engine.
3. **Formats.** The schemas use `date-time`, `uri`, `uri-reference` and `email`.
   - `uuid` is not a `format` in OSCAL. UUIDs are checked by the `UUIDDatatype` pattern
     (v4/v5 only).
   - `FormatChecker()` with `jsonschema[format]` installed provides all four formats, plus
     `uuid`.
   - `Draft7Validator.FORMAT_CHECKER` lacks `uuid`, so we use `FormatChecker()`.
   - Formats catch errors that the patterns miss. `import-profile.href = "has a space"`
     passes the schema structurally but fails `uri-reference`.
   - A date-time with no timezone, or an impossible date such as `2026-02-30`, fails
     both `format` and the `DateTimeWithTimezoneDatatype` pattern
     (`test_format_checker_enforced`).
4. **Same-minor inputs validate.** The 1.2.3 catalog, profiles, resolved catalogs and the
   example SSP all validate against the 1.2.1 schemas with 0 errors
   (`test_nist_example_ssp_validates`, `test_catalog_and_profiles_validate`). This
   supports reading 1.2.x inputs as raw JSON (L-0004).
5. **Cost.** On an M-series laptop:

   | Document | Validation time |
   |---|---|
   | Full 800-53 catalog (10 MB) | 1.8 s |
   | HIGH resolved catalog | 0.8 s |
   | Example SSP | 0.02 s |

   A 287-control generated SSP will be well under a second, so CI can validate every
   generated document.
6. **Counts pinned for later phases.**
   - The MODERATE profile selects **287** controls and enhancements (`with-ids`).
   - The MODERATE resolved catalog contains the same 287
     (`test_moderate_resolved_count`).

## Decisions

- Generated OSCAL stays at `1.2.1` (trestle 5.2.0), validated against the v1.2.1 schemas
  with `schema_validate.validate()`.
- Inputs stay at any `1.2.x` and are read as raw JSON. REF-005
  (`rmf_tool.oscal.version.check`) enforces the pins, which are recorded in
  `references/oscal/VERSIONS.yaml`.
- No schema patches. If NIST ships a schema that `regex` cannot compile,
  `test_all_schema_patterns_compile` fails, and the bump is blocked until it is handled.
