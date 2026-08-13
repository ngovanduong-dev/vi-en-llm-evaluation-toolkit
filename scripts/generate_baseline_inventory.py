"""Generate and verify the repository's deterministic baseline inventory."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any

ARTIFACT_SCHEMA_VERSION = 1
ARTIFACT_PATH = "artifacts/baseline/current_state.json"
GENERATOR_PATH = "scripts/generate_baseline_inventory.py"
PACKAGE_DIRECTORY = "src/vi_en_eval"
SCHEMA_MODULE = "vi_en_eval.schemas"
VALIDATOR_MODULE = "vi_en_eval.jsonl_validator"
PLUGIN_AUTOLOAD_ENV = "PYTEST_DISABLE_PLUGIN_AUTOLOAD"
INPUT_HASH_NORMALIZATION = "utf-8-lf"

JSONL_SCHEMA_BINDINGS: tuple[tuple[str, str], ...] = (
    ("data/sample_evaluations.jsonl", "evaluation"),
    ("data/sample_prompts.jsonl", "prompt"),
    ("data/sample_responses.jsonl", "response"),
)

STATIC_HASH_INPUTS: tuple[str, ...] = (
    GENERATOR_PATH,
    "pyproject.toml",
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class InventoryError(RuntimeError):
    """An input or collection failure that makes the inventory invalid."""


@contextmanager
def _isolated_runtime_environment() -> Iterator[None]:
    """Disable bytecode and external pytest plugins without leaking process state."""

    previous_bytecode_setting = sys.dont_write_bytecode
    previous_plugin_setting = os.environ.get(PLUGIN_AUTOLOAD_ENV)
    sys.dont_write_bytecode = True
    os.environ[PLUGIN_AUTOLOAD_ENV] = "1"
    try:
        yield
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
        if previous_plugin_setting is None:
            os.environ.pop(PLUGIN_AUTOLOAD_ENV, None)
        else:
            os.environ[PLUGIN_AUTOLOAD_ENV] = previous_plugin_setting


def _canonical_relative_literal(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or (path.parts and ":" in path.parts[0])
        or any(ord(character) < 32 for character in normalized)
    ):
        raise InventoryError(f"Invalid repository-relative path: {value!r}")
    if path.as_posix() != normalized:
        raise InventoryError(f"Path is not canonical POSIX form: {value!r}")
    return path.as_posix()


def _repository_file(root: Path, path: Path) -> tuple[Path, str]:
    if path.is_symlink():
        raise InventoryError(f"Symlinked input is not allowed: {path}")
    if not path.is_file():
        raise InventoryError(f"Required input file is missing: {path}")

    root_resolved = root.resolve(strict=True)
    resolved = path.resolve(strict=True)
    try:
        relative = resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise InventoryError(f"Input path escapes the repository: {path}") from exc

    relative_posix = _canonical_relative_literal(relative.as_posix())
    return resolved, relative_posix


def _require_directory(root: Path, relative_path: str) -> Path:
    canonical = _canonical_relative_literal(relative_path)
    path = root / Path(canonical)
    if path.is_symlink() or not path.is_dir():
        raise InventoryError(f"Required directory is missing or invalid: {canonical}")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise InventoryError(f"Directory escapes the repository: {canonical}") from exc
    return path


def _ensure_unique_paths(paths: Iterable[str], *, label: str) -> list[str]:
    ordered = sorted(paths)
    seen: dict[str, str] = {}
    for path in ordered:
        canonical = _canonical_relative_literal(path)
        folded = canonical.casefold()
        previous = seen.get(folded)
        if previous is not None:
            raise InventoryError(f"Duplicate {label} paths: {previous!r} and {canonical!r}")
        seen[folded] = canonical
    return ordered


def _is_under(relative_path: str, directory: str) -> bool:
    path_parts = PurePosixPath(relative_path).parts
    directory_parts = PurePosixPath(directory).parts
    return path_parts[: len(directory_parts)] == directory_parts


def discover_files(
    root: Path,
    directory: str,
    suffix: str,
    *,
    excluded_directories: Sequence[str] = (),
    exclude_readme: bool = False,
) -> list[str]:
    """Discover deterministic regular files under one repository directory."""

    base = _require_directory(root, directory)
    discovered: list[str] = []
    for candidate in base.rglob("*"):
        lexical_relative = candidate.relative_to(root).as_posix()
        if any(_is_under(lexical_relative, excluded) for excluded in excluded_directories):
            continue
        if candidate.is_symlink():
            if candidate.suffix == suffix:
                raise InventoryError(f"Symlinked input is not allowed: {lexical_relative}")
            continue
        if not candidate.is_file() or candidate.suffix != suffix:
            continue
        if exclude_readme and candidate.name.casefold() == "readme.md":
            continue
        _, relative = _repository_file(root, candidate)
        discovered.append(relative)

    return _ensure_unique_paths(discovered, label=directory)


def describe_runtime_schemas(registry: object) -> list[dict[str, str]]:
    """Validate and describe actual entries in the runtime schema registry."""

    try:
        from pydantic import BaseModel
    except Exception as exc:  # pragma: no cover - dependency failure is integration-only
        raise InventoryError(f"Unable to import Pydantic: {type(exc).__name__}: {exc}") from exc

    if not isinstance(registry, Mapping):
        raise InventoryError(f"{SCHEMA_MODULE}.SCHEMA_REGISTRY must be a mapping")

    registered: list[dict[str, str]] = []
    for name, model in registry.items():
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise InventoryError("Runtime schema names must be non-blank canonical strings")
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise InventoryError(f"Runtime schema {name!r} is not a Pydantic BaseModel subclass")
        registered.append(
            {
                "model": f"{model.__module__}:{model.__qualname__}",
                "name": name,
            }
        )

    if not registered:
        raise InventoryError("Runtime schema registry is empty")
    return sorted(registered, key=lambda entry: entry["name"])


def _import_runtime_components(root: Path) -> tuple[object, Callable[..., Any]]:
    source_directory = _require_directory(root, "src")
    source_text = str(source_directory.resolve(strict=True))
    inserted = source_text not in sys.path
    if inserted:
        sys.path.insert(0, source_text)
    try:
        importlib.invalidate_caches()
        schemas_module = importlib.import_module(SCHEMA_MODULE)
        validator_module = importlib.import_module(VALIDATOR_MODULE)
    except Exception as exc:
        raise InventoryError(
            f"Unable to import runtime schema registry or validator: {type(exc).__name__}: {exc}"
        ) from exc
    finally:
        if inserted:
            sys.path.remove(source_text)

    for module, expected_path in (
        (schemas_module, f"{PACKAGE_DIRECTORY}/schemas.py"),
        (validator_module, f"{PACKAGE_DIRECTORY}/jsonl_validator.py"),
    ):
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            raise InventoryError(f"Imported module has no source path: {module.__name__}")
        _, relative = _repository_file(root, Path(module_file))
        if relative != expected_path:
            raise InventoryError(
                f"Imported {module.__name__} from {relative!r}, expected {expected_path!r}"
            )

    registry = getattr(schemas_module, "SCHEMA_REGISTRY", None)
    validator = getattr(validator_module, "validate_jsonl", None)
    if not callable(validator):
        raise InventoryError(f"{VALIDATOR_MODULE}.validate_jsonl is not callable")
    return registry, validator


def validate_jsonl_bindings(
    discovered_paths: Sequence[str],
    bindings: Sequence[tuple[str, str]],
    schema_names: Iterable[str],
) -> list[tuple[str, str]]:
    """Require the discovered public JSONL set to equal the semantic binding set."""

    valid_schema_names = set(schema_names)
    binding_by_path: dict[str, tuple[str, str]] = {}
    for raw_path, schema_name in bindings:
        path = _canonical_relative_literal(raw_path)
        folded = path.casefold()
        if folded in binding_by_path:
            previous = binding_by_path[folded][0]
            raise InventoryError(f"Duplicate JSONL bindings: {previous!r} and {path!r}")
        if schema_name not in valid_schema_names:
            raise InventoryError(f"JSONL binding {path!r} uses unknown schema {schema_name!r}")
        binding_by_path[folded] = (path, schema_name)

    discovered = _ensure_unique_paths(discovered_paths, label="JSONL")
    discovered_by_folded = {path.casefold(): path for path in discovered}
    binding_keys = set(binding_by_path)
    discovered_keys = set(discovered_by_folded)
    missing = sorted(binding_by_path[key][0] for key in binding_keys - discovered_keys)
    unmapped = sorted(discovered_by_folded[key] for key in discovered_keys - binding_keys)
    if missing or unmapped:
        details: list[str] = []
        if missing:
            details.append(f"missing mapped files: {', '.join(missing)}")
        if unmapped:
            details.append(f"unmapped discovered files: {', '.join(unmapped)}")
        raise InventoryError("JSONL binding mismatch (" + "; ".join(details) + ")")

    return sorted((discovered_by_folded[key], binding_by_path[key][1]) for key in discovered_keys)


def _jsonl_line_counts(path: Path) -> tuple[int, int]:
    line_count = 0
    record_count = 0
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for line in handle:
                line_count += 1
                if line.strip():
                    record_count += 1
    except (OSError, UnicodeError) as exc:
        raise InventoryError(
            f"Unable to read JSONL input {path}: {type(exc).__name__}: {exc}"
        ) from exc
    return line_count, record_count


def collect_jsonl_inventory(
    root: Path,
    bindings: Sequence[tuple[str, str]],
    validator: Callable[..., Any],
) -> list[dict[str, Any]]:
    """Validate every bound JSONL file and return stable per-file metadata."""

    files: list[dict[str, Any]] = []
    invalid_paths: list[str] = []
    for relative_path, schema_name in bindings:
        path, canonical_path = _repository_file(root, root / Path(relative_path))
        line_count, record_count = _jsonl_line_counts(path)
        try:
            result = validator(path, schema_name=schema_name)
        except Exception as exc:
            raise InventoryError(
                f"JSONL validator failed for {canonical_path}: {type(exc).__name__}: {exc}"
            ) from exc

        issues = sorted(
            (
                {
                    "code": issue.code,
                    "field": issue.field,
                    "line_number": issue.line_number,
                    "message": issue.message,
                }
                for issue in result.issues
            ),
            key=lambda issue: (
                issue["line_number"],
                issue["code"],
                issue["field"] or "",
                issue["message"],
            ),
        )
        status = "valid" if result.is_valid else "invalid"
        if status != "valid":
            invalid_paths.append(canonical_path)
        if result.total_lines != line_count:
            raise InventoryError(f"Validator line count mismatch for {canonical_path}")

        files.append(
            {
                "line_count": line_count,
                "path": canonical_path,
                "record_count": record_count,
                "schema": schema_name,
                "valid_record_count": result.valid_records,
                "validation": {
                    "issues": issues,
                    "status": status,
                },
            }
        )

    if invalid_paths:
        raise InventoryError("JSONL validation failed: " + ", ".join(sorted(invalid_paths)))
    return sorted(files, key=lambda entry: entry["path"])


def _validate_documents(root: Path, paths: Sequence[str], *, label: str) -> list[str]:
    for relative_path in paths:
        path, _ = _repository_file(root, root / Path(relative_path))
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise InventoryError(
                f"Unable to read {label} {relative_path}: {type(exc).__name__}: {exc}"
            ) from exc
        if not content.strip():
            raise InventoryError(f"{label.capitalize()} is empty: {relative_path}")
    return list(paths)


class _PytestCollectionPlugin:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.nodeids: list[str] = []
        self.file_counts: Counter[str] = Counter()
        self.errors: list[str] = []

    def pytest_collection_finish(self, session: Any) -> None:
        nodeids: list[str] = []
        file_counts: Counter[str] = Counter()
        for item in session.items:
            item_path = Path(item.path)
            _, relative_path = _repository_file(self.root, item_path)
            _, separator, suffix = item.nodeid.partition("::")
            nodeid = relative_path + (f"::{suffix}" if separator else "")
            nodeids.append(nodeid)
            file_counts[relative_path] += 1
        self.nodeids = sorted(nodeids)
        self.file_counts = file_counts

    def pytest_collectreport(self, report: Any) -> None:
        if report.failed:
            details = getattr(report, "longreprtext", str(report.longrepr))
            summary = str(details).splitlines()[0] if details else "collection failed"
            self.errors.append(f"{report.nodeid}: {summary}")


def collect_pytest_inventory(root: Path) -> dict[str, Any]:
    """Collect final pytest items through hooks without executing test bodies."""

    tests_directory = _require_directory(root, "tests")
    plugin = _PytestCollectionPlugin(root)
    with _isolated_runtime_environment():
        try:
            pytest = importlib.import_module("pytest")
            exit_code = pytest.main(
                [
                    "--collect-only",
                    "-o",
                    "addopts=",
                    "-p",
                    "no:cacheprovider",
                    "-p",
                    "no:terminal",
                    "--rootdir",
                    str(root.resolve(strict=True)),
                    str(tests_directory.resolve(strict=True)),
                ],
                plugins=[plugin],
            )
        except Exception as exc:
            raise InventoryError(f"Pytest collection failed: {type(exc).__name__}: {exc}") from exc

    if exit_code != pytest.ExitCode.OK:
        details = "; ".join(sorted(plugin.errors)) or f"pytest exit code {int(exit_code)}"
        raise InventoryError(f"Pytest collection failed: {details}")
    if plugin.errors:
        raise InventoryError("Pytest collection failed: " + "; ".join(sorted(plugin.errors)))
    if not plugin.nodeids:
        raise InventoryError("Pytest collection returned zero test cases")

    files = [
        {
            "collected_test_case_count": plugin.file_counts[path],
            "path": path,
        }
        for path in sorted(plugin.file_counts)
    ]
    return {
        "collected_test_case_count": len(plugin.nodeids),
        "collection": {
            "cache_provider": False,
            "external_plugin_autoload": False,
            "mode": "pytest.main --collect-only",
            "test_execution": False,
        },
        "file_count": len(files),
        "files": files,
        "nodeids": plugin.nodeids,
    }


def _compact_canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_utf8_lf_bytes(path: Path) -> bytes:
    """Read strict UTF-8 without a BOM and normalize CRLF or lone CR to LF."""

    try:
        content = path.read_bytes()
    except OSError as exc:
        raise InventoryError(
            f"Unable to read hash input {path}: {type(exc).__name__}: {exc}"
        ) from exc
    if content.startswith(b"\xef\xbb\xbf"):
        raise InventoryError(f"UTF-8 BOM is not allowed in hash input: {path}")
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise InventoryError(f"Hash input is not valid UTF-8 text: {path}") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.encode("utf-8")


def build_input_hash(root: Path, input_paths: Iterable[str]) -> dict[str, Any]:
    """Hash canonical UTF-8/LF public content and its sorted manifest."""

    paths = _ensure_unique_paths(input_paths, label="hash input")
    if ARTIFACT_PATH.casefold() in {path.casefold() for path in paths}:
        raise InventoryError("The baseline artifact cannot hash itself")

    files: list[dict[str, str]] = []
    for relative_path in paths:
        path, canonical_path = _repository_file(root, root / Path(relative_path))
        digest = hashlib.sha256(_canonical_utf8_lf_bytes(path)).hexdigest()
        files.append({"path": canonical_path, "sha256": digest})

    aggregate = hashlib.sha256(_compact_canonical_json(files)).hexdigest()
    return {
        "algorithm": "sha256",
        "files": files,
        "normalization": INPUT_HASH_NORMALIZATION,
        "value": aggregate,
    }


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return the canonical public artifact encoding."""

    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _validate_inventory_relationships(payload: Mapping[str, Any]) -> None:
    schemas = payload["runtime_schemas"]
    jsonl = payload["jsonl"]
    portfolio = payload["portfolio_samples"]
    rubrics = payload["rubrics"]
    tests = payload["tests"]

    checks = (
        (schemas["count"], len(schemas["names"]), "runtime schema count"),
        (schemas["count"], len(schemas["registered"]), "runtime schema entries"),
        (jsonl["file_count"], len(jsonl["files"]), "JSONL file count"),
        (
            jsonl["total_line_count"],
            sum(entry["line_count"] for entry in jsonl["files"]),
            "JSONL line total",
        ),
        (
            jsonl["total_record_count"],
            sum(entry["record_count"] for entry in jsonl["files"]),
            "JSONL record total",
        ),
        (
            jsonl["total_valid_record_count"],
            sum(entry["valid_record_count"] for entry in jsonl["files"]),
            "valid JSONL record total",
        ),
        (portfolio["count"], len(portfolio["paths"]), "portfolio sample count"),
        (rubrics["standalone_document_count"], len(rubrics["paths"]), "rubric count"),
        (tests["file_count"], len(tests["files"]), "test file count"),
        (tests["collected_test_case_count"], len(tests["nodeids"]), "test case count"),
        (
            tests["collected_test_case_count"],
            sum(entry["collected_test_case_count"] for entry in tests["files"]),
            "per-file test case total",
        ),
    )
    for actual, expected, label in checks:
        if actual != expected:
            raise InventoryError(
                f"Inventory relationship failed for {label}: {actual} != {expected}"
            )


