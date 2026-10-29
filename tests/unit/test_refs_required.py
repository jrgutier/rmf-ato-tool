from pathlib import Path

from conftest import REPO_ROOT

from rmf_tool import refs
from rmf_tool.refs.required import REQUIRED_IDS

# AC-1 as written in the plan, plus SP800-18R2: NIST published Rev. 2 in June 2026 and
# withdrew Rev. 1 (the plan's "check for r2" step).
AC1 = {
    "SP800-37R2", "SP800-53R5", "SP800-53AR5", "SP800-53B", "SP800-30R1", "SP800-39",
    "SP800-60V1R1", "SP800-60V2R1", "SP800-137", "SP800-18R1", "SP800-18R2", "SP800-34R1",
    "SP800-61R3", "SP800-128", "SP800-160V1R1", "FIPS199", "FIPS200", "DODI8510.01",
    "CNSSI1253", "DODI5000.02", "DODI5000.85", "DODI5000.87", "DODI5000.80", "DODI5000.88",
    "DODCIO-CATO",
}


def test_required_reference_ids_pinned():
    assert len(REQUIRED_IDS) == len(set(REQUIRED_IDS))
    assert set(REQUIRED_IDS) == AC1


def test_index_marks_exactly_the_required_set():
    index = refs.load_index(Path(REPO_ROOT))
    assert {e["id"] for e in index["references"] if e["required"]} == set(REQUIRED_IDS)


def test_required_entries_are_pdfs_with_local_paths():
    index = refs.load_index(Path(REPO_ROOT))
    for e in index["references"]:
        if e["required"]:
            assert e["kind"] == "pdf" and e["local_path"] == f"references/pdf/{e['id']}.pdf"
