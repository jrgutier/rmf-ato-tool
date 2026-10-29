"""Validate OSCAL JSON against the pinned NIST v1.2.1 schemas (plan PM-3, L-0005).

The schemas use ``\\p{L}``/``\\p{N}``, which Python ``re`` cannot compile, so ``pattern``
and ``patternProperties`` are evaluated with the ``regex`` package. ``FormatChecker()``
(``jsonschema[format]``) enforces date-time, uri, uri-reference, email and uuid.
"""

from __future__ import annotations

import functools
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import regex
from jsonschema import Draft7Validator, FormatChecker, ValidationError, validators

SCHEMA_DIR = "references/oscal/schemas"
SCHEMA_FILES = {
    "ssp": "oscal_ssp_schema.json",
    "assessment-plan": "oscal_assessment-plan_schema.json",
    "assessment-results": "oscal_assessment-results_schema.json",
    "poam": "oscal_poam_schema.json",
    "catalog": "oscal_catalog_schema.json",
    "profile": "oscal_profile_schema.json",
}
ROOT_KEYS = {
    "system-security-plan": "ssp",
    "assessment-plan": "assessment-plan",
    "assessment-results": "assessment-results",
    "plan-of-action-and-milestones": "poam",
    "catalog": "catalog",
    "profile": "profile",
}


@functools.lru_cache(maxsize=512)
def _compiled(pattern: str) -> regex.Pattern[str]:
    return regex.compile(pattern)


def _pattern(validator: Any, patrn: str, instance: Any, schema: dict) -> Iterator[ValidationError]:
    if validator.is_type(instance, "string") and not _compiled(patrn).search(instance):
        yield ValidationError(f"{instance!r} does not match {patrn!r}")


def _pattern_properties(validator: Any, pattern_properties: dict, instance: Any,
                        schema: dict) -> Iterator[ValidationError]:
    if not validator.is_type(instance, "object"):
        return
    for patrn, subschema in pattern_properties.items():
        for key, value in instance.items():
            if _compiled(patrn).search(key):
                yield from validator.descend(value, subschema, path=key, schema_path=patrn)


OscalValidator = validators.extend(
    Draft7Validator, {"pattern": _pattern, "patternProperties": _pattern_properties}
)


def all_patterns(schema: Any) -> Iterator[str]:
    """Every ``pattern`` value and ``patternProperties`` key in a schema tree."""
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "pattern" and isinstance(value, str):
                yield value
            elif key == "patternProperties" and isinstance(value, dict):
                yield from value
            yield from all_patterns(value)
    elif isinstance(schema, list):
        for item in schema:
            yield from all_patterns(item)


def load_schema(root: Path, model: str) -> dict:
    if model not in SCHEMA_FILES:
        raise KeyError(f"unknown OSCAL model {model!r}; expected one of {', '.join(SCHEMA_FILES)}")
    return json.loads((root / SCHEMA_DIR / SCHEMA_FILES[model]).read_text(encoding="utf-8"))


def model_of(doc: dict) -> str:
    """The model name for an OSCAL document, from its single root key."""
    for key, model in ROOT_KEYS.items():
        if key in doc:
            return model
    raise KeyError(f"not an OSCAL document (root keys: {', '.join(doc) or 'none'})")


def validator_for(root: Path, model: str) -> Any:
    return OscalValidator(load_schema(root, model), format_checker=FormatChecker())


def validate(root: Path, doc: dict, model: str | None = None) -> list[ValidationError]:
    """All schema errors for ``doc`` (empty when valid), in document order."""
    validator = validator_for(root, model or model_of(doc))
    return sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path])


def describe(error: ValidationError) -> str:
    where = "/".join(str(p) for p in error.absolute_path) or "(root)"
    return f"{where}: [{error.validator}] {error.message[:300]}"
