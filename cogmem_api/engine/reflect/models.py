"""Pydantic models for CogMem reflect lazy synthesis."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ReflectNetwork = Literal["world", "experience", "opinion", "habit", "intention", "action_effect"]


class ReflectEvidence(BaseModel):
    """A single retrieved memory unit used for lazy synthesis."""

    id: str = Field(description="Memory unit identifier")
    fact_type: ReflectNetwork = Field(description="CogMem memory network type")
    text: str = Field(description="Primary narrative text")
    raw_snippet: str | None = Field(default=None, description="Lossless raw snippet from source dialogue")
    source: str = Field(default="unknown", description="Retrieval source channel")
    score: float = Field(default=0.0, description="Ranking score for evidence ordering")
    event_date: datetime | None = Field(default=None, description="Optional timestamp for temporal ordering")

    @field_validator("text")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be empty")
        return value

    @field_validator("raw_snippet")
    @classmethod
    def _normalize_raw_snippet(cls, value: str | None) -> str | None:
        if value is None:
            return None
        snippet = value.strip()
        return snippet or None


class ReflectSynthesisResult(BaseModel):
    """Output for a lazy reflect synthesis call."""

    answer: str = Field(description="Final markdown answer")
    used_memory_ids: list[str] = Field(default_factory=list, description="Memory unit IDs used in the answer")
    networks_covered: list[ReflectNetwork] = Field(
        default_factory=list,
        description="Distinct CogMem networks represented in selected evidence",
    )
    evidence_count: int = Field(default=0, description="Number of evidence items used for synthesis")
    prompt: str | None = Field(default=None, description="Final prompt passed to the generator when debugging")
