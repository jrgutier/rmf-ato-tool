"""OSCAL version pins and REF-005 (plan PM-3, L-0004).

Generated documents are stamped ``OSCAL_VERSION``, the version compliance-trestle 5.2.0
accepts. Input catalogs and profiles from NIST oscal-content may be any ``1.2.x``
(same minor) and are always read as raw JSON, never through trestle models.
"""

from __future__ import annotations

import importlib.metadata
import json
import re
from pathlib import Path
from typing import Any

from rmf_tool.findings import Finding
from rmf_tool.yamlload import safe_load

OSCAL_VERSION = "1.2.1"
TRESTLE_VERSION = "5.2.0"
SCHEMA_TAG = "v1.2.1"
CONTENT_TAG = "v1.6.0"
CONTENT_FALLBACK_TAG = "v1.5.0"
INPUT_MINOR = "1.2"
VERSIONS_PATH = "references/oscal/VERSIONS.yaml"

CONTENT_KINDS = ("oscal-catalog", "oscal-profile", "oscal-resolved-catalog", "oscal-example")
_ROOT_KEYS = ("catalog", "profile", "system-security-plan")


def same_minor(version: str, minor: str = INPUT_MINOR) -> bool:
    return re.fullmatch(re.escape(minor) + r"\.\d+", version) is not None


def document_version(doc: dict[str, Any]) -> str | None:
    """``metadata.oscal-version`` of an OSCAL document (any root model)."""
    for key in _ROOT_KEYS:
        if key in doc:
            return doc[key].get("metadata", {}).get("oscal-version")
    return None


def _trestle_version() -> tuple[str | None, str | None]:
    try:
        from trestle.oscal import OSCAL_VERSION as trestle_oscal
    except ImportError:
        return None, None
    return importlib.metadata.version("compliance-trestle"), trestle_oscal


def check(root: Path, index: Any) -> list[Finding]:
    """REF-005: VERSIONS.yaml, the constants above, trestle, index URLs and file contents
    all agree."""
    findings: list[Finding] = []

    def err(msg: str, path: str | None = VERSIONS_PATH) -> None:
        findings.append(Finding("REF-005", "E", msg, path))

    vpath = root / VERSIONS_PATH
    if not vpath.is_file():
        err("file not found")
        return findings
    pins = safe_load(vpath.read_text(encoding="utf-8"))
    expected = {
        "generated_oscal_version": OSCAL_VERSION,
        "compliance_trestle": TRESTLE_VERSION,
        "input_minor": INPUT_MINOR,
    }
    for key, want in expected.items():
        if str(pins.get(key)) != want:
            err(f"{key} is {pins.get(key)!r}; rmf_tool.oscal.version pins {want!r}")
    if pins.get("schemas", {}).get("tag") != SCHEMA_TAG:
        err(f"schemas.tag must be {SCHEMA_TAG}")
    if pins.get("content", {}).get("tag") not in (CONTENT_TAG, CONTENT_FALLBACK_TAG):
        err(f"content.tag must be {CONTENT_TAG} (fallback {CONTENT_FALLBACK_TAG})")
    if SCHEMA_TAG.lstrip("v") != OSCAL_VERSION:
        err(f"schema tag {SCHEMA_TAG} does not match OSCAL_VERSION {OSCAL_VERSION}")

    installed, trestle_oscal = _trestle_version()
    if installed != TRESTLE_VERSION or trestle_oscal != OSCAL_VERSION:
        err(f"installed compliance-trestle {installed} (OSCAL {trestle_oscal}); "
            f"expected {TRESTLE_VERSION} (OSCAL {OSCAL_VERSION})", None)

    inputs = {str(k): str(v) for k, v in (pins.get("inputs") or {}).items()}
    content_tag = pins.get("content", {}).get("tag", CONTENT_TAG)
    seen: set[str] = set()
    for entry in index["references"]:
        kind, rel = entry["kind"], entry["local_path"]
        if kind == "oscal-schema":
            tag = SCHEMA_TAG
        elif kind in CONTENT_KINDS:
            tag = content_tag
            seen.add(rel)
        else:
            continue
        for url in entry["urls"]:
            if f"/{tag}/" not in url:
                err(f"{entry['id']}: URL {url} is not pinned to {tag}", "references/index.yaml")
        path = root / rel
        if entry["status"] != "ok" or not path.is_file():
            continue  # REF-001/REF-002 report missing files
        try:
            doc = json.loads(path.read_bytes())
        except ValueError as exc:
            err(f"not valid JSON: {exc}", rel)
            continue
        if kind == "oscal-schema":
            if f"/oscal/{OSCAL_VERSION}/" not in str(doc.get("$id", "")):
                err(f"$id {doc.get('$id')!r} is not an OSCAL {OSCAL_VERSION} schema", rel)
            continue
        version = document_version(doc)
        if version is None or not same_minor(version):
            err(f"oscal-version {version!r} is not {INPUT_MINOR}.x", rel)
        if inputs.get(rel) != version:
            err(f"VERSIONS.yaml inputs records {inputs.get(rel)!r} for {rel}; "
                f"the file is {version!r}")
    for rel in sorted(set(inputs) - seen):
        err(f"inputs lists {rel}, which is not an OSCAL content entry in index.yaml")
    return findings
