"""`rmf build <run>` (plan §7.5 step 5): assemble the artifact Markdown, build the OSCAL
documents that the run's data supports, render the assumptions report, and refresh the
package manifest when one exists. ``generated()`` is the same pipeline in memory; GEN-STALE-001
compares it with disk, so a build followed by a check never reports staleness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rmf_tool import assemble, package
from rmf_tool.oscal.build_poam import POAM_FILE, build_poam
from rmf_tool.oscal.build_sap import SAP_FILE, build_sap
from rmf_tool.oscal.build_sar import SAR_FILE, build_sar
from rmf_tool.oscal.build_ssp import PROFILE_FILE, SSP_FILE, NotBuildable, build_profile, build_ssp
from rmf_tool.run import assumptions, interviews, poam_dates
from rmf_tool.run.model import Run


@dataclass
class Generated:
    files: dict[str, str | None] = field(default_factory=dict)  # path -> text, None: absent
    notes: dict[str, str] = field(default_factory=dict)  # path -> why it is not built


def oscal_outputs(run: Run) -> Generated:
    out = Generated()
    for rel, builder in ((PROFILE_FILE, build_profile), (SSP_FILE, build_ssp),
                         (SAP_FILE, build_sap), (SAR_FILE, build_sar), (POAM_FILE, build_poam)):
        try:
            out.files[rel] = builder(run)
        except NotBuildable as exc:
            out.files[rel] = None
            out.notes[rel] = str(exc)
    if out.files[PROFILE_FILE] is None:
        out.notes.setdefault(PROFILE_FILE, "baseline.json missing (rmf baseline resolve)")
    return out


def assumptions_report(run: Run) -> str:
    items, _ = assumptions.load(run)
    return assumptions.render(run, items, interviews.load_all(run))


def write_output(run: Run, rel: str, text: str | None) -> bool:
    path = run.path(rel)
    if text is None:
        if path.is_file():
            path.unlink()
            return True
        return False
    # compared as bytes: a generated file that is no longer text is rewritten, not a crash
    if path.is_file() and path.read_bytes() == text.encode("utf-8"):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def build(run: Run) -> tuple[list[str], dict[str, str]]:
    """Write every generated file; returns (changed paths, not-built notes)."""
    changed = assemble.write(run)
    frozen = poam_dates.freeze(run)
    if frozen is not None and write_output(run, poam_dates.ORIGINAL_FILE, frozen):
        changed.append(poam_dates.ORIGINAL_FILE)
    oscal = oscal_outputs(run)
    for rel, text in oscal.files.items():
        if write_output(run, rel, text):
            changed.append(rel)
    if write_output(run, assumptions.REPORT_FILE, assumptions_report(run)):
        changed.append(assumptions.REPORT_FILE)
    if run.path(package.MANIFEST_FILE).is_file() and package.write(run):
        changed.append(package.MANIFEST_FILE)
    return changed, oscal.notes
