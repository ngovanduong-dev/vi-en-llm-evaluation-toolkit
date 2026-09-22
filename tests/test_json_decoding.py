import json

import pytest

from vi_en_eval._json import JsonPolicyError, decode_json
from vi_en_eval.code_checks import validate_json_text, validate_jsonl_text


@pytest.mark.parametrize(
    "text",
    [
        '{"score": 1}',
        '{"outer": [{"tiếng Việt": "đúng\u2028dòng"}]}',
        '{"id": 1, "Id": 2, "id ": 3}',
        "[true, false, null, 1.5]",
        "5",
        "null",
        '"hello"',
    ],
)
def test_valid_json_syntax_does_not_require_record_shape(text):
    assert decode_json(text) == json.loads(text)
    assert validate_json_text(text).is_valid


@pytest.mark.parametrize(
    ("text", "code"),
    [(literal, "non_finite_number") for literal in ("NaN", "Infinity", "-Infinity")]
    + [
        (' {"score": NaN}', "non_finite_number"),
        ('{"id": 1, "id": 2}', "duplicate_json_key"),
        ('{"outer": [{"score": 1, "score": 2}]}', "duplicate_json_key"),
        ('{"id": 1, "\\u0069d": 2}', "duplicate_json_key"),
    ],
)
def test_shared_transport_policy(text, code):
    with pytest.raises(JsonPolicyError) as exc_info:
        decode_json(text)
    assert exc_info.value.code == code
    result = validate_json_text(text)
    assert not result.is_valid
    assert result.code == code
    assert result.line_number is None
    assert result.column is None
    assert text not in result.message


def test_syntax_error_retains_position():
    result = validate_json_text(' {"outer": 1\n  } trailing')
    assert result.code == "invalid_json"
    assert result.line_number == 2
    assert result.column is not None
    assert "Extra data" in result.message


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_jsonl_uses_physical_lines_and_continues_after_errors(newline):
    rows = [
        '{"text":"Tiếng Việt\u2028next\u0085part"}',
        '{"x":1,"x":2}',
        " ",
        '{"x":Infinity}',
        '{"ok":true}',
    ]
    results = validate_jsonl_text(newline.join(rows) + newline)
    assert [result.line_number for result in results] == [1, 2, 3, 4, 5]
    assert [result.code for result in results] == [
        "valid_jsonl_line",
        "duplicate_json_key",
        "blank_jsonl_line",
        "non_finite_number",
        "valid_jsonl_line",
    ]
    assert results[1].column is None
    assert results[3].column is None
