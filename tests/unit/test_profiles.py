import pytest

from rmf_tool.profiles import PHASES, ProfileError, closed_phases, resolve, rule_active


def close(root, *phases):
    (root / ".phases").mkdir(exist_ok=True)
    for p in phases:
        (root / ".phases" / f"{p}.closed").write_text(f"closed {p}\n")


def test_phase_marker_files_read(tmp_path):
    assert closed_phases(tmp_path) == frozenset()
    close(tmp_path, "p1", "p2")
    (tmp_path / ".phases" / ".gitkeep").write_text("")

    assert closed_phases(tmp_path) == {"p1", "p2"}


def test_unknown_marker_rejected(tmp_path):
    close(tmp_path, "p9")
    with pytest.raises(ProfileError, match="p9"):
        closed_phases(tmp_path)


def test_profile_is_closed_phases_plus_target(tmp_path):
    close(tmp_path, "p1", "p2")

    assert resolve(tmp_path, "p3a").phases == {"p1", "p2", "p3a"}
    assert resolve(tmp_path, "p1").phases == {"p1", "p2"}
    assert resolve(tmp_path, None).phases == {"p1", "p2"}


def test_rule_phase_gating(tmp_path):
    profile = resolve(tmp_path, "p3a")

    assert rule_active("p3a", profile)
    assert not rule_active("p5", profile)
    with pytest.raises(ProfileError):
        rule_active("p99", profile)


def test_release_profile_includes_all(tmp_path):
    profile = resolve(tmp_path, "release")

    assert profile.phases == set(PHASES)
    assert profile.examples and profile.agent_severity == "E"
    assert resolve(tmp_path, "p35").agent_severity == "W"


def test_fork_profile_skips_examples_and_agent(tmp_path):
    profile = resolve(tmp_path, "fork")

    assert profile.phases == set(PHASES)
    assert not profile.examples
    assert profile.agent_severity is None


def test_unknown_profile_rejected(tmp_path):
    with pytest.raises(ProfileError, match="unknown profile"):
        resolve(tmp_path, "p8")


def test_p3b_requires_p2x_closed(tmp_path):
    with pytest.raises(ProfileError, match="p2x"):
        resolve(tmp_path, "p3b")
    close(tmp_path, "p2x")
    assert "p3b" in resolve(tmp_path, "p3b").phases
