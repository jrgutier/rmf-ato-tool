"""Apply a negative-fixture mutation spec (plan §4.1) to a copy of a base run."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


def _yaml() -> YAML:
    yaml = YAML()
    yaml.width = 4096
    yaml.preserve_quotes = True
    return yaml


def _walk(node: Any, path: str) -> tuple[Any, Any]:
    """(parent, last key) for a dotted path; integer parts index lists."""
    parts = [int(p) if p.isdigit() else p for p in str(path).split(".")]
    for part in parts[:-1]:
        node = node[part]
    return node, parts[-1]


def _edit_yaml(file: Path, edit: Any) -> None:
    yaml = _yaml()
    data = yaml.load(file.read_text(encoding="utf-8"))
    edit(data)
    buf = io.StringIO()
    yaml.dump(data, buf)
    file.write_text(buf.getvalue(), encoding="utf-8")


def _matches(item: Any, where: dict[str, Any]) -> bool:
    return isinstance(item, dict) and all(item.get(k) == v for k, v in where.items())


def apply(run_dir: Path, mutation: dict[str, Any]) -> None:
    op, file = mutation["op"], run_dir / mutation["file"]
    if op == "delete_file":
        file.unlink()
    elif op == "write_file":
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(mutation["content"], encoding="utf-8")
    elif op == "append_text":
        file.write_text(file.read_text(encoding="utf-8") + mutation["text"], encoding="utf-8")
    elif op == "replace_text":
        text = file.read_text(encoding="utf-8")
        assert mutation["old"] in text, f"{mutation['file']}: {mutation['old']!r} not found"
        file.write_text(text.replace(mutation["old"], mutation["new"], 1), encoding="utf-8")
    elif op == "set_field":
        def set_field(data: Any) -> None:
            parent, key = _walk(data, mutation["path"])
            parent[key] = mutation["value"]
        _edit_yaml(file, set_field)
    elif op == "delete_field":
        def delete_field(data: Any) -> None:
            parent, key = _walk(data, mutation["path"])
            del parent[key]
        _edit_yaml(file, delete_field)
    elif op == "delete_list_item":
        def delete_item(data: Any) -> None:
            parent, key = _walk(data, mutation["path"])
            items = parent[key]
            index = next(i for i, item in enumerate(items) if _matches(item, mutation["where"]))
            del items[index]
        _edit_yaml(file, delete_item)
    elif op == "resolve_baseline":
        # Regenerate baseline.json as `rmf baseline resolve` would, after the mutations before
        # it changed facts.yaml, run.yaml or tailoring.yaml; never hand-written (INV-2).
        from rmf_tool import baseline
        from rmf_tool.run.model import open_run

        repo = Path(__file__).resolve().parents[2]
        file.write_text(baseline.render(baseline.resolve(open_run(run_dir, repo))),
                        encoding="utf-8")
    else:
        raise ValueError(f"unknown mutation op {op!r}")
