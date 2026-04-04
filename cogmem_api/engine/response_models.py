"""Core response models used by the CogMem engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class DispositionTraits:
    """Personality/disposition traits used during think/reflect generation."""

    skepticism: int = 3
    literalism: int = 3
    empathy: int = 3

    def __post_init__(self) -> None:
        for field_name in ("skepticism", "literalism", "empathy"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer in range [1, 5]")
            if value < 1 or value > 5:
                raise ValueError(f"{field_name} must be in range [1, 5]")


@dataclass(slots=True)
class MemoryFact:
    """Minimal memory fact model used to format think prompt evidence."""

    id: str
    text: str
    fact_type: str
    context: str | None = None
    occurred_start: datetime | str | None = None


@dataclass(slots=True)
class TokenUsage:
    """Token usage metrics for LLM-backed operations."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )
