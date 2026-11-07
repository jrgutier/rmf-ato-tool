"""framework/baselines/cnssi-1253-parameters.yaml: the Parameter Value column of CNSSI 1253
Appendix D, regenerated from the PDF, mapped to catalog parameters, with comparable bounds."""

import re

import pytest
from conftest import REPO_ROOT

from rmf_tool import cnssi1253_params as params


@pytest.fixture(scope="module")
def values():
    return params.load(REPO_ROOT)


def _by_label(values, control):
    return {v.get("label", ""): v for v in values[control]}


def test_committed_yaml_is_regenerated_output():
    pytest.importorskip("pymupdf")  # PDF geometry needs the optional [extract] extra (L-0038)
    result = params.generate(REPO_ROOT)
    assert (REPO_ROOT / params.YAML_PATH).read_text(encoding="utf-8") == result.text
    assert params.main(["--check", "--repo", str(REPO_ROOT)]) == 0


def test_ra5_scan_frequency(values):
    # RA-5 a.: "Monitor and scan ... [frequency]", one aggregate for monitoring and scanning
    assert _by_label(values, "ra-5")["a."] == {
        "label": "a.", "params": ["ra-05_odp.01", "ra-05_odp.02"],
        "value": "at least every 30 days", "bound": "max"}


def test_ac2_item_labels(values):
    ac2 = _by_label(values, "ac-2")
    assert {k: (v["params"], v["value"]) for k, v in ac2.items()} == {
        "h.1.": (["ac-02_odp.06"], "24 hours"),
        "h.2.": (["ac-02_odp.07"], "24 hours"),
        "h.3.": (["ac-02_odp.08"], "24 hours"),
        "j.": (["ac-02_odp.10"], "at least quarterly"),
    }


def test_ordinals_follow_the_printed_order(values):
    # SC-24 prints known state, state information, failures; the ODP numbers do not
    sc24 = _by_label(values, "sc-24")
    assert [sc24[f"{n} PV:"]["params"] for n in ("1st", "2nd", "3rd")] == [
        ["sc-24_odp.02"], ["sc-24_odp.03"], ["sc-24_odp.01"]]
    assert sc24["1st PV:"]["value"] == "known secure state"
    ac22 = _by_label(values, "ac-2.2")
    assert ac22["1st PV:"]["params"] == ["ac-02.02_odp.01"]
    assert ac22["2nd PV:"] == {"label": "2nd PV:", "params": ["ac-02.02_odp.02"],
                               "value": "not to exceed 72 hours", "bound": "max"}
    # an ordinal within items: the 1st parameter of c.1 and of c.2
    assert _by_label(values, "ac-1")["c.1., c.2. 1st PV:"]["params"] == [
        "ac-01_odp.05", "ac-01_odp.07"]


def test_looser():
    nss = {"value": "at least every 30 days", "bound": "max"}
    assert params.looser("at least monthly when connected", nss) is True
    assert params.looser("at least every 7 days", nss) is False
    assert params.looser("weekly", nss) is False
    assert params.looser("as needed", nss) is None
    length = {"value": "a case sensitive 12-character mix", "bound": "min"}
    assert params.looser("8 characters", length) is True
    assert params.looser("15-character", length) is False
    assert params.looser("8 characters", nss) is None


def test_every_row_with_a_value_in_the_text_is_transcribed(values):
    """An independent recount from the text extraction: the Parameter Value cell of each
    row, located by the header's column on its page."""
    with_value, unread, page_cols = set(), set(), None
    current = None
    for line in (REPO_ROOT / params.TEXT_PATH).read_text(encoding="utf-8").splitlines():
        if line.startswith("<!-- page"):
            page_cols, current = None, None
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip()[1:-1].split("|")]
        if "Parameter Value" in cells:
            page_cols = (cells.index("Parameter Value"), len(cells))
            continue
        ident = next((c for c in cells[:3] if re.fullmatch(r"[A-Z]{2}-\d+(\(\d+\))?", c)), None)
        if ident:
            current = ident
            if page_cols is None or len(cells) != page_cols[1]:
                unread.add(ident)  # a page without its header row (one row runs over)
                current = None
                continue
        if current and len(cells) == page_cols[1] and cells[page_cols[0]]:
            with_value.add(current)
    transcribed = {params.oscal_id(i) for i in with_value | unread} & set(values)
    assert len(unread) == 2
    assert {params.oscal_id(i) for i in with_value} == set(values) - {
        params.oscal_id(i) for i in unread}
    assert transcribed == set(values)
    assert len(values) == 162


@pytest.mark.parametrize(("run", "nss", "loose"), [
    ("same day", "not to exceed 5 working days", False),
    ("immediately", "2 hours", False),
    ("real time", "continuously", False),
    ("3 times per month", "at least every 30 days", False),
    ("1 business day", "at least every 30 days", False),
    ("semi-annually", "at least quarterly", True),
    ("bi-weekly", "at least weekly", True),
])
def test_stricter_words_are_read_not_refused(run, nss, loose):
    """Fable F3: a stricter value in words PVAL-001 once could not read was an error."""
    assert params.looser(run, {"value": nss, "bound": "max"}) is loose
