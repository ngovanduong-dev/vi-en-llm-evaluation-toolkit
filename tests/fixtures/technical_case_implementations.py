"""Reviewed implementations corresponding to the synthetic technical cases.

These functions manually encode the relevant candidate behavior. Tests never
extract or execute code from response text stored in JSONL.
"""

from collections.abc import Callable, Iterable
from typing import TypeVar


def iterable_mean_candidate_a(values: Iterable[float]) -> float:
    """Traverse the input twice, matching Candidate A's one-shot defect."""

    count = sum(1 for value in values if value > 0)
    if count == 0:
        return 0.0
    return sum(value for value in values if value > 0) / count


def iterable_mean_candidate_b(values: Iterable[float]) -> float:
    """Accumulate a positive total and count in one pass."""

    total = 0.0
    count = 0
    for value in values:
        if value > 0:
            total += value
            count += 1
    return total / count if count else 0.0


def call_isolation_candidate_a(words: Iterable[str]) -> dict[str, list[str]]:
    """Allocate independent state for every call."""

    groups: dict[str, list[str]] = {}
    for word in words:
        groups.setdefault(word[0], []).append(word)
    return groups


def make_call_isolation_candidate_b() -> Callable[[Iterable[str]], dict[str, list[str]]]:
    """Return a fresh function whose mutable default persists across its calls."""

    def group_by_initial(
        words: Iterable[str],
        groups: dict[str, list[str]] = {},  # noqa: B006 - intentional defect fixture
    ) -> dict[str, list[str]]:
        for word in words:
            groups.setdefault(word[0], []).append(word)
        return groups

    return group_by_initial


_ItemT = TypeVar("_ItemT")


def stable_dedup_candidate_a(items: Iterable[_ItemT]) -> list[_ItemT]:
    """Use ordered dictionary keys, which require hashable values."""

    return list(dict.fromkeys(items))


def stable_dedup_candidate_b(items: Iterable[_ItemT]) -> list[_ItemT]:
    """Use equality-based membership to support unhashable values."""

    result: list[_ItemT] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
