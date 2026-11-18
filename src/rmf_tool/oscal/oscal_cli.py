"""OSCAL-003: NIST's ``oscal-cli validate`` (metaschema-framework/oscal-cli), optional.

OSCAL-001 checks the JSON schema and OSCAL-002 the trestle model; neither evaluates the
Metaschema constraints the JSON schema cannot express: allowed values (prop names, part names),
index and key references (a ``role-id`` defined in ``metadata.roles``, a ``party-uuid`` defined
in ``metadata.parties``), uniqueness and cardinality. ``oscal-cli`` does, so it runs as a third,
optional check when it is installed (Java 11 or later). Its findings are warnings: the tool is
not a pinned dependency, and its constraint set moves with its release.

Discovery: ``RMF_OSCAL_CLI`` names the executable (a path or a name on PATH), or ``off`` to turn
the check off; without it, ``rmf oscal validate`` looks for ``oscal-cli`` on PATH and then in
``.tools/oscal-cli/`` (where ``OSCAL_CLI=1 make bootstrap`` puts it), while
``rmf check`` runs OSCAL-003 only when ``RMF_OSCAL_CLI`` is set, so the reports a run commits do
not depend on what happens to be installed.

A profile is not passed to oscal-cli: validating it resolves its import, which fetches the
remote NIST catalog the generated profile names (minutes, and a network call ``rmf check`` never
makes); OSCAL-001 and OSCAL-002 cover the profile's one include list.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENV = "RMF_OSCAL_CLI"
OFF = "off"
EXECUTABLE = "oscal-cli"
BOOTSTRAPPED = ".tools/oscal-cli/bin/oscal-cli"  # relative to the repository root
TIMEOUT = 300  # seconds per document
SKIPPED_MODELS = frozenset({"profile"})
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


@dataclass(frozen=True)
class Located:
    """Where the oscal-cli executable is, or why it is not used."""

    path: str | None
    note: str  # a one-line reason, shown when ``path`` is None


def locate(path_lookup: bool = True, root: Path | None = None) -> Located:
    """The oscal-cli to run: ``RMF_OSCAL_CLI``, else (with ``path_lookup``) ``oscal-cli`` on
    PATH, else the bootstrapped copy under ``root``. A set ``RMF_OSCAL_CLI`` that does not
    resolve is a note, never a silent skip."""
    env = os.environ.get(ENV, "").strip()
    if env.lower() == OFF:
        return Located(None, f"{ENV}=off: OSCAL-003 skipped")
    if env:
        found = shutil.which(env)
        if found is None:
            return Located(None, f"{ENV}={env} is not an executable: OSCAL-003 skipped")
        return Located(found, "")
    if not path_lookup:
        return Located(None, f"{ENV} not set: OSCAL-003 skipped")
    found = shutil.which(EXECUTABLE)
    if found is None and root is not None and os.access(root / BOOTSTRAPPED, os.X_OK):
        found = str(root / BOOTSTRAPPED)
    if found is None:
        return Located(None, f"{EXECUTABLE} not found on PATH or in .tools/ (optional): "
                       "OSCAL-003 skipped")
    return Located(found, "")


def _results(sarif: dict[str, Any]) -> list[tuple[str, str]]:
    """(oscal-cli rule ID, message) per failed constraint in a SARIF log."""
    out = []
    for run in sarif.get("runs") or []:
        for result in run.get("results") or []:
            if result.get("kind", "fail") != "fail":
                continue
            rule = result.get("ruleId") or "schema"
            text = " ".join(str((result.get("message") or {}).get("text", "")).split())
            out.append((rule, text))
    return out


def _grouped(results: list[tuple[str, str]]) -> list[str]:
    """One message per oscal-cli rule: its first occurrence and how many more there are, so a
    constraint broken on every control reads as one finding, not hundreds."""
    first: dict[str, str] = {}
    count: dict[str, int] = {}
    for rule, text in results:
        first.setdefault(rule, text)
        count[rule] = count.get(rule, 0) + 1
    out = []
    for rule in sorted(first):
        more = count[rule] - 1
        tail = f" (and {more} more like it)" if more else ""
        out.append(f"oscal-cli {rule}: {first[rule][:300]}{tail}")
    return out


def _last_line(text: str) -> str:
    lines = [ln for ln in _ANSI.sub("", text).splitlines()
             if ln.strip() and not ln.startswith("Picked up ")]
    return lines[-1].strip()[:300] if lines else "no output"


def problems(exe: str, path: Path) -> list[str]:
    """oscal-cli's failed constraints for one document, grouped per oscal-cli rule; a run that
    neither passes nor writes its SARIF log is one message naming what it printed."""
    with tempfile.TemporaryDirectory(prefix="rmf-oscal-cli-") as tmp:
        sarif_path = Path(tmp) / "result.sarif"
        argv = [exe, "validate", "--quiet", "--no-color", "-o", str(sarif_path), str(path)]
        try:
            proc = subprocess.run(argv, capture_output=True, text=True, check=False,
                                  timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return [f"oscal-cli did not finish within {TIMEOUT} s"]
        except OSError as exc:
            return [f"oscal-cli cannot run: {exc}"]
        results: list[tuple[str, str]] = []
        if sarif_path.is_file():
            try:
                results = _results(json.loads(sarif_path.read_text(encoding="utf-8")))
            except (ValueError, AttributeError) as exc:
                return [f"oscal-cli wrote an unreadable SARIF log: {exc}"]
        if results:
            return _grouped(results)
        if proc.returncode == 0:
            return []
        return [f"oscal-cli exited {proc.returncode}: "
                f"{_last_line(proc.stderr + chr(10) + proc.stdout)}"]
