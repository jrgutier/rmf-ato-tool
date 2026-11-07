"""CLOUD-* and HOST-001 beyond their negative fixtures: the cases the sources permit, Table 1
against the text of DTM 24-001, and the DCRT release key."""

import json
import re

import jsonschema
import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check import engine
from rmf_tool.check.rules import cloud
from rmf_tool.run.model import open_run

TEXT = REPO_ROOT / "references/text/DTM-24-001.md"
STAR = "\uf0e9"  # the "CSSP must perform" star, extracted as a private-use code point
# The first line of each activity's row name on p. 9 of DTM 24-001 Table 1.
P9_ROWS = {
    "AS&W for Boundary Cyberspace": "asw-boundary", "AS&W at the Application": "asw-application",
    "Warning Intelligence": "warning-intelligence",
    "Maintain continuous visibility into": "endpoint-visibility",
    "Correlate asset and vulnerability data": "correlate-threat-data",
    "Malware Notification": "malware-notification",
    "Network Security Monitoring and": "nsm-boundary",
    "Network and Endpoint Security": "enclave-monitoring",
    "Employ UAM capabilities to detect": "uam-detect",
    "Maintain insider threat audit data": "uam-audit-data",
    "Correlate insider threat audit data with": "uam-correlate",
    "CPCON and Orders Implementation": "cpcon-implementation",
    "CPCON and Orders Notification and": "cpcon-notification",
    "Incident Categorization": "incident-categorization",
    "Incident Reporting": "incident-reporting",
    "Incident Handling Response": "incident-handling",
    "Incident Response – Law Enforcement (LE)": "incident-law-enforcement",
    "Incident Response – Counterintelligence": "incident-counterintelligence",
    "Incident Response – Analysis": "incident-analysis",
}


def _page9_cells() -> dict[str, list[str]]:
    text = TEXT.read_text(encoding="utf-8")
    page = text.split("<!-- page 9 -->")[1].split("<!-- page 10 -->")[0]
    rows = {}
    for line in page.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 12 and cells[2] in P9_ROWS:
            rows[P9_ROWS[cells[2]]] = cells[3:]
    return rows


def test_table_1_page_9_matches_the_text():
    """L-0077: the CSSP star is extracted as a private-use code point that shows as blank; each
    row's marks must match its TABLE_1 key."""
    rows = _page9_cells()
    assert set(rows) == set(P9_ROWS.values())
    for activity, cells in rows.items():
        marks = {c for c in cells if c != "N/A"}
        key = cloud.TABLE_1[activity]
        if marks == {STAR}:
            assert key == cloud.CSSP, activity
        elif marks == {"●"}:
            assert key == cloud.DOW, activity
        elif marks == {"ο"}:
            assert key == cloud.ANY, activity
        else:  # UAM detection: open circles, DoW only at IL 6
            assert activity in cloud.IL6_DOW and [c == "●" for c in cells] == [
                False, False, True] * 3, activity
        assert ("N/A" in cells) == (activity in cloud.IL2_NOT_APPLICABLE), activity
    assert {a for a, k in cloud.TABLE_1.items() if k == cloud.CSSP} <= set(rows)


def _host_errors(tmp_path, edit):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/boundary.yaml", lambda d: edit(d["hosting"]))
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule == "HOST-001"]


def _in_existing_enclave(hosting):
    """Encl 3.d: hosted in an existing authorized enclave, still a major application by design."""
    hosting["environment"] = "existing-enclave"


def _cloud_first(hosting):
    """DoDI 5000.82 3.7.b: cloud first, recorded as decc: cloud."""
    hosting["environment"] = "cloud"
    hosting["decc"]["status"] = "cloud"
    hosting["cloud"]["assessment"] = "cloud-hosted"


@pytest.mark.parametrize("edit", [_in_existing_enclave, _cloud_first])
def test_host_001_permits_what_the_sources_allow(tmp_path, edit):
    found = _host_errors(tmp_path, edit)
    assert not [m for m in found if "Defense Enterprise Computing Center when" in m]
    assert not [m for m in found if "is designated a major application" in m]


def test_host_001_judges_the_designation_only_while_developed(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["lifecycle_state"].__setitem__("value", "operational"))
    edit_yaml(run_dir / "artifacts/data/boundary.yaml",
              lambda d: d["hosting"]["enclave_application"].__setitem__("status", "possible"))
    run = open_run(run_dir, REPO_ROOT)
    assert not [f for f in engine.evaluate(run).findings if f.rule == "HOST-001"
                and "designated a major application" in f.finding.message]


def test_dcrt_report_states_its_release_even_while_pending():
    schema = json.loads((REPO_ROOT / "framework/schema/cloud.schema.json").read_text())
    report = schema["properties"]["external_assessments"]["properties"]["dcrt_reports"]["items"]
    validator = jsonschema.Draft202012Validator({**report, "$defs": schema["$defs"]})
    pending = {"id": "DCRT-01", "briefed": "2026-07-01", "released_to_jfhq_dodin": None,
               "covers": ["all-findings"]}
    assert list(validator.iter_errors(pending)) == []
    silent = {k: v for k, v in pending.items() if k != "released_to_jfhq_dodin"}
    assert [e.message for e in validator.iter_errors(silent)]
    assert re.search(r"released_to_jfhq_dodin",
                     " ".join(e.message for e in validator.iter_errors(silent)))
