from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from pydantic import BaseModel
import pytest

from scripts import generate_baseline_inventory as baseline
from src.jsonl_validator import validate_jsonl


class ExampleRecord(BaseModel):
    value: str


class UnregisteredRecord(BaseModel):
    other: int


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _payload() -> dict:
    return {
        "artifact_schema_version": baseline.ARTIFACT_SCHEMA_VERSION,
        "message": "Dữ liệu công khai",
        "status": "valid",
    }


def test_runtime_registry_is_read_dynamically_and_sorted():
    registry = {"zeta": ExampleRecord, "alpha": ExampleRecord}

    registered = baseline.describe_runtime_schemas(registry)

    assert [entry["name"] for entry in registered] == sorted(registry)
    assert all(entry["model"].endswith(":ExampleRecord") for entry in registered)


def test_unregistered_models_are_not_counted():
    registry = {"example": ExampleRecord}

    registered = baseline.describe_runtime_schemas(registry)

    assert [entry["name"] for entry in registered] == ["example"]
    assert UnregisteredRecord.__name__ not in {entry["model"] for entry in registered}


@pytest.mark.parametrize(
    "registry",
    [
        {},
        {"": ExampleRecord},
        {"invalid": object},
        [("example", ExampleRecord)],
    ],
)
def test_invalid_runtime_registry_is_rejected(registry):
    with pytest.raises(baseline.InventoryError):
        baseline.describe_runtime_schemas(registry)


def test_jsonl_discovery_and_bindings_match_exactly(tmp_path):
    _write(tmp_path / "data" / "one.jsonl", '{"id":"one"}\n')
    _write(tmp_path / "data" / "nested" / "two.jsonl", '{"id":"two"}\n')
    _write(tmp_path / "data" / "private" / "hidden.jsonl", '{"id":"hidden"}\n')

    discovered = baseline.discover_files(
        tmp_path,
        "data",
        ".jsonl",
        excluded_directories=("data/private",),
    )
    bindings = baseline.validate_jsonl_bindings(
        discovered,
        (("data/one.jsonl", "first"), ("data/nested/two.jsonl", "second")),
        {"first", "second"},
    )

    assert [path for path, _ in bindings] == sorted(discovered)
    assert all("hidden" not in path for path in discovered)


def test_jsonl_binding_mismatch_and_duplicates_fail(tmp_path):
    _write(tmp_path / "data" / "one.jsonl", "{}\n")
    discovered = baseline.discover_files(tmp_path, "data", ".jsonl")

    with pytest.raises(baseline.InventoryError, match="unmapped discovered files"):
        baseline.validate_jsonl_bindings(discovered, (), {"example"})
    with pytest.raises(baseline.InventoryError, match="missing mapped files"):
        baseline.validate_jsonl_bindings(
            discovered,
            (("data/one.jsonl", "example"), ("data/missing.jsonl", "example")),
            {"example"},
        )
    with pytest.raises(baseline.InventoryError, match="Duplicate JSONL bindings"):
        baseline.validate_jsonl_bindings(
            discovered,
            (("data/one.jsonl", "example"), ("DATA/ONE.JSONL", "example")),
            {"example"},
        )


def test_document_discovery_excludes_indexes(tmp_path):
    _write(tmp_path / "portfolio_samples" / "README.md", "# Index\n")
    _write(tmp_path / "portfolio_samples" / "group" / "sample.md", "# Sample\n")
    _write(tmp_path / "rubrics" / "README.md", "# Index\n")
    _write(tmp_path / "rubrics" / "rubric.md", "# Rubric\n")

    samples = baseline.discover_files(
        tmp_path,
        "portfolio_samples",
        ".md",
        exclude_readme=True,
    )
    rubrics = baseline.discover_files(tmp_path, "rubrics", ".md", exclude_readme=True)

    assert samples == ["portfolio_samples/group/sample.md"]
    assert rubrics == ["rubrics/rubric.md"]