def build_inventory(
    root: Path = REPOSITORY_ROOT,
    *,
    bindings: Sequence[tuple[str, str]] = JSONL_SCHEMA_BINDINGS,
) -> dict[str, Any]:
    """Build a complete valid inventory in memory without writing files."""

    root = root.resolve(strict=True)
    with _isolated_runtime_environment():
        registry, validator = _import_runtime_components(root)
        registered = describe_runtime_schemas(registry)
        schema_names = [entry["name"] for entry in registered]

        discovered_jsonl = discover_files(
            root,
            "data",
            ".jsonl",
            excluded_directories=("data/private",),
        )
        validated_bindings = validate_jsonl_bindings(
            discovered_jsonl,
            bindings,
            schema_names,
        )
        jsonl_files = collect_jsonl_inventory(root, validated_bindings, validator)

        portfolio_paths = _validate_documents(
            root,
            discover_files(
                root,
                "portfolio_samples",
                ".md",
                exclude_readme=True,
            ),
            label="portfolio sample",
        )
        rubric_paths = _validate_documents(
            root,
            discover_files(root, "rubrics", ".md", exclude_readme=True),
            label="rubric document",
        )
        tests = collect_pytest_inventory(root)
        test_python_paths = discover_files(root, "tests", ".py")
        package_python_paths = discover_files(root, PACKAGE_DIRECTORY, ".py")

        input_paths = [
            *STATIC_HASH_INPUTS,
            *package_python_paths,
            *discovered_jsonl,
            *portfolio_paths,
            *rubric_paths,
            *test_python_paths,
        ]
        input_hash = build_input_hash(root, input_paths)

    payload: dict[str, Any] = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "jsonl": {
            "file_count": len(jsonl_files),
            "files": jsonl_files,
            "total_line_count": sum(entry["line_count"] for entry in jsonl_files),
            "total_record_count": sum(entry["record_count"] for entry in jsonl_files),
            "total_valid_record_count": sum(entry["valid_record_count"] for entry in jsonl_files),
        },
        "portfolio_samples": {
            "count": len(portfolio_paths),
            "paths": portfolio_paths,
        },
        "provenance": {
            "generator": GENERATOR_PATH,
            "input_hash": input_hash,
        },
        "rubrics": {
            "paths": rubric_paths,
            "standalone_document_count": len(rubric_paths),
        },
        "runtime_schemas": {
            "count": len(registered),
            "names": schema_names,
            "registered": registered,
            "registry": f"{SCHEMA_MODULE}:SCHEMA_REGISTRY",
        },
        "status": "valid",
        "tests": tests,
    }
    _validate_inventory_relationships(payload)
    return payload


