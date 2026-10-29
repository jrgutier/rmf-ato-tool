"""`rmf refs verify` (REF-001, REF-002, REF-005, REF-006) and the text check behind
`rmf refs extract --check` (REF-003). Offline: never touches the network.

REF-001 severity (plan §5.0, §7.6): ``pending-acquisition`` on a required entry is a
warning before the p2x gate (``strict=False``) and an error at it (``strict=True``);
``degraded`` (with the user's approval, enforced by the schema) is always a warning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rmf_tool.findings import Finding
from rmf_tool.oscal import version as oscal_version
from rmf_tool.refs import INDEX_PATH, lfs_pointer_oid, sha256_file
from rmf_tool.refs.domains import disallowed_reason
from rmf_tool.refs.required import REQUIRED_IDS

VERIFY_RULES = ("REF-001", "REF-002", "REF-005", "REF-006")


def _ref001(entry: Any, strict: bool) -> Finding | None:
    status = entry["status"]
    if status == "ok":
        return None
    if status == "degraded":
        reason = entry["degraded"]["reason"]
        return Finding("REF-001", "W", f"{entry['id']}: degraded ({reason})", INDEX_PATH)
    must_have = entry["required"] or entry["acquisition"] == "auto"
    if status == "pending-acquisition":
        sev = "E" if strict and entry["required"] else "W"
        hint = "import it per playbooks/_ops/fetch-blocked-refs.md"
    else:
        sev = "E" if must_have else "W"
        hint = "run rmf refs fetch" if entry["acquisition"] == "auto" else "run rmf refs import"
    return Finding("REF-001", sev, f"{entry['id']}: status {status} ({hint})", INDEX_PATH)


def _ref002(root: Path, entry: Any) -> Finding | None:
    rel = entry["local_path"]
    if entry["status"] not in ("ok", "degraded") or not rel or not entry["sha256"]:
        return None
    path = root / rel
    if not path.is_file():
        return Finding("REF-002", "E", f"{entry['id']}: file missing", rel)
    actual = lfs_pointer_oid(path) or sha256_file(path)
    if actual != entry["sha256"]:
        return Finding("REF-002", "E",
                       f"{entry['id']}: sha256 {actual} != pinned {entry['sha256']}", rel)
    return None


def _ref006(entry: Any) -> list[Finding]:
    urls = [*entry["urls"], entry["landing_url"], entry["resolved_url"]]
    out = []
    for url in filter(None, urls):
        # resolved_url may be a release-asset host reached by a redirect from github.com.
        via = entry["urls"][0] if url == entry["resolved_url"] and entry["urls"] else None
        reason = disallowed_reason(url, redirected_from=via)
        if reason:
            out.append(Finding("REF-006", "E", f"{entry['id']}: {url}: {reason}", INDEX_PATH))
    return out


def verify(root: Path, index: Any, *, strict: bool = False, required_only: bool = False,
           ids: list[str] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    marked = {e["id"] for e in index["references"] if e["required"]}
    if marked != set(REQUIRED_IDS):
        missing, extra = sorted(set(REQUIRED_IDS) - marked), sorted(marked - set(REQUIRED_IDS))
        findings.append(Finding(
            "REF-001", "E",
            f"required set differs from rmf_tool.refs.required (not marked required: "
            f"{', '.join(missing) or 'none'}; unexpectedly required: {', '.join(extra) or 'none'})",
            INDEX_PATH))
    for entry in index["references"]:
        if (ids and entry["id"] not in ids) or (required_only and not entry["required"]):
            continue
        for f in (_ref001(entry, strict), _ref002(root, entry)):
            if f is not None:
                findings.append(f)
        findings += _ref006(entry)
    if not required_only and not ids:
        findings += oscal_version.check(root, index)
    return findings


def check_texts(root: Path, index: Any, ids: list[str] | None = None) -> list[Finding]:
    """REF-003 without re-extracting: every ok PDF has a current text extraction whose
    bytes match the recorded text sha256 (checked by extract.check)."""
    from rmf_tool.refs import extract

    findings: list[Finding] = []
    for entry in index["references"]:
        if entry["kind"] != "pdf" or entry["status"] != "ok" or (ids and entry["id"] not in ids):
            continue
        ref_id, text = entry["id"], entry.get("text")
        if not text:
            findings.append(Finding(
                "REF-003", "E", f"{ref_id}: no text extraction (rmf refs extract --id {ref_id})",
                INDEX_PATH))
            continue
        problems = extract.check(ref_id, root / entry["local_path"],
                                 root / Path(text["path"]).parent,
                                 source_sha256=entry["sha256"], extractor=text["extractor"],
                                 text_sha256=text["sha256"])
        if text.get("source_sha256") != entry["sha256"]:
            problems.append(f"{ref_id}: index text.source_sha256 does not match the PDF sha256")
        findings += [Finding("REF-003", "E", p, text["path"]) for p in problems]
    return findings