def test_jsonl_counts_are_derived_from_file_and_validator(tmp_path):
    path = _write(tmp_path / "data" / "example.jsonl", '{"id":"one"}\n\n{"id":"two"}\n')
    result = SimpleNamespace(
        is_valid=True,
        issues=[],
        total_lines=3,
        valid_records=2,
    )

    files = baseline.collect_jsonl_inventory(
        tmp_path,
        (("data/example.jsonl", "example"),),
        lambda *_args, **_kwargs: result,
    )

    assert files[0]["line_count"] == len(path.read_text(encoding="utf-8").splitlines())
    assert files[0]["record_count"] == 2
    assert files[0]["valid_record_count"] == result.valid_records


def test_malformed_jsonl_fails_closed(tmp_path):
    _write(tmp_path / "data" / "broken.jsonl", '{"id":"broken"\n')

    with pytest.raises(baseline.InventoryError, match="JSONL validation failed"):
        baseline.collect_jsonl_inventory(
            tmp_path,
            (("data/broken.jsonl", "evaluation"),),
            validate_jsonl,
        )


def test_collection_counts_final_items_without_running_tests(tmp_path):
    _write(tmp_path / "pytest.ini", "[pytest]\ntestpaths = tests\n")
    _write(
        tmp_path / "tests" / "test_fixture.py",
        "from pathlib import Path\n"
        "import pytest\n\n"
        "@pytest.mark.parametrize('value', [1, 2])\n"
        "def test_parameterized(value):\n"
        "    Path(__file__).with_name('executed.txt').write_text(str(value))\n",
    )
    previous_bytecode_setting = sys.dont_write_bytecode
    previous_plugin_setting = os.environ.get(baseline.PLUGIN_AUTOLOAD_ENV)

    inventory = baseline.collect_pytest_inventory(tmp_path)

    assert inventory["collected_test_case_count"] == len(inventory["nodeids"])
    assert inventory["collected_test_case_count"] == 2
    assert inventory["file_count"] == len(inventory["files"])
    assert not (tmp_path / "tests" / "executed.txt").exists()
    assert not (tmp_path / ".pytest_cache").exists()
    assert list(tmp_path.rglob("__pycache__")) == []
    assert sys.dont_write_bytecode is previous_bytecode_setting
    assert os.environ.get(baseline.PLUGIN_AUTOLOAD_ENV) == previous_plugin_setting


def test_collection_error_and_zero_items_fail(tmp_path):
    _write(tmp_path / "pytest.ini", "[pytest]\ntestpaths = tests\n")
    _write(tmp_path / "tests" / "test_broken.py", "def test_broken(:\n")

    with pytest.raises(baseline.InventoryError, match="Pytest collection failed"):
        baseline.collect_pytest_inventory(tmp_path)

    (tmp_path / "tests" / "test_broken.py").unlink()
    with pytest.raises(baseline.InventoryError, match="zero test cases|exit code 5"):
        baseline.collect_pytest_inventory(tmp_path)


def test_path_normalization_and_symlink_behavior(tmp_path, monkeypatch):
    assert baseline._canonical_relative_literal("tests\\test_example.py") == (
        "tests/test_example.py"
    )
    with pytest.raises(baseline.InventoryError):
        baseline._canonical_relative_literal("../outside.py")

    _write(tmp_path / "data" / "target.jsonl", "{}\n")
    link = tmp_path / "data" / "link.jsonl"
    _write(link, "{}\n")
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == link or original_is_symlink(self),
    )
    with pytest.raises(baseline.InventoryError, match="Symlinked input"):
        baseline.discover_files(tmp_path, "data", ".jsonl")


def test_canonical_json_bytes_are_stable_utf8_lf():
    first = {"z": "Tiếng Việt", "a": {"two": 2, "one": 1}}
    second = {"a": {"one": 1, "two": 2}, "z": "Tiếng Việt"}

    first_bytes = baseline.canonical_json_bytes(first)
    second_bytes = baseline.canonical_json_bytes(second)

    assert first_bytes == second_bytes
    assert first_bytes.endswith(b"\n")
    assert b"\r\n" not in first_bytes
    assert not first_bytes.startswith(b"\xef\xbb\xbf")
    assert json.loads(first_bytes.decode("utf-8")) == first