def write_artifact_atomic(path: Path, content: bytes) -> None:
    """Atomically replace the artifact using a temporary file beside it."""

    if path.is_symlink():
        raise InventoryError(f"Artifact path must not be a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _emit_stdout(content: bytes) -> None:
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("generate", "check"))
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Write canonical generated JSON to stdout; diagnostics remain on stderr.",
    )
    return parser


def main(argv: Sequence[str] | None = None, *, root: Path = REPOSITORY_ROOT) -> int:
    args = create_argument_parser().parse_args(argv)
    root = root.resolve(strict=True)
    artifact_path = root / Path(ARTIFACT_PATH)

    try:
        payload = build_inventory(root)
        candidate = canonical_json_bytes(payload)

        if args.mode == "generate":
            write_artifact_atomic(artifact_path, candidate)
            print(f"Generated {ARTIFACT_PATH}", file=sys.stderr)
            if args.stdout:
                _emit_stdout(candidate)
            return 0

        if artifact_path.is_symlink():
            raise InventoryError(f"Artifact path must not be a symlink: {ARTIFACT_PATH}")
        if not artifact_path.is_file():
            print(f"Baseline artifact is missing: {ARTIFACT_PATH}", file=sys.stderr)
            if args.stdout:
                _emit_stdout(candidate)
            return 1
        current = artifact_path.read_bytes()
        if current != candidate:
            print(
                f"Baseline artifact does not match generated output: {ARTIFACT_PATH}",
                file=sys.stderr,
            )
            if args.stdout:
                _emit_stdout(candidate)
            return 1

        print(f"Baseline artifact is current: {ARTIFACT_PATH}", file=sys.stderr)
        if args.stdout:
            _emit_stdout(candidate)
        return 0
    except InventoryError as exc:
        print(f"Baseline inventory error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(
            f"Baseline inventory error: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
