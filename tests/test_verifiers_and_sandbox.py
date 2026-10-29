from __future__ import annotations

import unicodedata

import pytest
from pydantic import ValidationError

from vi_en_eval.verifiers import (
    ASTAnalysisPolicy,
    IFEvalConstraintSpec,
    analyze_python_ast,
    compare_code_candidates_ab,
    run_in_python_sandbox,
    verify_instruction_following,
)


def test_vietnamese_normalization_preserves_lexical_evidence():
    text = unicodedata.normalize("NFD", "- Đà Nẵng là thành phố.\n- chứa từ cấm.")
    result = verify_instruction_following(
        text,
        IFEvalConstraintSpec(
            exact_bullet_count=2,
            forbidden_phrases=("TỪ CẤM",),
            required_keywords=("ĐÀ NẴNG",),
        ),
    )
    assert {v.constraint_name for v in result.violations} == {
        "unicode_nfc_normalization",
        "forbidden_phrases",
    }
    assert result.total_checks == 4 and result.passed_checks == 2
    assert result.score_ratio == 0.5 and result.word_count == 8
    assert "NFD" in result.synthesized_english_rationale


def test_ifeval_table_json_and_bullets():
    text = '- Một\n2. Hai\n| A | B |\n| :--- | ---: |\n| 1 | 2 |\n```json\n{"verdict":"pass","score":5}\n```'
    report = verify_instruction_following(
        text,
        IFEvalConstraintSpec(
            exact_bullet_count=2,
            require_markdown_table=True,
            required_json_keys=("verdict", "score"),
        ),
    )
    assert report.passed and report.score_ratio == 1


@pytest.mark.parametrize(
    "options",
    [
        {"min_words": 3, "max_words": 2},
        {"min_words": 0},
        {"exact_bullet_count": -1},
        {"required_keywords": ("",)},
        {"forbidden_phrases": (" ",)},
        {"required_json_keys": ("",)},
        {"unknown": True},
    ],
)
def test_invalid_constraint_spec(options):
    with pytest.raises(ValidationError):
        IFEvalConstraintSpec(**options)


@pytest.mark.parametrize(
    ("text", "options", "name"),
    [
        ("a", {"min_words": 2}, "min_words"),
        ("a b", {"max_words": 1}, "max_words"),
        ("- a", {"exact_bullet_count": 2}, "exact_bullet_count"),
        ("a", {"required_keywords": ("b",)}, "required_keywords"),
        ("| --- | --- |", {"require_markdown_table": True}, "require_markdown_table"),
        ("A | B | C\n--- | ---", {"require_markdown_table": True}, "require_markdown_table"),
        ('{"a":1}', {"required_json_keys": ("b",)}, "required_json_keys"),
        ("[]", {"required_json_keys": ("b",)}, "required_json_keys"),
        ('{"a":1,"a":2}', {"require_valid_json_block": True}, "require_valid_json_block"),
        ('{"a":NaN}', {"require_valid_json_block": True}, "require_valid_json_block"),
        ("{", {"require_valid_json_block": True}, "require_valid_json_block"),
        (
            "```json\n{}\n```\n```json\n{}\n```",
            {"require_valid_json_block": True},
            "require_valid_json_block",
        ),
        ("```python\n{}\n```", {"require_valid_json_block": True}, "require_valid_json_block"),
    ],
)
def test_ifeval_failures_have_one_evidence_record(text, options, name):
    report = verify_instruction_following(
        text, IFEvalConstraintSpec(require_unicode_nfc=False, **options)
    )
    assert not report.passed and report.score_ratio == 0
    assert report.total_checks == 1 and report.passed_checks == 0
    assert len(report.violations) == 1 and report.violations[0].constraint_name == name
    assert report.violations[0].evidence_rationale in report.synthesized_english_rationale


def test_ifeval_no_checks_and_boundary_lengths():
    assert (
        verify_instruction_following(
            "", IFEvalConstraintSpec(require_unicode_nfc=False)
        ).score_ratio
        == 1
    )
    assert verify_instruction_following(
        "Đà Nẵng", IFEvalConstraintSpec(min_words=2, max_words=2)
    ).passed
    assert verify_instruction_following(
        "```\n- fake bullet\n```\n+ actual", IFEvalConstraintSpec(exact_bullet_count=1)
    ).passed
    assert not verify_instruction_following(
        "```\nA | B\n--- | ---\n```", IFEvalConstraintSpec(require_markdown_table=True)
    ).passed
    assert verify_instruction_following(
        '```json\r\n{"a": [1, {"b": "}"}]}\r\n```', IFEvalConstraintSpec(required_json_keys=("a",))
    ).passed
    key = unicodedata.normalize("NFD", "Đà")
    assert verify_instruction_following(
        '{"' + key + '": 1}',
        IFEvalConstraintSpec(require_unicode_nfc=False, required_json_keys=(key,)),
    ).passed


