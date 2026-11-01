from pathlib import Path

from conftest import REPO_ROOT

from rmf_tool import refs
from rmf_tool.refs.required import REQUIRED_IDS

# AC-1 as written in the plan, plus SP800-18R2: NIST published Rev. 2 in June 2026 and
# withdrew Rev. 1 (the plan's "check for r2" step).
AC1_ORIGINAL = {
    "SP800-37R2", "SP800-53R5", "SP800-53AR5", "SP800-53B", "SP800-30R1", "SP800-39",
    "SP800-60V1R1", "SP800-60V2R1", "SP800-137", "SP800-18R1", "SP800-18R2", "SP800-34R1",
    "SP800-61R3", "SP800-128", "SP800-160V1R1", "FIPS199", "FIPS200", "DODI8510.01",
    "CNSSI1253", "DODI5000.02", "DODI5000.85", "DODI5000.87", "DODI5000.80", "DODI5000.88",
    "DODCIO-CATO",
}
# Added at p9: SP800-161R1 (November 2024 update) and SP800-137A are now obtained; the other
# seven were already pinned and cited but marked required: false (FW-CITE-003).
P9_ADDED = {
    "SP800-161R1", "SP800-137A", "DODI5000.89", "DODI5000.90", "DODCIO-DEVSECOPS",
    "CNSSI1253F-ATT6-PRIVACY", "CNSSI1253F-ATT2-SPACE", "CNSSI1253E-ATT5-CLASSIFIED",
    "CNSSI1253E-ATT1-TEMPLATE",
}
# Imported from the operator downloads of 2026-10-31 (docs/audits/2026-10-31-operator-imports.md).
OPERATOR_IMPORTS = {
    "DODI5000.74", "DODI5000.75", "DODI5000.81", "DODI5000.82", "DODI5000.83", "DODI5400.11",
    "DODI5400.16", "DODD8140.01", "DOWI8430.01", "DODI8500.01", "DODI8530.01", "DODI8531.01",
    "DTM-24-001", "CNSSI1254", "CNSSI4009", "CNSSP12", "CNSSP22", "DODCIO-RECIPROCITY",
    "DODCIO-CATO-IG", "DODCIO-CATO-EVAL", "DODCIO-CSRMC", "DODCIO-CSRMC-TENETS",
}
AC1 = AC1_ORIGINAL | P9_ADDED | OPERATOR_IMPORTS


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


def test_p9_additions_are_obtained_pdfs():
    index = refs.load_index(Path(REPO_ROOT))
    for e in index["references"]:
        if e["id"] in P9_ADDED:
            assert e["status"] == "ok" and e["kind"] == "pdf"
