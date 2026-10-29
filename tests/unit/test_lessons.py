from conftest import REPO_ROOT, doc, entry

from rmf_tool.lessons import LESSONS_PATH, check, check_format, parse


def errors(findings, rule=None):
    return [f for f in findings if f.severity == "E" and (rule is None or f.rule == rule)]


def test_entry_format_valid():
    text = doc(entry(1), entry(2, promotion="AGENTS.md INV-7 | check: test_x"),
               entry(3, promotion="LR-01"), entry(4, promotion="none — outside the repo"))
    entries, findings = parse(text)

    assert [e.id for e in entries] == ["L-0001", "L-0002", "L-0003", "L-0004"]
    assert entries[0].fields["Root cause"] == "cause 1."
    assert check_format(text) == []


def test_real_lessons_file_valid():
    text = (REPO_ROOT / LESSONS_PATH).read_text(encoding="utf-8")
    entries, _ = parse(text)

    assert check_format(text) == []
    assert [e.id for e in entries[:7]] == [f"L-{n:04d}" for n in range(1, 8)]


def test_ids_monotonic():
    gap = check_format(doc(entry(1), entry(3)))
    assert [f.message for f in errors(gap, "LES-002")] == ["L-0003: expected L-0002"]
    assert errors(check_format(doc(entry(2))), "LES-002")


def test_dates_non_decreasing():
    findings = check_format(doc(entry(1, "2026-10-30"), entry(2, "2026-10-29")))
    assert [f.message for f in errors(findings)] == ["L-0002: date precedes L-0001"]


def test_invalid_date_rejected():
    assert errors(check_format(doc(entry(1, "2026-13-01"))), "LES-002")


def test_pending_promotion_fails():
    findings = check_format(doc(entry(1, promotion="pending")))
    assert [f.rule for f in errors(findings)] == ["LES-003"]
    # A check name that merely contains the word is fine.
    assert check_format(doc(entry(1, promotion="check: test_pending_promotion_fails"))) == []


def test_invalid_promotion_rejected():
    for bad in ("maybe later", "none - ascii hyphen", "AGENTS.md section 3"):
        assert errors(check_format(doc(entry(1, promotion=bad))), "LES-002"), bad


def test_malformed_header_and_fields():
    bad_header = "## L-0001 - 2026-10-29 - run: x - tags: a\n- Symptom: s\n"
    assert errors(check_format(doc(bad_header)), "LES-002")

    swapped = entry(1).replace(
        "- Fix: fix 1.\n- Rule: rule 1.\n", "- Rule: rule 1.\n- Fix: fix 1.\n"
    )
    assert errors(check_format(doc(swapped)), "LES-002")

    extra = entry(1) + "- Notes: something\n"
    assert errors(check_format(doc(extra)), "LES-002")

    stray = entry(1) + "free text\n"
    assert errors(check_format(doc(stray)), "LES-002")

    duplicate = entry(1) + "- Fix: again\n"
    assert errors(check_format(doc(duplicate)), "LES-002")

    assert errors(check_format("# Lessons\n"), "LES-002")


def test_continuation_lines_and_fenced_preamble():
    fenced = "# Lessons\n\n```\n## L-0099 · not an entry\n```\n\n"
    wrapped = entry(1).replace("- Fix: fix 1.\n", "- Fix: fix 1,\n  continued.\n")
    entries, findings = parse(fenced + wrapped)

    assert findings == []
    assert entries[0].fields["Fix"] == "fix 1, continued."


def test_no_history_skips_append_check_with_warning(git_repo):
    git_repo.write(LESSONS_PATH, doc(entry(1)))

    findings = check(git_repo.root)

    assert errors(findings) == []
    assert [(f.rule, f.severity) for f in findings] == [("LES-002", "W")]


def test_append_only_vs_merge_base(git_repo):
    git_repo.write(LESSONS_PATH, doc(entry(1)))
    base = git_repo.commit("base")
    git_repo.git("update-ref", "refs/remotes/origin/main", base)
    git_repo.write(LESSONS_PATH, doc(entry(1), entry(2)))
    git_repo.commit("append")

    assert check(git_repo.root) == []

    git_repo.write(LESSONS_PATH, doc(entry(1).replace("cause 1.", "cause rewritten."), entry(2)))
    assert [f.message for f in errors(check(git_repo.root))] == [
        "L-0001 was modified (append-only)"
    ]

    git_repo.write(LESSONS_PATH, doc(entry(2).replace("L-0002", "L-0001")))
    assert [f.message for f in errors(check(git_repo.root))] == [
        "L-0001 was modified (append-only)"
    ]


def test_missing_ref_falls_back_to_head_parent(git_repo):
    git_repo.write(LESSONS_PATH, doc(entry(1), entry(2)))
    git_repo.commit("one")
    git_repo.write(LESSONS_PATH, doc(entry(1)))  # L-0002 deleted
    git_repo.commit("two")

    messages = [f.message for f in errors(check(git_repo.root))]

    assert messages == ["L-0002 was removed (append-only)"]


def test_missing_file_is_error(git_repo):
    assert [f.message for f in check(git_repo.root)] == ["file not found"]
