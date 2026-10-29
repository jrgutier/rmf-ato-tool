"""REF-006: the allowed download domains (plan §6.1).

Checked on every configured URL and on every redirect hop. Only ``https`` is allowed.
"""

from __future__ import annotations

from urllib.parse import urlsplit

# A host matches when it equals a domain or is a subdomain of it.
ALLOWED_DOMAINS = ("nist.gov", "esd.whs.mil", "cnss.gov", "public.cyber.mil",
                   "dodcio.defense.gov")
# GitHub hosts are allowed only below these path prefixes.
GITHUB_PREFIXES = {"github.com": "/usnistgov/", "raw.githubusercontent.com": "/usnistgov/"}
# GitHub release-asset hosts: only as a redirect target from github.com/usnistgov/*.
RELEASE_ASSET_HOSTS = ("release-assets.githubusercontent.com", "objects.githubusercontent.com")


def _host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().rstrip(".")


def disallowed_reason(url: str, redirected_from: str | None = None) -> str | None:
    """Why ``url`` may not be fetched, or None when it is allowed."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        return f"scheme {parts.scheme or '(none)'!r} is not https"
    host = _host(url)
    if any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS):
        return None
    prefix = GITHUB_PREFIXES.get(host)
    if prefix is not None:
        return None if parts.path.startswith(prefix) else f"{host} path outside {prefix}"
    if host in RELEASE_ASSET_HOSTS:
        if redirected_from is not None and disallowed_reason(redirected_from) is None \
                and _host(redirected_from) == "github.com":
            return None
        return f"{host} is allowed only as a redirect target from github.com/usnistgov"
    return f"host {host or '(none)'!r} is not an allowed domain"


def is_allowed(url: str, redirected_from: str | None = None) -> bool:
    return disallowed_reason(url, redirected_from) is None
