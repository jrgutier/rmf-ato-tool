"""The reference library: ``references/index.yaml`` and the files it pins (plan §6.1).

``index.yaml`` is hand-curated (ids, titles, URLs) and machine-updated (sha256, size,
dates, status, text block) by ``rmf refs fetch|import|extract``. It is loaded and saved
round-trip, so comments and key order survive updates.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import jsonschema
from ruamel.yaml import YAML

INDEX_PATH = "references/index.yaml"
SCHEMA_PATH = "references/schema/index.schema.json"
PDF_DIR = "references/pdf"
TEXT_DIR = "references/text"
INBOX_DIR = "references/_inbox"
FETCH_LOG = "references/fetch-log.jsonl"

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"


class IndexFileError(ValueError):
    """index.yaml is missing, unparsable or violates its schema (exit code 2)."""


def _yaml() -> YAML:
    yaml = YAML()
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.representer.add_representer(
        type(None), lambda r, _: r.represent_scalar("tag:yaml.org,2002:null", "null")
    )
    return yaml


def load_index(root: Path) -> Any:
    """The parsed index (a round-trip mapping), validated against its JSON schema."""
    path = root / INDEX_PATH
    try:
        data = _yaml().load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise IndexFileError(f"{INDEX_PATH}: {exc.strerror or exc}") from exc
    except Exception as exc:  # ruamel raises several unrelated parser error types
        raise IndexFileError(f"{INDEX_PATH}: not valid YAML: {exc}") from exc
    errors = schema_errors(root, data)
    if errors:
        raise IndexFileError(f"{INDEX_PATH}: schema violation: " + "; ".join(errors[:5]))
    return data


def schema_errors(root: Path, data: Any) -> list[str]:
    schema = json.loads((root / SCHEMA_PATH).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path]):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{where}: {err.message}")
    return errors


def dump_index(data: Any) -> str:
    buf = io.StringIO()
    _yaml().dump(data, buf)
    return buf.getvalue()


def save_index(root: Path, data: Any) -> bool:
    """Write the index if its serialization changed. Returns True when it wrote."""
    path = root / INDEX_PATH
    text = dump_index(data)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def entries(data: Any) -> list[Any]:
    return list(data["references"])


def find(data: Any, ref_id: str) -> Any | None:
    return next((e for e in data["references"] if e["id"] == ref_id), None)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lfs_pointer_oid(path: Path) -> str | None:
    """The sha256 oid when ``path`` is an un-smudged Git LFS pointer file, else None."""
    with path.open("rb") as fh:
        head = fh.read(200)
    if not head.startswith(LFS_POINTER_PREFIX):
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("oid sha256:"):
            return line.split(":", 1)[1].strip()
    return None
