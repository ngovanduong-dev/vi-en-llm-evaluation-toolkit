from src.code_checks import (
    CODING_REVIEW_CHECKLIST,
    check_python_syntax,
    validate_json_text,
    validate_jsonl_text,
)


def test_python_syntax_valid_code():
    result = check_python_syntax("def add(a, b):\n    return a + b\n")

    assert result.is_valid
    assert result.code == "valid_python_syntax"


def test_python_syntax_invalid_code():
    result = check_python_syntax("def broken(:\n    pass\n")

    assert not result.is_valid
    assert result.code == "python_syntax_error"
    assert result.message == "Python syntax error."


def test_validate_json_text_valid():
    result = validate_json_text('{"winner": "A", "score": 5}')

    assert result.is_valid
    assert result.code == "valid_json"


def test_validate_json_text_invalid():
    result = validate_json_text('{"winner": "A",}')

    assert not result.is_valid
    assert result.code == "invalid_json"
    assert result.line_number == 1
    assert result.column is not None


def test_validate_jsonl_text_reports_each_line():
    content = '{"id": "one"}\n{"id": "two",}\n{"id": "three"}\n'

    results = validate_jsonl_text(content)

    assert len(results) == 3
    assert results[0].is_valid
    assert not results[1].is_valid
    assert results[1].line_number == 2
    assert results[2].is_valid


def test_validate_jsonl_text_rejects_blank_lines():
    content = '{"id": "one"}\n\n{"id": "two"}\n'

    results = validate_jsonl_text(content)

    assert len(results) == 3
    assert results[1].code == "blank_jsonl_line"
    assert results[1].line_number == 2


def test_coding_review_checklist_contains_expected_items():
    assert "Syntax error" in CODING_REVIEW_CHECKLIST
    assert "Unsupported library/function claim" in CODING_REVIEW_CHECKLIST
    assert "Invalid JSON output" in CODING_REVIEW_CHECKLIST