def test_input_hash_uses_raw_bytes_and_sorted_manifest(tmp_path):
    first = _write(tmp_path / "first.txt", "first\n")
    second = _write(tmp_path / "second.txt", "second\n")

    forward = baseline.build_input_hash(tmp_path, ("second.txt", "first.txt"))
    reverse = baseline.build_input_hash(tmp_path, ("first.txt", "second.txt"))

    assert forward == reverse
    assert [entry["path"] for entry in forward["files"]] == ["first.txt", "second.txt"]
    assert forward["files"][0]["sha256"] == hashlib.sha256(first.read_bytes()).hexdigest()

    second.write_bytes(b"changed\n")
    changed = baseline.build_input_hash(tmp_path, ("first.txt", "second.txt"))
    assert changed["value"] != forward["value"]


def test_artifact_is_rejected_as_a_hash_input(tmp_path):
    _write(tmp_path / baseline.ARTIFACT_PATH, "{}\n")

    with pytest.raises(baseline.InventoryError, match="cannot hash itself"):
        baseline.build_input_hash(tmp_path, (baseline.ARTIFACT_PATH,))


def test_generate_is_byte_stable_and_check_does_not_write(tmp_path, monkeypatch):
    monkeypatch.setattr(baseline, "build_inventory", lambda _root: _payload())

    assert baseline.main(["generate"], root=tmp_path) == 0
    artifact = tmp_path / baseline.ARTIFACT_PATH
    first_bytes = artifact.read_bytes()
    assert baseline.main(["generate"], root=tmp_path) == 0
    assert artifact.read_bytes() == first_bytes

    monkeypatch.setattr(
        baseline,
        "write_artifact_atomic",
        lambda *_args: pytest.fail("check mode attempted to write"),
    )
    assert baseline.main(["check"], root=tmp_path) == 0
    assert artifact.read_bytes() == first_bytes


def test_check_missing_and_mismatch_return_drift_code(tmp_path, monkeypatch):
    monkeypatch.setattr(baseline, "build_inventory", lambda _root: _payload())

    assert baseline.main(["check"], root=tmp_path) == 1
    artifact = _write(tmp_path / baseline.ARTIFACT_PATH, "{}\n")
    before = artifact.read_bytes()
    assert baseline.main(["check"], root=tmp_path) == 1
    assert artifact.read_bytes() == before


def test_source_failure_returns_error_code_without_overwrite(tmp_path, monkeypatch):
    artifact = _write(tmp_path / baseline.ARTIFACT_PATH, "preserve\n")
    before = artifact.read_bytes()

    def fail(_root):
        raise baseline.InventoryError("source is invalid")

    monkeypatch.setattr(baseline, "build_inventory", fail)

    assert baseline.main(["generate"], root=tmp_path) == 2
    assert artifact.read_bytes() == before


def test_stdout_contains_only_canonical_payload(tmp_path, monkeypatch, capfd):
    monkeypatch.setattr(baseline, "build_inventory", lambda _root: _payload())

    assert baseline.main(["generate", "--stdout"], root=tmp_path) == 0
    captured = capfd.readouterr()

    assert captured.out.encode("utf-8") == baseline.canonical_json_bytes(_payload())
    assert "Generated" in captured.err


def test_repository_inventory_relationships_and_input_scope():
    payload = baseline.build_inventory()

    assert payload["status"] == "valid"
    assert payload["runtime_schemas"]["count"] == len(
        payload["runtime_schemas"]["registered"]
    )
    assert payload["jsonl"]["file_count"] == len(payload["jsonl"]["files"])
    assert payload["portfolio_samples"]["count"] == len(
        payload["portfolio_samples"]["paths"]
    )
    assert payload["rubrics"]["standalone_document_count"] == len(
        payload["rubrics"]["paths"]
    )
    assert payload["tests"]["collected_test_case_count"] == len(
        payload["tests"]["nodeids"]
    )

    input_paths = {
        entry["path"] for entry in payload["provenance"]["input_hash"]["files"]
    }
    assert baseline.ARTIFACT_PATH not in input_paths
    assert "AGENTS.md" not in input_paths
    assert all(not path.startswith("data/private/") for path in input_paths)
    assert all(not Path(path).is_absolute() for path in input_paths)


def test_committed_artifact_matches_generator():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            baseline.GENERATOR_PATH,
            "check",
        ],
        cwd=baseline.REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
