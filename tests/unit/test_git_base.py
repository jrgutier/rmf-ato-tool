from rmf_tool.gitutil import repo_root, resolve_base, show_file


def test_resolve_base_merge_base(git_repo):
    first = git_repo.commit("one")
    git_repo.git("update-ref", "refs/remotes/origin/main", first)
    git_repo.commit("two")
    git_repo.commit("three")

    base = resolve_base(git_repo.root)

    assert (base.ref, base.how, base.warning) == (first, "merge-base", None)


def test_resolve_base_fallback_head_parent(git_repo):
    first = git_repo.commit("one")
    git_repo.commit("two")

    base = resolve_base(git_repo.root)

    assert (base.ref, base.how) == (first, "HEAD~1")


def test_resolve_base_none_returns_skip(git_repo):
    assert resolve_base(git_repo.root).how == "skip"  # no commits at all
    git_repo.commit("only")

    base = resolve_base(git_repo.root)

    assert base.ref is None
    assert base.how == "skip"
    assert "origin/main" in base.warning


def test_show_file_at_ref(git_repo):
    git_repo.write("docs/a.md", "v1\n")
    ref = git_repo.commit("one")
    git_repo.write("docs/a.md", "v2\n")

    assert show_file(git_repo.root, ref, "docs/a.md") == "v1\n"
    assert show_file(git_repo.root, ref, "docs/missing.md") is None


def test_repo_root_finds_toplevel(git_repo, tmp_path):
    sub = git_repo.root / "a" / "b"
    sub.mkdir(parents=True)

    assert repo_root(sub) == git_repo.root.resolve()
    outside = tmp_path / "plain"
    outside.mkdir()
    assert repo_root(outside) == outside.resolve()
