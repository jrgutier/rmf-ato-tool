# ADR-0006: allow media.defense.gov for the CSRMC PDFs

Date: 2026-10-31 · Status: accepted · Phase: 9

## Context

The DoD CIO published the Cybersecurity Risk Management Construct (CSRMC) and its strategic
tenets in September 2025. The candidate PDF URLs recorded in the index are on
`media.defense.gov`, the defense.gov media host, not on `dodcio.defense.gov`. Nothing has been
probed: the host, the URLs, whether an allowed domain also offers the documents, and the
documents' public release status are all unconfirmed until a person downloads them and the
maintainer reads them. `ALLOWED_DOMAINS` (REF-006) did not list that host, so an index entry
for them would have failed REF-006 and `rmf refs import --url` would have refused the URL.

## Decision

Add exactly `media.defense.gov` to `ALLOWED_DOMAINS` in `src/rmf_tool/refs/domains.py`. Its
only use is the two CSRMC entries (`DODCIO-CSRMC`, `DODCIO-CSRMC-TENETS`), acquired
browser-assisted as `playbooks/_ops/fetch-blocked-refs.md` describes. A host matches when it
equals a listed domain or is a subdomain of it, so `defense.gov`, `www.defense.gov` and
`dodcio.defense.gov` are unaffected: adding `media.defense.gov` does not allow its parent.

## Consistency with INV-7

INV-7 limits references to public documents from the allowed domains, fetched with TLS
verification on and no User-Agent spoofing. `media.defense.gov` is a DoD publishing host; that
the CSRMC documents are cleared for public release is expected, not confirmed, and the
maintainer checks the markings on each document at import. The entries are
`acquisition: browser-assisted`, so no script touches the host; a person downloads the file
and `rmf refs import` checks `%PDF-` and `qpdf --check`. No other defense.gov host is added.

## Consequences

- REF-006 now accepts `media.defense.gov` URLs, on every redirect hop.
- A future document on another defense.gov host needs its own ADR (INV-7 stays an
  allowlist, not a pattern).
- `tests/unit/test_refs_domains.py` pins the exact tuple and that the parent domain and
  look-alike hosts are refused.
