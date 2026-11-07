"""YAML parsing memoized on the text, so a file read again unchanged is not parsed again.

ruamel parses in pure Python, and a check reads the same run, framework and table files
many times (one negative fixture parsed 3,300 documents, 80% of its time). The key is the
text itself, never a path or mtime, so a file rewritten between reads (``rmf build``) is
always parsed afresh. Each caller gets its own copy and may mutate it. Parse errors are
not cached, so they surface on every read.
"""

from __future__ import annotations

import copy
import functools
import pickle
from typing import Any

from ruamel.yaml import YAML

_CACHE_SIZE = 1024


@functools.lru_cache(maxsize=_CACHE_SIZE)
def _safe(text: str) -> bytes:
    # Safe-loaded data is plain Python (dict, list, str, numbers, dates): a pickle of it
    # restores in a fraction of a deep copy's time.
    return pickle.dumps(YAML(typ="safe").load(text), protocol=pickle.HIGHEST_PROTOCOL)


@functools.lru_cache(maxsize=_CACHE_SIZE)
def _rt(text: str) -> Any:
    return YAML(typ="rt").load(text)


def safe_load(text: str) -> Any:
    """``YAML(typ="safe").load(text)``, memoized."""
    return pickle.loads(_safe(text))


def rt_load(text: str) -> Any:
    """``YAML(typ="rt").load(text)``, memoized; the copy keeps line and comment data."""
    return copy.deepcopy(_rt(text))