@pytest.mark.parametrize(
    "source",
    [
        "import os as harmless",
        "from subprocess import run as launch",
        "from . import local",
        "from math import *",
        "import pathlib",
        "danger = open",
        "fn = eval; fn('1')",
        "x = ().__class__",
        "x = __builtins__",
        "import math; math.__dict__",
        "from math import __dict__",
        "getattr(1, 'real')",
        "import math; math.open('x')",
    ],
)
def test_ast_gate_rejects_restricted_references(source):
    report = analyze_python_ast(source)
    assert not report.is_safe_to_execute
    assert any(i.category == "security_violation" for i in report.issues)


@pytest.mark.parametrize("source", ["def broken(:", "return 1", "break", "\0"])
def test_ast_invalid_syntax(source):
    report = analyze_python_ast(source)
    assert not report.is_safe_to_execute and report.branch_complexity_score == 0
    assert report.issues[0].category == "syntax_error"


def test_ast_all_argument_kinds_defaults_and_quality_toggles():
    source = "async def f(a, /, b, *args, key=[], **kwargs):\n    try:\n        return b\n    except:\n        return None\n"
    report = analyze_python_ast(source)
    assert report.is_safe_to_execute and not report.passed_all_checks
    assert len(report.issues) == 3
    assert all(name in report.issues[0].message for name in ("a", "b", "args", "key", "kwargs"))
    assert analyze_python_ast(
        source,
        ASTAnalysisPolicy(
            require_type_annotations=False,
            forbid_mutable_default_args=False,
            forbid_bare_except=False,
        ),
    ).passed_all_checks


@pytest.mark.parametrize(
    "default",
    [
        "[]",
        "{}",
        "set()",
        "list()",
        "dict()",
        "bytearray()",
        "([],)",
        "[x for x in ()]",
        "{x for x in ()}",
        "{x: x for x in ()}",
    ],
)
def test_mutable_default_forms(default):
    report = analyze_python_ast(f"def f(x: object = {default}) -> object:\n    return x")
    assert len(report.issues) == 1 and "mutable" in report.issues[0].message


def test_ast_entrypoint_requires_top_level_definition():
    report = analyze_python_ast(
        "def outer() -> None:\n    def inner() -> None: pass",
        ASTAnalysisPolicy(require_function_name="inner"),
    )
    assert not report.is_safe_to_execute and report.issues[-1].category == "missing_symbol"
    assert analyze_python_ast(
        "def f() -> int: return 1", ASTAnalysisPolicy(require_function_name="f")
    ).passed_all_checks


def test_complexity_counts_decisions_not_with_or_assert():
    source = """def f(a: int, b: int) -> list[int]:
    if a and b or a:
        return [x for x in range(a) if x > 1]
    return [a if b else 0]
"""
    assert analyze_python_ast(source).branch_complexity_score == 7
    assert analyze_python_ast("assert True").branch_complexity_score == 1
    assert (
        analyze_python_ast("match 1:\n case 1 if True: pass\n case _: pass").branch_complexity_score
        == 3
    )


GOOD = """def append_tag(tag: str, history: list[str] | None = None) -> list[str]:
    result = list(history) if history is not None else []
    result.append(tag)
    return result
"""
BAD = """def append_tag(tag: str, history: list[str] = []) -> list[str]:
    history.append(tag)
    return history
"""
FIXTURE = "append_tag('v1')\nassert append_tag('v2') == ['v2'], 'State leaked across calls'"


def test_pairwise_state_leak_counterexample_and_reverse():
    policy = ASTAnalysisPolicy(require_function_name="append_tag")
    report = compare_code_candidates_ab(GOOD, BAD, FIXTURE, policy)
    assert report.winner == "model_a" and report.model_a_result.passed
    assert report.model_b_result.status == "assertion_failed"
    assert "State leaked across calls" in report.synthesized_english_rationale
    assert compare_code_candidates_ab(BAD, GOOD, FIXTURE, policy).winner == "model_b"


@pytest.mark.parametrize(
    ("a", "b", "winner"),
    [
        ("x = 1", "x = 1", "tie_both_pass"),
        ("x = 0", "x = 0", "tie_both_fail"),
        ("x = 1", "x = 1\ndef f(): pass", "model_a"),
        ("x = 1\ndef f(): pass", "x = 1", "model_b"),
        ("x = 1\ndef f(): pass", "x = 1\ndef f(): pass", "tie_both_pass"),
    ],
)
def test_pairwise_ties_and_quality(a, b, winner):
    report = compare_code_candidates_ab(a, b, "assert x == 1")
    assert report.winner == winner
    if winner == "tie_both_pass" and report.model_a_result.ast_report.issues:
        assert "Model A=1, Model B=1" in report.synthesized_english_rationale


