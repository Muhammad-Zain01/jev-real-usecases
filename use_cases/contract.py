"""Shared input and output contract for every use case."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UseCaseInput:
    """Data supplied to a use case by the runner or future UI."""

    data: Mapping[str, Any]


@dataclass(frozen=True)
class FieldSpec:
    """Describes one input field that the UI should render."""

    name: str
    label: str
    kind: str
    required: bool = True
    description: str = ""


@dataclass(frozen=True)
class UseCaseSpec:
    """Metadata used by the UI to display and build a use-case form."""

    id: str
    title: str
    description: str
    fields: tuple[FieldSpec, ...]


@dataclass(frozen=True)
class UseCaseResult:
    """Common result returned by every use case."""

    name: str
    response: Any
    answers: Mapping[str, Any]
