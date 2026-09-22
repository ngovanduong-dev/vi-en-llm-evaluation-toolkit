"""Shared JSON transport policy for toolkit validation entry points."""

from __future__ import annotations

import json
from typing import Any


class JsonPolicyError(ValueError):
    """A JSON policy violation without a reliable source position."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _reject_constant(value: str) -> Any:
    raise JsonPolicyError("non_finite_number", "Non-finite JSON literals are not allowed")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JsonPolicyError(
                "duplicate_json_key", "Duplicate JSON object names are not allowed"
            )
        result[key] = value
    return result


def decode_json(value: str) -> Any:
    """Decode JSON, rejecting non-finite literals and repeated names at every depth.

    This checks transport only, not record shape or schema. Policy errors omit
    input values and positions; ordinary syntax errors retain JSONDecodeError.
    """
    return json.loads(value, parse_constant=_reject_constant, object_pairs_hook=_unique_object)
