"""`rmf refs fetch`: download ``acquisition: auto`` references (plan PM-2, AC-4).

- An honest User-Agent; TLS verification always on (L-0003).
- Liveness is a ranged GET, never HEAD (L-0001); the full body is a plain GET.
- Redirects are followed by hand so every hop is checked against the allowed
  domains (REF-006).
- PDFs must start with ``%PDF-`` and pass ``qpdf --check``; OSCAL JSON must parse and
  have the model's root key.
- A download whose SHA-256 differs from the pinned one is reported as ``changed`` and
  the pinned file is kept, unless ``--accept-new --note`` is given.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import tempfile
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from rmf_tool import __version__
from rmf_tool.refs import FETCH_LOG, load_index, save_index, sha256_file
from rmf_tool.refs.domains import disallowed_reason

USER_AGENT = f"rmf-tool/{__version__} (reference library fetcher) python-httpx/{httpx.__version__}"
PROBE_RANGE = "bytes=0-1023"
MAX_REDIRECTS = 5
TIMEOUT = httpx.Timeout(120.0, connect=20.0)
PDF_MAGIC = b"%PDF-"
JSON_ROOT_KEYS = {
    "oscal-catalog": "catalog",
    "oscal-resolved-catalog": "catalog",
    "oscal-profile": "profile",
    "oscal-example": "system-security-plan",
}
FAILED = ("changed", "manual-required")


class FetchFailure(Exception):
    """One URL could not be fetched or its content was rejected."""


@dataclass
class Result:
    id: str
    status: str  # downloaded | unchanged | accepted | changed | manual-required | skipped
    message: str = ""
    log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return self.status in FAILED


def make_client() -> httpx.Client:
    # httpx verifies TLS by default; this tool never passes verify=False (L-0003).
    return httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=False,
                        timeout=TIMEOUT)


def _strip_query(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _send(client: httpx.Client, url: str, headers: dict[str, str],
          hops: list[dict[str, Any]]) -> httpx.Response:
    """A streaming GET that follows redirects by hand, checking every hop (REF-006)."""
    reason = disallowed_reason(url)
    if reason:
        raise FetchFailure(f"REF-006: {url}: {reason}")
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        resp = client.send(client.build_request("GET", current, headers=headers), stream=True)
        hops.append({"url": _strip_query(current), "status": resp.status_code})
        if not (resp.is_redirect and "location" in resp.headers):
            return resp
        nxt = urljoin(current, resp.headers["location"])
        resp.close()
        reason = disallowed_reason(nxt, redirected_from=current)
        if reason:
            raise FetchFailure(f"REF-006: redirect to {_strip_query(nxt)}: {reason}")
        current = nxt
    raise FetchFailure(f"more than {MAX_REDIRECTS} redirects")


def _head_bytes(resp: httpx.Response, limit: int = 1024) -> bytes:
    buf = b""
    for chunk in resp.iter_bytes():
        buf += chunk
        if len(buf) >= limit:
            break
    return buf[:limit]


def _looks_right(kind: str, head: bytes) -> str | None:
    if kind == "pdf":
        return None if head.startswith(PDF_MAGIC) else f"not a PDF (starts with {head[:16]!r})"
    return None if head.lstrip().startswith(b"{") else f"not JSON (starts with {head[:16]!r})"


def validate_file(path: Path, kind: str) -> str | None:
    """Why the file at ``path`` is not acceptable content for ``kind``, or None."""
    if kind == "pdf":
        with path.open("rb") as fh:
            head = fh.read(len(PDF_MAGIC))
        if head != PDF_MAGIC:
            return f"not a PDF (starts with {head!r})"
        try:
            proc = subprocess.run(["qpdf", "--check", str(path)], capture_output=True,
                                  text=True, check=False)
        except FileNotFoundError:
            return "qpdf not found on PATH (make bootstrap)"
        # qpdf exits 0 when clean, 3 when it only printed warnings, 2 on errors.
        if proc.returncode not in (0, 3):
            detail = (proc.stdout + proc.stderr).strip().splitlines()
            return "qpdf --check failed: " + (detail[-1] if detail else f"exit {proc.returncode}")
        return None
    try:
        doc = json.loads(path.read_bytes())
    except (ValueError, UnicodeDecodeError) as exc:
        return f"not valid JSON: {exc}"
    if not isinstance(doc, dict):
        return "JSON root is not an object"
    if kind == "oscal-schema":
        return None if "$schema" in doc else "JSON schema without a $schema key"
    root_key = JSON_ROOT_KEYS.get(kind)
    if root_key and root_key not in doc:
        return f"OSCAL document without a {root_key!r} root"
    return None


def _download(client: httpx.Client, url: str, kind: str, dest_dir: Path,
              hops: list[dict[str, Any]]) -> tuple[str, Path]:
    """Probe with a ranged GET, then download to a temp file next to the destination."""
    with closing(_send(client, url, {"Range": PROBE_RANGE}, hops)) as resp:
        if resp.status_code not in (200, 206):
            raise FetchFailure(f"HTTP {resp.status_code}")
        reason = _looks_right(kind, _head_bytes(resp))
        if reason:
            raise FetchFailure(reason)
    with closing(_send(client, url, {}, hops)) as resp:
        if resp.status_code != 200:
            raise FetchFailure(f"HTTP {resp.status_code}")
        final = str(resp.url)
        fd, tmp_name = tempfile.mkstemp(dir=dest_dir, prefix=".fetch-", suffix=".part")
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "wb") as fh:
                for chunk in resp.iter_bytes():
                    fh.write(chunk)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    reason = validate_file(tmp, kind)
    if reason:
        tmp.unlink(missing_ok=True)
        raise FetchFailure(reason)
    return final, tmp


def _record(entry: Any, dest: Path, final_url: str | None, sha: str, today: str,
            note: str | None) -> None:
    entry["resolved_url"] = _strip_query(final_url) if final_url else None
    entry["sha256"] = sha
    entry["size_bytes"] = dest.stat().st_size
    entry["downloaded"] = today
    if note:
        entry["revision_note"] = note
    entry["status"] = "ok"


def _settle(entry: Any, dest: Path, tmp: Path, final_url: str, *, accept_new: bool,
            note: str | None, today: str) -> Result:
    ref_id, pinned = entry["id"], entry["sha256"]
    new_sha = sha256_file(tmp)
    if pinned is not None and new_sha != pinned:
        if not accept_new:
            entry["status"] = "changed"
            return Result(ref_id, "changed",
                          f"upstream sha256 {new_sha} differs from pinned {pinned}; kept "
                          f"{entry['local_path']} (review, then --accept-new --note)")
        os.replace(tmp, dest)
        _record(entry, dest, final_url, new_sha, today, note)
        return Result(ref_id, "accepted", f"new sha256 {new_sha} accepted")
    if pinned == new_sha and dest.is_file() and sha256_file(dest) == new_sha:
        entry["status"] = "ok"
        return Result(ref_id, "unchanged")
    os.replace(tmp, dest)
    _record(entry, dest, final_url, new_sha, today, note)
    return Result(ref_id, "downloaded", f"{entry['size_bytes']} bytes, sha256 {new_sha}")


def fetch_entry(client: httpx.Client, root: Path, entry: Any, *, accept_new: bool = False,
                note: str | None = None, today: str | None = None) -> Result:
    """Fetch one index entry in place (mutates ``entry``)."""
    if entry["acquisition"] != "auto":
        return Result(entry["id"], "skipped",
                      f"acquisition: {entry['acquisition']} (use rmf refs import)")
    today = today or dt.datetime.now(dt.UTC).date().isoformat()
    dest = root / entry["local_path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    log: list[dict[str, Any]] = []
    for url in entry["urls"]:
        hops: list[dict[str, Any]] = []
        try:
            final, tmp = _download(client, url, entry["kind"], dest.parent, hops)
        except (FetchFailure, httpx.HTTPError) as exc:
            errors.append(f"{url}: {exc}")
            log.append({"url": url, "hops": hops, "error": str(exc)})
            continue
        log.append({"url": url, "hops": hops})
        try:
            result = _settle(entry, dest, tmp, final, accept_new=accept_new, note=note,
                             today=today)
        finally:
            tmp.unlink(missing_ok=True)
        result.log = log
        return result
    entry["status"] = "manual-required"
    return Result(entry["id"], "manual-required", "; ".join(errors) or "no URLs", log)


def _append_log(root: Path, results: list[Result]) -> None:
    path = root / FETCH_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as fh:
        for r in results:
            if r.status == "skipped":
                continue
            fh.write(json.dumps({"ts": ts, "id": r.id, "result": r.status,
                                 "message": r.message, "attempts": r.log}) + "\n")


def is_present(root: Path, entry: Any) -> bool:
    """The pinned file is on disk with the pinned SHA-256 (not an LFS pointer)."""
    path = root / entry["local_path"] if entry["local_path"] else None
    return bool(path and entry["sha256"] and path.is_file()
                and sha256_file(path) == entry["sha256"])


def fetch(root: Path, ids: list[str] | None = None, *, accept_new: bool = False,
          note: str | None = None, missing_only: bool = False,
          client_factory: Callable[[], httpx.Client] = make_client,
          today: str | None = None) -> list[Result]:
    """Fetch the selected auto entries, update index.yaml, append to fetch-log.jsonl."""
    data = load_index(root)
    selected = [e for e in data["references"] if not ids or e["id"] in ids]
    unknown = sorted(set(ids or ()) - {e["id"] for e in selected})
    if unknown:
        raise KeyError(f"unknown reference id(s): {', '.join(unknown)}")
    results: list[Result] = []
    with client_factory() as client:
        for entry in selected:
            if missing_only and entry["acquisition"] == "auto" and is_present(root, entry):
                if entry["status"] != "ok":
                    entry["status"] = "ok"
                results.append(Result(entry["id"], "unchanged", "present (not re-downloaded)"))
                continue
            results.append(fetch_entry(client, root, entry, accept_new=accept_new, note=note,
                                       today=today))
    save_index(root, data)
    _append_log(root, results)
    return results
