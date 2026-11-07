"""The memoized YAML loader: a cached parse is never shared or served for changed text."""

import pytest

from rmf_tool.run.model import YamlError, read_yaml
from rmf_tool.yamlload import rt_load, safe_load


def test_each_read_gets_its_own_copy():
    first = safe_load("a: [1, 2]\n")
    first["a"].append(3)
    assert safe_load("a: [1, 2]\n") == {"a": [1, 2]}


def test_a_rewritten_file_is_parsed_again(tmp_path):
    path = tmp_path / "f.yaml"
    path.write_text("v: 1\n")
    assert read_yaml(path) == {"v": 1}
    path.write_text("v: 2\n")  # same size, likely within the same clock tick
    assert read_yaml(path) == {"v": 2}


def test_a_parse_error_is_raised_on_every_read(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("a: [\n")
    for _ in range(2):
        with pytest.raises(YamlError):
            read_yaml(path)


def test_round_trip_copies_keep_line_numbers():
    text = "a: 1\nb:\n  c: 2\n"
    first = rt_load(text)
    first["b"]["c"] = 9
    second = rt_load(text)
    assert second["b"]["c"] == 2 and second.lc.key("b") == (1, 0)
