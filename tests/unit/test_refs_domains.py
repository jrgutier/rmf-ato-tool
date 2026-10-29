import pytest

from rmf_tool.refs.domains import ALLOWED_DOMAINS, disallowed_reason, is_allowed

GH = "https://github.com/usnistgov/OSCAL/releases/download/v1.2.1/oscal_ssp_schema.json"
ASSET = "https://release-assets.githubusercontent.com/github-production-release-asset/1/x"


@pytest.mark.parametrize("url", [
    "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-37r2.pdf",
    "https://csrc.nist.gov/pubs/sp/800/37/r2/final",
    "https://nist.gov/x",
    "https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/851001p.pdf",
    "https://www.cnss.gov/CNSS/issuances/Instructions.cfm",
    "https://public.cyber.mil/stigs/",
    "https://dodcio.defense.gov/Library/",
    GH,
    "https://raw.githubusercontent.com/usnistgov/oscal-content/v1.6.0/x.json",
])
def test_allowed(url):
    assert is_allowed(url), disallowed_reason(url)


@pytest.mark.parametrize("url,why", [
    ("http://nvlpubs.nist.gov/a.pdf", "not https"),
    ("https://evilnist.gov/a.pdf", "not an allowed domain"),
    ("https://nist.gov.evil.com/a.pdf", "not an allowed domain"),
    ("https://github.com/someone/OSCAL/x", "path outside"),
    ("https://raw.githubusercontent.com/other/oscal-content/x", "path outside"),
    (ASSET, "only as a redirect target"),
    ("not a url", "not https"),
])
def test_disallowed(url, why):
    assert why in disallowed_reason(url)


def test_release_assets_only_via_usnistgov_redirect():
    assert is_allowed(ASSET, redirected_from=GH)
    assert not is_allowed(ASSET, redirected_from="https://github.com/evil/x")
    assert not is_allowed(ASSET, redirected_from="https://nvlpubs.nist.gov/x")


def test_allowed_domains_constant():
    assert ALLOWED_DOMAINS == ("nist.gov", "esd.whs.mil", "cnss.gov", "public.cyber.mil",
                               "dodcio.defense.gov")
