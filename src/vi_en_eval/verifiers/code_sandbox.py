"""AST-gated execution for reviewed fixtures in a separate Python process.

This runner is not an OS sandbox. Execute adversarial code only inside an
externally managed container or VM with filesystem, network, and resource limits.
"""

from __future__ import annotations

import math
import os

# Separate interpreter is the execution mechanism.
import subprocess  # nosec B404
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import BinaryIO, Literal

from pydantic import BaseModel, ConfigDict

from .ast_analyzer import ASTAnalysisPolicy, ASTAnalysisReport, analyze_python_ast

Status = Literal["passed", "blocked_by_ast", "assertion_failed", "runtime_error", "timeout"]
Winner = Literal["model_a", "model_b", "tie_both_pass", "tie_both_fail"]
_OUTPUT_LIMIT = 4000
_RUNNER = """import builtins
import traceback
from pathlib import Path

try:
    namespace = {"__builtins__": dict(vars(builtins)), "__name__": "candidate"}
    exec(compile(Path("candidate.py").read_text(encoding="utf-8"), "candidate.py", "exec"), namespace)
    namespace["__builtins__"] = dict(vars(builtins))
    exec(compile(Path("fixtures.py").read_text(encoding="utf-8"), "fixtures.py", "exec"), namespace)
except AssertionError:
    traceback.print_exc()
    raise SystemExit(11)
except BaseException:
    traceback.print_exc()
    raise SystemExit(12)
"""


class SandboxExecutionResult(BaseModel):
    """Runtime result, bounded output, and the candidate's static diagnostics."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    passed: bool
    status: Status
    exit_code: int | None
    duration_ms: float
    stdout: str
    stderr: str
    output_truncated: bool = False
    ast_report: ASTAnalysisReport


class PairwiseCodeComparisonReport(BaseModel):
    """Fixture outcomes, with static issue count as a deterministic tie-breaker."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    winner: Winner
    model_a_result: SandboxExecutionResult
    model_b_result: SandboxExecutionResult
    synthesized_english_rationale: str


class _Capture:
    """Drain a pipe without retaining unbounded output in memory."""

    def __init__(self) -> None:
        self.data = bytearray()
        self.truncated = False

    def drain(self, stream: BinaryIO) -> None:
        with stream:
            while chunk := stream.read(4096):
                room = _OUTPUT_LIMIT - len(self.data)
                self.data.extend(chunk[:room])
                self.truncated |= len(chunk) > room

    def text(self) -> str:
        return self.data.decode("utf-8", errors="replace")


def _execute(directory: str, timeout: float) -> tuple[Status, int | None, str, str, bool]:
    stdout, stderr = _Capture(), _Capture()
    # -I ignores PYTHON* variables; -X utf8 selects the child's encoding explicitly.
    environment = {key: os.environ[key] for key in ("SYSTEMROOT",) if key in os.environ}
    # Fixed interpreter, no shell; reviewed code only.
    with subprocess.Popen(  # nosec B603
        [sys.executable, "-I", "-B", "-X", "utf8", "runner.py"],
        cwd=directory,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        if process.stdout is None or process.stderr is None:
            raise RuntimeError("Failed to open execution pipes")
        readers = [
            threading.Thread(target=stdout.drain, args=(process.stdout,), daemon=True),
            threading.Thread(target=stderr.drain, args=(process.stderr,), daemon=True),
        ]
        for reader in readers:
            reader.start()
        status: Status
        try:
            code: int | None = process.wait(timeout=timeout)
            status = (
                "passed" if code == 0 else "assertion_failed" if code == 11 else "runtime_error"
            )
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            code, status = None, "timeout"
        for reader in readers:
            reader.join()
    error = stderr.text()
    if status == "timeout":
        error = f"TimeoutExpired: execution exceeded {timeout}s limit.\n{error}"
    return status, code, stdout.text(), error, stdout.truncated or stderr.truncated


def run_in_python_sandbox(
    candidate_code: str,
    test_harness_code: str,
    policy: ASTAnalysisPolicy | None = None,
    timeout_seconds: float = 2.5,
) -> SandboxExecutionResult:
    """Gate both sources, then run reviewed code and fixtures with a wall-clock timeout."""
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    if not test_harness_code.strip():
        raise ValueError("The test harness must not be blank")
    report = analyze_python_ast(candidate_code, policy)
    fixture_policy = (policy or ASTAnalysisPolicy()).model_copy(
        update={"require_function_name": None}
    )
    fixtures = analyze_python_ast(test_harness_code, fixture_policy)
    if not report.is_safe_to_execute or not fixtures.is_safe_to_execute:
        messages = [
            f"Candidate: {i.message}" for i in report.issues if i.category != "code_quality"
        ]
        messages.extend(
            f"Fixture: {i.message}" for i in fixtures.issues if i.category != "code_quality"
        )
        return SandboxExecutionResult(
            passed=False,
            status="blocked_by_ast",
            exit_code=None,
            duration_ms=0,
            stdout="",
            stderr="Execution blocked by AST policy: " + "; ".join(messages),
            ast_report=report,
        )
    start = time.perf_counter_ns()
    try:
        with tempfile.TemporaryDirectory(prefix="vi_en_eval_") as directory:
            for name, code in (
                ("runner.py", _RUNNER),
                ("candidate.py", candidate_code),
                ("fixtures.py", test_harness_code),
            ):
                Path(directory, name).write_text(code, encoding="utf-8")
            status, exit_code, stdout, stderr, truncated = _execute(directory, timeout_seconds)
    except OSError as exc:
        status, exit_code, stdout, stderr, truncated = (
            "runtime_error",
            None,
            "",
            f"Execution I/O failure: {exc}",
            False,
        )
    return SandboxExecutionResult(
        passed=status == "passed",
        status=status,
        exit_code=exit_code,
        duration_ms=round((time.perf_counter_ns() - start) / 1_000_000, 2),
        stdout=stdout,
        stderr=stderr,
        output_truncated=truncated,
        ast_report=report,
    )


def compare_code_candidates_ab(
    model_a_code: str,
    model_b_code: str,
    counterexample_test_code: str,
    policy: ASTAnalysisPolicy | None = None,
    timeout_seconds: float = 2.5,
) -> PairwiseCodeComparisonReport:
    """Compare fixture results; elapsed time is evidence only, never a ranking input."""
    a = run_in_python_sandbox(model_a_code, counterexample_test_code, policy, timeout_seconds)
    b = run_in_python_sandbox(model_b_code, counterexample_test_code, policy, timeout_seconds)
    winner: Winner
    if a.passed != b.passed:
        winner = "model_a" if a.passed else "model_b"
        failed = b if a.passed else a
        detail = failed.stderr.strip().splitlines()[-1] if failed.stderr.strip() else failed.status
        rationale = f"{winner} passed the supplied fixtures; the other candidate returned {failed.status}: {detail}"
    elif a.passed:
        count_a, count_b = len(a.ast_report.issues), len(b.ast_report.issues)
        winner = (
            "model_a" if count_a < count_b else "model_b" if count_b < count_a else "tie_both_pass"
        )
        rationale = (
            f"Both candidates passed the supplied fixtures. Static issue counts: "
            f"Model A={count_a}, Model B={count_b}; fewer issues break a runtime tie."
        )
    else:
        winner = "tie_both_fail"
        rationale = f"Neither candidate passed the supplied fixtures: Model A={a.status}, Model B={b.status}."
    return PairwiseCodeComparisonReport(
        winner=winner,
        model_a_result=a,
        model_b_result=b,
        synthesized_english_rationale=rationale,
    )
