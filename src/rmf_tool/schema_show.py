"""`rmf schema show` and `rmf schema template`: a run-data schema as an outline or a YAML
skeleton, so an agent learns the fields a record needs without reading the schema source or
the rule code (dry-run findings F-01-13, F-03-10, F-08-5).

Both are deterministic reads of ``framework/schema/<name>.schema.json``. The skeleton holds the
required fields only, each string a ``<<FILL: title>>`` token, each enum its first value with
the others in a comment; optional fields are listed by ``show``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

SCHEMA_DIR = "framework/schema"
MAX_DEPTH = 8


class SchemaError(ValueError):
    pass


def names(root: Path) -> list[str]:
    return sorted(p.name.removesuffix(".schema.json")
                  for p in (root / SCHEMA_DIR).glob("*.schema.json"))


def load(root: Path, name: str) -> dict[str, Any]:
    name = name.removesuffix(".yaml").removesuffix(".schema.json").rsplit("/", 1)[-1]
    path = root / SCHEMA_DIR / f"{name}.schema.json"
    if not path.is_file():
        raise SchemaError(f"no schema {name!r}; known: {', '.join(names(root))}")
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(node: Mapping[str, Any], schema: Mapping[str, Any]) -> Mapping[str, Any]:
    seen = 0
    while "$ref" in node and seen < MAX_DEPTH:
        ref = str(node["$ref"])
        if not ref.startswith("#/"):
            return node
        target: Any = schema
        for part in ref[2:].split("/"):
            target = target[part]
        merged = {k: v for k, v in node.items() if k != "$ref"}
        node = {**target, **merged}
        seen += 1
    return node


def _kind(node: Mapping[str, Any]) -> str:
    if "enum" in node:
        return "one of " + ", ".join(str(v) for v in node["enum"])
    if "const" in node:
        return f"= {node['const']}"
    kind = node.get("type")
    if isinstance(kind, list):
        kind = "|".join(str(k) for k in kind)
    extra = []
    if node.get("pattern"):
        extra.append(f"pattern {node['pattern']}")
    if node.get("format"):
        extra.append(str(node["format"]))
    if node.get("minItems"):
        extra.append(f"at least {node['minItems']}")
    return " ".join([str(kind or "any"), *(f"({e})" for e in extra)])


def outline(schema: Mapping[str, Any]) -> list[str]:
    """One line per field: indented path, `*` when required, kind, and title."""
    lines: list[str] = []
    title = schema.get("title")
    if title:
        lines.append(str(title))
    if schema.get("description"):
        lines.append(str(schema["description"]))

    def walk(node: Mapping[str, Any], depth: int) -> None:
        node = _resolve(node, schema)
        if depth > MAX_DEPTH:
            return
        if node.get("type") == "array" and isinstance(node.get("items"), Mapping):
            walk(node["items"], depth)
            return
        required = set(node.get("required") or ())
        for key, child in (node.get("properties") or {}).items():
            child = _resolve(child, schema)
            mark = "*" if key in required else " "
            label = child.get("title") or child.get("description") or ""
            many = "[]" if child.get("type") == "array" else ""
            item = _resolve(child.get("items") or {}, schema) if many else child
            lines.append(f"{'  ' * depth}{mark} {key}{many}: {_kind(item)}"
                         + (f"  # {label}" if label else ""))
            walk(child, depth + 1)

    walk(schema, 0)
    lines.append("(* required)")
    return lines


def _sample(pattern: str) -> str | None:
    """A shortest string matching `pattern`, from its parse tree; None when unsure."""
    try:
        from re import _parser as parser  # type: ignore[attr-defined]
    except ImportError:  # pragma: no cover - Python < 3.11
        import sre_parse as parser  # type: ignore[no-redef]
    category = {"CATEGORY_DIGIT": "0", "CATEGORY_WORD": "a", "CATEGORY_SPACE": " ",
                "CATEGORY_NOT_SPACE": "a", "CATEGORY_NOT_DIGIT": "a"}

    def gen(items: Any) -> str:
        out = []
        for op, arg in items:
            name = str(op)
            if name == "LITERAL":
                out.append(chr(arg))
            elif name == "ANY":
                out.append("a")
            elif name == "IN":
                first = arg[0]
                kind = str(first[0])
                if kind == "NEGATE":
                    out.append("a")
                elif kind == "RANGE":
                    out.append(chr(first[1][0]))
                elif kind == "LITERAL":
                    out.append(chr(first[1]))
                elif kind == "CATEGORY":
                    out.append(category.get(str(first[1]), "a"))
                else:
                    raise ValueError(kind)
            elif name in ("MAX_REPEAT", "MIN_REPEAT", "POSSESSIVE_REPEAT"):
                low, _, sub = arg
                out.append(gen(sub) * max(low, 0))
            elif name == "SUBPATTERN":
                out.append(gen(arg[-1]))
            elif name == "BRANCH":
                out.append(gen(arg[1][0]))
            elif name == "AT":
                continue
            elif name == "CATEGORY":
                out.append(category.get(str(arg), "a"))
            else:
                raise ValueError(name)
        return "".join(out)

    try:
        value = gen(parser.parse(pattern))
    except (ValueError, TypeError, IndexError, re.error):
        return None
    return value if value and re.search(pattern, value) else None


def _fill(node: Mapping[str, Any], key: str) -> str:
    label = str(node.get("title") or key)
    if node.get("pattern"):
        label += f", matching {node['pattern']}"
    return "'<<FILL: " + label.replace("'", "’") + ">>'"


def skeleton(schema: Mapping[str, Any]) -> str:
    """A YAML skeleton with every required field, in schema order."""
    out: list[str] = [f"# {schema.get('title', 'record')}: generated by `rmf schema template`;",
                      "# replace every <<FILL>>; `rmf schema show` lists the optional fields."]

    def scalar(node: Mapping[str, Any], key: str) -> tuple[str, str]:
        if "enum" in node:
            rest = [str(v) for v in node["enum"][1:]]
            return str(node["enum"][0]), (f"  # or: {', '.join(rest)}" if rest else "")
        if "const" in node:
            return str(node["const"]), ""
        kind = node.get("type")
        if kind == "boolean":
            return "false", ""
        if isinstance(kind, list):
            kind = next((k for k in kind if k != "null"), None)
        if kind in ("integer", "number"):
            return str(node.get("minimum", 0)), ""
        if node.get("format") == "date":
            return "2026-01-01", f"  # <<FILL: {node.get('title') or key}>>"
        if node.get("pattern"):
            sample = _sample(str(node["pattern"]))
            if sample is not None:
                label = str(node.get("title") or key)
                return json.dumps(sample), f"  # <<FILL: {label}>>"
        return _fill(node, key), ""

    def emit(node: Mapping[str, Any], indent: str, depth: int, first: str = "") -> None:
        node = _resolve(node, schema)
        required = list(node.get("required") or ())
        # an if/else whose `if` needs a field the skeleton leaves out takes the else branch
        for cond in [node, *(node.get("allOf") or [])]:
            if "if" in cond and set(cond["if"].get("required") or ()) - set(required):
                required += [r for r in (cond.get("else") or {}).get("required") or ()
                             if r not in required]
        props = node.get("properties") or {}
        if first and not any(k in props for k in required):
            out.append(f"{first}{{}}")
        for i, key in enumerate(k for k in props if k in required):
            child = _resolve(props[key], schema)
            lead = first if i == 0 and first else indent
            kind = child.get("type")
            if kind == "object" or (kind is None and "properties" in child):
                out.append(f"{lead}{key}:")
                if depth < MAX_DEPTH:
                    emit(child, indent + "  ", depth + 1)
            elif kind == "array":
                item = _resolve(child.get("items") or {}, schema)
                if item.get("type") == "object" or "properties" in item:
                    out.append(f"{lead}{key}:")
                    if depth < MAX_DEPTH:
                        emit(item, indent + "    ", depth + 1, first=indent + "  - ")
                else:
                    value, note = scalar({**item, "title": item.get("title")
                                          or child.get("title")}, key)
                    out.append(f"{lead}{key}:{note}")
                    out.append(f"{indent}  - {value}")
            else:
                value, note = scalar(child, key)
                out.append(f"{lead}{key}: {value}{note}")

    emit(schema, "", 0)
    return "\n".join(out) + "\n"
