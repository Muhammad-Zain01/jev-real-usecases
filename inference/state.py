"""Helpers for building the state sent to Jev."""

from collections.abc import Mapping
from typing import Any


class StateBuilder:
    """Build the JSON-like state that Jev evaluates."""

    def __init__(self, initial: Mapping[str, Any] | None = None) -> None:
        self._state: dict[str, Any] = dict(initial or {})

    def add(self, name: str, value: Any) -> "StateBuilder":
        """Add one piece of context to the state."""
        self._state[name] = value
        return self

    def build(self) -> dict[str, Any]:
        """Return the state in the format expected by the SDK."""
        return dict(self._state)
