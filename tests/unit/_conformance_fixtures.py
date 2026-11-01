"""A synthetic conformance repository for the FW-REQ rule tests.

The real register changes at every phase, so tests that pin its entries, work items and
waivers break as the work proceeds. These helpers build a small register from a two-page
document and the real schemas; each test mutates its own copy.
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any

from conftest import REPO_ROOT

from rmf_tool.conformance import register

DOC = "DOC"
TIER1 = "TIERONE"
PENDING = "PENDING"
SOURCE_TEXT = """<!-- page 1 -->

## 2.1. OWNERS.

The owner:

a. Will register the system with the component registry before use.

b. Will retire the system when its authorization ends.

The authorizing official must approve every registration. Assessors may reuse prior results.

<!-- page 2 -->

Appendix A references, which the register never reads.
"""
TIER1_TEXT = """<!-- page 1 -->

a. The head of the agency must appoint an authorizing official for every system.
"""
INDEX: dict[str, dict[str, Any]] = {
    DOC: {"id": DOC, "kind": "pdf", "status": "ok", "text": {"path": f"references/text/{DOC}.md"}},
    TIER1: {"id": TIER1, "kind": "pdf", "status": "ok", "tier": 1,
            "text": {"path": f"references/text/{TIER1}.md"}},
    PENDING: {"id": PENDING, "kind": "pdf", "status": "pending-acquisition", "tier": 1},
}
SOURCES = f"""schema_version: 1
documents:
  - ref: {DOC}
    mode: statement
    basis: A two-page test instruction.
    scopes:
      - {{pages: [1, 1], note: "The body"}}
    excluded:
      - {{pages: [2, 2], reason: "Appendix A references."}}
  - ref: {TIER1}
    mode: statement
    basis: A one-page tier 1 test instruction.
    scopes:
      - {{pages: [1, 1], note: "The body"}}
  - {{ref: {PENDING}, mode: statement, basis: "Pending acquisition; scopes at import."}}
reference_list:
  - {{document: Some Document, disposition: library, ref: {DOC}}}
"""
WORK_ITEMS = """schema_version: 1
work_items:
  - id: "WI-01"
    title: "Registration before use"
    findings: ["N-1"]
    status: "open"
  - id: "WI-02"
    title: "A repository defect"
    findings: ["C-1"]
    status: "closed"
    closed_by: "commit abc1234: fixed"
    scope: "internal"
    scope_reason: "A repository defect with no requirement entry behind it."
"""
EMPTY = {"triage.yaml": "schema_version: 1\npatterns: []\n",
         "policy.yaml": "schema_version: 1\nfan_out_exceptions: []\n"}


def build(tmp_path: Path) -> Path:
    """A repository under ``tmp_path`` with a freshly extracted register, WI-01 bound to the
    first entry, and every text hash accepted."""
    conformance = tmp_path / "conformance"
    shutil.copytree(REPO_ROOT / "conformance/schema", conformance / "schema")
    (tmp_path / "references/text").mkdir(parents=True)
    (tmp_path / f"references/text/{DOC}.md").write_text(SOURCE_TEXT, encoding="utf-8")
    (tmp_path / f"references/text/{TIER1}.md").write_text(TIER1_TEXT, encoding="utf-8")
    (conformance / "sources.yaml").write_text(SOURCES, encoding="utf-8")
    (conformance / "work-items.yaml").write_text(WORK_ITEMS, encoding="utf-8")
    for name, text in EMPTY.items():
        (conformance / name).write_text(text, encoding="utf-8")
    hashes = {ref: register.text_hash((tmp_path / INDEX[ref]["text"]["path"]).read_text())
              for ref in (DOC, TIER1)}
    (conformance / "text-hashes.yaml").write_text(register.render_text_hashes(hashes))
    extract(tmp_path)
    reg = register.load(tmp_path)
    register.mark(reg, f"REQ-{DOC}-0001", work_item="WI-01")
    write(tmp_path, reg)
    return tmp_path


def extract(repo: Path, only: str | None = None) -> None:
    reg = register.load(repo)
    assert not reg.problems, reg.problems
    for ref in (DOC, TIER1):
        if only in (None, ref):
            text = register.text_of(repo, INDEX[ref])
            register.write_requirements(repo, register.build(reg, reg.sources[ref], text).document)


def write(repo: Path, reg: register.Register) -> None:
    for doc in reg.files.values():
        doc["requirements"] = [{k: e[k] for k in register._ORDER if k in e}
                               for e in doc["requirements"]]
        register.write_requirements(repo, doc)


def load(repo: Path) -> register.Register:
    reg = register.load(repo)
    assert not reg.problems, reg.problems
    return reg


def entry(reg: register.Register, number: int = 1, ref: str = DOC) -> dict[str, Any]:
    found = reg.entry(f"REQ-{ref}-{number:04d}")
    assert found is not None
    return found


def index() -> dict[str, dict[str, Any]]:
    return copy.deepcopy(INDEX)
