"""Core response models used by the CogMem engine."""

from __future__ import annotations

from dataclasses import dataclass


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
