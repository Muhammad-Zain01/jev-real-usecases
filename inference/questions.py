"""Helpers for building Jev questions."""

from collections.abc import Mapping, Sequence
from typing import Any

from typesafe_sdk import Choice, Noul, Score


class QuestionBuilder:
    """Build named Choice, Noul, and Score questions for one Jev call."""

    def __init__(self) -> None:
        self._questions: dict[str, Any] = {}

    def choice(
        self,
        name: str,
        instructions: str,
        criteria: Mapping[str, Any],
    ) -> "QuestionBuilder":
        """Add a question that selects one option."""
        self._questions[name] = Choice(
            instructions=instructions,
            criteria=dict(criteria),
        )
        return self

    def noul(
        self,
        name: str,
        instructions: str,
        criteria: Mapping[str, Any] | None = None,
    ) -> "QuestionBuilder":
        """Add a yes/no probability question."""
        self._questions[name] = Noul(
            instructions=instructions,
            criteria=dict(criteria) if criteria is not None else None,
        )
        return self

    def score(
        self,
        name: str,
        instructions: str,
        criteria: Sequence[Any],
    ) -> "QuestionBuilder":
        """Add an ordered scoring question."""
        self._questions[name] = Score(
            instructions=instructions,
            criteria=list(criteria),
        )
        return self

    def build(self) -> dict[str, Any]:
        """Return all questions in the format expected by the SDK."""
        return dict(self._questions)
