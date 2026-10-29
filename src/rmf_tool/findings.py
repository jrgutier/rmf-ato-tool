"""Rule findings and the shared ``{summary, findings}`` report shape (plan §4.5)."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # "E" | "W"
    message: str
    path: str | None = None
    line: int | None = None

    def render(self) -> str:
        prefix = "error" if self.severity == "E" else "warning"
        where = ""
        if self.path:
            where = f" {self.path}" + (f":{self.line}" if self.line is not None else "")
        return f"{prefix} {self.rule}{where}: {self.message}"


def report(findings: list[Finding], rules_run: list[str]) -> dict:
    return {
        "summary": {
            "errors": sum(f.severity == "E" for f in findings),
            "warnings": sum(f.severity == "W" for f in findings),
            "rules_run": rules_run,
        },
        "findings": [asdict(f) for f in findings],
    }
