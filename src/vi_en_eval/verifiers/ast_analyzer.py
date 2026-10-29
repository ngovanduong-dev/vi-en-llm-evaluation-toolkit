"""Conservative syntax policy and module-level branch complexity estimates."""

from __future__ import annotations

import ast
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_BANNED_MODULES = frozenset(
    {"os", "subprocess", "sys", "shutil", "socket", "urllib", "http", "ctypes", "pickle"}
)
DEFAULT_BANNED_BUILTINS = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "input",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "vars",
        "breakpoint",
        "help",
        "exit",
        "quit",
    }
)
DEFAULT_ALLOWED_MODULES = frozenset(
    {
        "math",
        "statistics",
        "collections",
        "itertools",
        "functools",
        "decimal",
        "fractions",
        "re",
        "string",
        "heapq",
        "bisect",
        "typing",
        "__future__",
    }
)


class ASTAnalysisPolicy(BaseModel):
    """An allowlist for imports plus syntactic restrictions; not a security boundary."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    allowed_modules: frozenset[str] = DEFAULT_ALLOWED_MODULES
    banned_modules: frozenset[str] = DEFAULT_BANNED_MODULES
    banned_builtins: frozenset[str] = DEFAULT_BANNED_BUILTINS
    require_function_name: str | None = Field(default=None, min_length=1)
    require_type_annotations: bool = True
    forbid_mutable_default_args: bool = True
    forbid_bare_except: bool = True


class ASTIssue(BaseModel):
    """Source location and evidence for one static diagnostic."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    category: Literal["syntax_error", "security_violation", "code_quality", "missing_symbol"]
    lineno: int
    col_offset: int
    message: str


class ASTAnalysisReport(BaseModel):
    """Static findings; is_safe_to_execute means only that the gate accepted syntax."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    is_safe_to_execute: bool
    passed_all_checks: bool
    defined_functions: tuple[str, ...]
    branch_complexity_score: int
    issues: tuple[ASTIssue, ...]


def _mutable_default(node: ast.AST) -> bool:
    if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
        return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id in {"list", "dict", "set", "bytearray"}
    return isinstance(node, ast.Tuple) and any(_mutable_default(child) for child in node.elts)


def _branches(node: ast.AST) -> int:
    if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler)):
        return 1
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    if isinstance(node, ast.match_case):
        return int(
            not isinstance(node.pattern, ast.MatchAs) or node.pattern.pattern is not None
        ) + int(node.guard is not None)
    return 0


def analyze_python_ast(
    source_code: str, policy: ASTAnalysisPolicy | None = None
) -> ASTAnalysisReport:
    """Inspect imports, restricted references, function signatures, and decision points."""
    active = policy or ASTAnalysisPolicy()
    issues: list[ASTIssue] = []

    def add(
        node: ast.AST, category: Literal["security_violation", "code_quality"], message: str
    ) -> None:
        issues.append(
            ASTIssue(
                category=category,
                lineno=getattr(node, "lineno", 1),
                col_offset=getattr(node, "col_offset", 0),
                message=message,
            )
        )

    try:
        tree = ast.parse(source_code)
        # Compilation validates context errors that ast.parse accepts, such as top-level return.
        compile(tree, "<candidate>", "exec", dont_inherit=True)
    except (SyntaxError, ValueError, RecursionError) as exc:
        return ASTAnalysisReport(
            is_safe_to_execute=False,
            passed_all_checks=False,
            defined_functions=(),
            branch_complexity_score=0,
            issues=(
                ASTIssue(
                    category="syntax_error",
                    lineno=getattr(exc, "lineno", None) or 1,
                    col_offset=max(0, (getattr(exc, "offset", None) or 1) - 1),
                    message=f"Invalid Python source: {exc}",
                ),
            ),
        )

    functions = tuple(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    top_level = {
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    complexity = 1
    for node in ast.walk(tree):
        complexity += _branches(node)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            for module in modules:
                root = module.split(".")[0]
                if (
                    root in active.banned_modules
                    or root not in active.allowed_modules
                    or (isinstance(node, ast.ImportFrom) and node.level)
                ):
                    add(
                        node,
                        "security_violation",
                        f"Import of restricted module '{module}' is forbidden.",
                    )
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if (
                        alias.name == "*"
                        or alias.name.startswith("_")
                        or alias.name in active.banned_builtins
                    ):
                        add(node, "security_violation", f"Restricted import member '{alias.name}'.")
        if isinstance(node, ast.Name) and (
            node.id in active.banned_builtins or node.id.startswith("__")
        ):
            add(node, "security_violation", f"Reference to restricted name '{node.id}'.")
        if isinstance(node, ast.Attribute) and (
            node.attr.startswith("_") or node.attr in active.banned_builtins
        ):
            add(node, "security_violation", f"Reference to restricted attribute '{node.attr}'.")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
            arguments += [arg for arg in (node.args.vararg, node.args.kwarg) if arg is not None]
            missing = [
                arg.arg
                for arg in arguments
                if arg.annotation is None and arg.arg not in {"self", "cls"}
            ]
            if active.require_type_annotations and (missing or node.returns is None):
                add(
                    node,
                    "code_quality",
                    f"Function '{node.name}' lacks complete type annotations "
                    f"(missing args: {missing}, return annotated: {node.returns is not None}).",
                )
            defaults = [*node.args.defaults, *(d for d in node.args.kw_defaults if d is not None)]
            if active.forbid_mutable_default_args:
                for default in defaults:
                    if _mutable_default(default):
                        add(
                            default,
                            "code_quality",
                            f"Function '{node.name}' has a mutable default argument; "
                            "state may leak across calls.",
                        )
        if active.forbid_bare_except and isinstance(node, ast.ExceptHandler) and node.type is None:
            add(node, "code_quality", "Bare 'except:' clause; catch specific exceptions.")
    if active.require_function_name and active.require_function_name not in top_level:
        issues.append(
            ASTIssue(
                category="missing_symbol",
                lineno=1,
                col_offset=0,
                message=f"Required top-level function '{active.require_function_name}' is missing.",
            )
        )
    return ASTAnalysisReport(
        is_safe_to_execute=not any(
            i.category in {"security_violation", "missing_symbol"} for i in issues
        ),
        passed_all_checks=not issues,
        defined_functions=functions,
        branch_complexity_score=complexity,
        issues=tuple(issues),
    )
