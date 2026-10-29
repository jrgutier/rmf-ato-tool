from pathlib import Path

import pytest
from conftest import REPO_ROOT
from jsonschema import FormatChecker

from rmf_tool.oscal import schema_validate as sv

SCHEMA = {
    "type": "object",
    "properties": {"token": {"type": "string", "pattern": r"^(\p{L}|_)(\p{L}|\p{N}|[.\-_])*$"}},
    "patternProperties": {r"^\p{Lu}+$": {"type": "integer"}},
}


def errors(instance):
    validator = sv.OscalValidator(SCHEMA, format_checker=FormatChecker())
    return sorted(e.message for e in validator.iter_errors(instance))


def test_unicode_property_patterns():
    assert errors({"token": "Ünïcode_1", "ÄB": 3}) == []
    assert errors({"token": "1bad"})[0].startswith("'1bad' does not match")
    assert errors({"ÄB": "three"}) == ["'three' is not of type 'integer'"]
    assert errors({"lower": "ignored", "token": 5}) == ["5 is not of type 'string'"]
    assert errors("not an object") == ["'not an object' is not of type 'object'"]


def test_model_of():
    assert sv.model_of({"plan-of-action-and-milestones": {}}) == "poam"
    with pytest.raises(KeyError, match="not an OSCAL document"):
        sv.model_of({"something": {}})


def test_unknown_model():
    with pytest.raises(KeyError, match="unknown OSCAL model"):
        sv.load_schema(Path(REPO_ROOT), "component")


def test_all_patterns_walks_lists_and_pattern_properties():
    tree = {"anyOf": [{"pattern": "a"}, {"patternProperties": {"b": {"pattern": "c"}}}]}
    assert sorted(sv.all_patterns(tree)) == ["a", "b", "c"]
