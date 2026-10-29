"""rmf_tool: deterministic CLI for the DoD RMF manual and agent simulation template."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("rmf-tool")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+unknown"