@pytest.mark.parametrize(
    ("source", "fixtures", "status"),
    [
        ("import subprocess", "assert True", "blocked_by_ast"),
        ("x = 1", "import os", "blocked_by_ast"),
        ("def broken(:", "assert True", "blocked_by_ast"),
        ("raise ValueError('AssertionError is just text')", "assert True", "runtime_error"),
        ("raise SystemExit(0)", "assert True", "runtime_error"),
        ("assert False", "assert True", "assertion_failed"),
        (
            "from __future__ import annotations\ndef f(x: Missing) -> int: return 1",
            "assert f(0) == 1",
            "passed",
        ),
        ("import math\nx = math.sqrt(4)", "assert x == 2", "passed"),
    ],
)
def test_execution_statuses(source, fixtures, status):
    report = run_in_python_sandbox(source, fixtures)
    assert report.status == status
    assert report.passed == (status == "passed")


def test_timeout_and_bounded_unicode_output():
    timeout = run_in_python_sandbox(
        "print('ready', flush=True)\nwhile True: pass", "assert True", timeout_seconds=0.5
    )
    assert timeout.status == "timeout" and timeout.exit_code is None
    assert "ready" in timeout.stdout
    report = run_in_python_sandbox("print('Đà Nẵng')\nprint('x' * 20000)", "assert True")
    assert report.passed and report.output_truncated
    assert report.stdout.startswith("Đà Nẵng") and len(report.stdout.encode("utf-8")) <= 4000


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_invalid_timeout(timeout):
    with pytest.raises(ValueError, match="finite and positive"):
        run_in_python_sandbox("pass", "assert True", timeout_seconds=timeout)


def test_blank_fixture_and_launch_failure(monkeypatch):
    with pytest.raises(ValueError, match="blank"):
        run_in_python_sandbox("pass", " ")
    from vi_en_eval.verifiers import code_sandbox

    def fail(*args, **kwargs):
        raise OSError("launch failed")

    monkeypatch.setattr(code_sandbox.subprocess, "Popen", fail)
    result = run_in_python_sandbox("pass", "assert True")
    assert result.status == "runtime_error" and "launch failed" in result.stderr


def test_process_flags_environment_and_cleanup(tmp_path, monkeypatch):
    from vi_en_eval.verifiers import code_sandbox

    original = code_sandbox.tempfile.TemporaryDirectory

    def temporary_directory(**kwargs):
        return original(dir=tmp_path, **kwargs)

    monkeypatch.setattr(code_sandbox.tempfile, "TemporaryDirectory", temporary_directory)
    monkeypatch.setenv("EVALUATION_SECRET_SENTINEL", "must-not-be-inherited")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    policy = ASTAnalysisPolicy(allowed_modules=frozenset({"sys", "os"}), banned_modules=frozenset())
    # Expanded policy is confined to this reviewed fixture that inspects process settings.
    report = run_in_python_sandbox(
        "import sys\nimport os\nassert sys.flags.isolated == 1\n"
        "assert sys.dont_write_bytecode\nassert sys.flags.utf8_mode == 1\n"
        "assert 'EVALUATION_SECRET_SENTINEL' not in os.environ\n"
        "assert 'PYTHONPATH' not in os.environ\n",
        "assert True",
        policy,
    )
    assert report.passed, report.stderr
    assert list(tmp_path.iterdir()) == []


def test_existing_reviewed_iterable_and_dedup_counterexamples():
    import inspect

    from tests.fixtures.technical_case_implementations import (
        iterable_mean_candidate_a,
        iterable_mean_candidate_b,
        stable_dedup_candidate_a,
        stable_dedup_candidate_b,
    )

    prelude = "from collections.abc import Iterable\nfrom typing import TypeVar\n_ItemT = TypeVar('_ItemT')\n"
    for a, b, fixtures in (
        (
            iterable_mean_candidate_a,
            iterable_mean_candidate_b,
            "assert solve(iter([2.0, -1.0, 4.0])) == 3.0",
        ),
        (
            stable_dedup_candidate_a,
            stable_dedup_candidate_b,
            "assert solve([['x'], ['y'], ['x']]) == [['x'], ['y']]",
        ),
    ):
        source_a = prelude + inspect.getsource(a).replace(a.__name__, "solve")
        source_b = prelude + inspect.getsource(b).replace(b.__name__, "solve")
        report = compare_code_candidates_ab(source_a, source_b, fixtures)
        assert report.winner == "model_b", report
