"""AC-2 and PM-3: the pinned NIST OSCAL content and schemas are present, consistent and
usable with the regex-backed validator."""

import copy
import json
import re
from pathlib import Path

import pytest
import regex
from conftest import REPO_ROOT

from rmf_tool import refs
from rmf_tool.oscal import schema_validate as sv
from rmf_tool.oscal import version

ROOT = Path(REPO_ROOT)
OSCAL = ROOT / "references/oscal"
BASELINES = ("LOW", "MODERATE", "HIGH", "PRIVACY")


def load(rel):
    return json.loads((OSCAL / rel).read_text(encoding="utf-8"))


def control_ids(controls):
    for c in controls:
        yield c["id"]
        yield from control_ids(c.get("controls", []))


def resolved_ids(catalog):
    return [cid for g in catalog["catalog"].get("groups", [])
            for cid in control_ids(g.get("controls", []))]


@pytest.fixture(scope="module")
def example_ssp():
    return load("examples/ssp-example.json")


def test_catalog_and_profiles_present():
    assert "catalog" in load("catalog/NIST_SP-800-53_rev5_catalog.json")
    for b in BASELINES:
        assert "profile" in load(f"profiles/NIST_SP-800-53_rev5_{b}-baseline_profile.json")
        resolved = load(f"profiles/NIST_SP-800-53_rev5_{b}-baseline-resolved-profile_catalog.json")
        assert "catalog" in resolved
    for model in sv.SCHEMA_FILES:
        assert (OSCAL / "schemas" / sv.SCHEMA_FILES[model]).is_file()


def test_oscal_versions_consistent():
    """REF-005: generated version == trestle == schemas (1.2.1); inputs are 1.2.x and
    match VERSIONS.yaml; every URL carries its pinned tag."""
    assert version.check(ROOT, refs.load_index(ROOT)) == []
    from trestle.oscal import OSCAL_VERSION as trestle_version

    assert trestle_version == version.OSCAL_VERSION == version.SCHEMA_TAG.lstrip("v")


def test_all_schema_patterns_compile():
    patterns = set()
    for name in sv.SCHEMA_FILES.values():
        patterns |= set(sv.all_patterns(json.loads((OSCAL / "schemas" / name).read_text())))
    assert patterns
    for p in patterns:
        regex.compile(p)
    stdlib_failures = []
    for p in patterns:
        try:
            re.compile(p)
        except re.error:
            stdlib_failures.append(p)
    # Documents why the regex engine is needed (L-0005): \p{L} in TokenDatatype.
    assert any(r"\p{L}" in p for p in stdlib_failures)


def test_format_checker_enforced(example_ssp):
    bad = copy.deepcopy(example_ssp)
    ssp = bad["system-security-plan"]
    ssp["metadata"]["last-modified"] = "2026-02-30T10:00:00Z"
    ssp["uuid"] = "not-a-uuid"
    ssp["import-profile"]["href"] = "has a space"  # passes every pattern; only format fails

    errors = {("/".join(map(str, e.absolute_path)), e.validator)
              for e in sv.validate(ROOT, bad)}

    assert ("system-security-plan/metadata/last-modified", "format") in errors
    assert ("system-security-plan/uuid", "pattern") in errors
    assert ("system-security-plan/import-profile/href", "format") in errors


def test_nist_example_ssp_validates(example_ssp):
    assert [sv.describe(e) for e in sv.validate(ROOT, example_ssp)] == []


@pytest.mark.parametrize("rel", [
    "profiles/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json",
    "profiles/NIST_SP-800-53_rev5_MODERATE-baseline-resolved-profile_catalog.json",
])
def test_catalog_and_profiles_validate(rel):
    assert [sv.describe(e) for e in sv.validate(ROOT, load(rel))] == []


def test_moderate_resolved_count():
    profile = load("profiles/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json")
    selected = [i for inc in profile["profile"]["imports"][0]["include-controls"]
                for i in inc["with-ids"]]
    resolved = resolved_ids(
        load("profiles/NIST_SP-800-53_rev5_MODERATE-baseline-resolved-profile_catalog.json"))
    assert len(selected) == len(resolved) == 287
    assert set(selected) == set(resolved)
