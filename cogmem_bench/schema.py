"""Scenario-spec schema — the pre-registration contract for benchmark cases.

A ScenarioSpec is authored (by a strong LLM / human) *before* any conversation
is generated. The gold answer and the discriminating fact live here, never in the
generator. The generator only renders the spec into natural dialogue.

Three artifacts flow through the pipeline:
  ScenarioSpec          -> authored up front (the pre-registration record)
  GeneratedConversation -> produced by the generation step from a spec
  GateResult            -> verdict of the embedding + discrimination gates
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from cogmem_api.engine.retain.types import ALLOWED_INTENTION_STATUSES

# The three node types this benchmark exists to test.
TARGET_TYPES = ("habit", "intention", "action_effect")
TargetType = Literal["habit", "intention", "action_effect"]
TrapType = Literal["type-confusion", "stale-intention", "contradiction", "volume"]

# Workload kinds. "chat" = human-AI casual dialogue (S33). "agentic" = single-agent
# tool-use trace (S34). Default stays "chat" so existing 20 specs round-trip unchanged.
Workload = Literal["chat", "agentic"]


class GoldFragment(BaseModel):
    """One distributed piece of the gold fact, embedded in a single session.

    No fragment may state the whole gold fact or the answer — the benchmark answer must
    require *combining* fragments across sessions (lifecycle: plan + resolution; causal:
    precondition + action/outcome; habit: several individual occurrences).
    """

    session_index: int = Field(..., ge=0, description="Session that carries this piece.")
    reveal: str = Field(
        ...,
        description="The partial info this session embeds. Must NOT be the full fact/answer.",
    )


class GoldFact(BaseModel):
    """The discriminating fact whose metadata the gold answer depends on.

    `text` + `metadata` are the canonical truth used by the judge and the embedding gate.
    `fragments` are how that truth is *distributed* across sessions for generation — no
    single session is self-sufficient, so a world/experience/opinion-only system that can
    only recall isolated sentences cannot answer.
    """

    text: str = Field(..., description="Canonical fact (judge/embedding-gate reference; never shown verbatim to the generator).")
    fact_type: TargetType = Field(..., description="Must match the spec's target_type.")
    fragments: list[GoldFragment] = Field(
        ...,
        min_length=2,
        description="Distributed pieces across >=2 sessions; the answer requires combining them.",
    )
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description=(
            "Type-specific structured fields the answer hinges on. "
            "intention -> {'intention_status'}; "
            "action_effect -> {'precondition','action','outcome'(, 'confidence')}; "
            "habit -> {'frequency'} (the repetition/aggregation descriptor)."
        ),
    )

    @property
    def fragment_indices(self) -> list[int]:
        return sorted({f.session_index for f in self.fragments})

    @model_validator(mode="after")
    def _require_type_metadata(self) -> "GoldFact":
        md = self.metadata
        if self.fact_type == "intention":
            status = str(md.get("intention_status", "")).strip().lower()
            if status not in ALLOWED_INTENTION_STATUSES:
                raise ValueError(
                    f"intention gold_fact needs metadata.intention_status in "
                    f"{sorted(ALLOWED_INTENTION_STATUSES)}, got {md.get('intention_status')!r}"
                )
        elif self.fact_type == "action_effect":
            missing = [k for k in ("precondition", "action", "outcome") if not str(md.get(k, "")).strip()]
            if missing:
                raise ValueError(f"action_effect gold_fact missing metadata fields: {missing}")
        elif self.fact_type == "habit":
            if not str(md.get("frequency", "")).strip():
                raise ValueError("habit gold_fact needs metadata.frequency (repetition descriptor)")
        return self


class Trap(BaseModel):
    """A distractor designed to break a world/experience/opinion-only system."""

    trap_type: TrapType
    description: str = Field(..., description="What the trap is and why it misleads w/e/o-only.")
    session_index: int | None = Field(None, ge=0, description="Session that carries the trap, if fixed.")


class SessionPlan(BaseModel):
    """How the 7-10 sessions are laid out: which carry gold vs distractor."""

    total_sessions: int = Field(..., ge=7, le=10)
    gold_session_indices: list[int] = Field(..., min_length=2, max_length=5)
    session_topics: list[str] | None = Field(
        None, description="Optional per-session topic guidance; if set, length must equal total_sessions."
    )
    dates: list[str] | None = Field(
        None, description="Optional ISO date per session (oldest->newest); length must equal total_sessions."
    )

    @model_validator(mode="after")
    def _check_lengths(self) -> "SessionPlan":
        for idx in self.gold_session_indices:
            if not (0 <= idx < self.total_sessions):
                raise ValueError(f"gold_session_index {idx} out of range for total_sessions={self.total_sessions}")
        if self.session_topics is not None and len(self.session_topics) != self.total_sessions:
            raise ValueError("session_topics length must equal total_sessions")
        if self.dates is not None and len(self.dates) != self.total_sessions:
            raise ValueError("dates length must equal total_sessions")
        return self


class ScenarioSpec(BaseModel):
    """The pre-registration contract for one benchmark case."""

    scenario_id: str
    target_type: TargetType
    topic: str = Field(..., description="Consistent conversation theme.")
    gold_fact: GoldFact
    question: str
    gold_answer: str = Field(..., description="Machine-checkable: number / status / name.")
    traps: list[Trap] = Field(default_factory=list)
    session_plan: SessionPlan
    shared_context: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Canonical facts every session must agree with (names, dates, specifics). "
            "Injected verbatim into every generation call to keep multi-call sessions "
            "consistent. Generation-only — not emitted into the fixture."
        ),
    )
    question_date: str | None = Field(None, description="ISO date representing 'now' when the question is asked.")
    rationale: str | None = Field(
        None, description="Why this question needs the target type's metadata (pre-registration justification)."
    )
    workload: Workload = Field(
        "chat",
        description=(
            "Conversation kind. 'chat' (default): human-AI dialogue, the S33 workload. "
            "'agentic': single-agent tool-use trace where each session is one task episode "
            "with inline [tool: ...] / [output: ...] tags. The generator branches on this; "
            "everything downstream (fixture/retain/gates) is workload-agnostic."
        ),
    )
    tools_used: list[str] | None = Field(
        None,
        description=(
            "Agentic only — inventory of tool names the agent may call (e.g. ['bash','grep','http']). "
            "Constrains the generator from inventing arbitrary tools."
        ),
    )
    episodes: list[str] | None = Field(
        None,
        description=(
            "Agentic only — one-line task description per session (len must equal "
            "session_plan.total_sessions). Each session = one task episode. The gold causal "
            "rule's precondition lives in one episode; action+outcome in another (anti-leak: "
            "no single episode renders the full precondition->action->outcome triple)."
        ),
    )
    gold_action_tokens: list[str] | None = Field(
        None,
        description=(
            "Agentic only — distinctive substrings (env vars, CLI flags, command names) that "
            "must appear ONLY inside the gold action+outcome episode. The leak validator scans "
            "every non-gold episode and warns if any of these strings appears (T1 lesson: "
            "Minimax mượn `-p no:cacheprovider` flag vào a filler pytest call → defeated the "
            "ablation). Case-sensitive substring match. Recommended: 2-5 tokens per spec, each "
            "specific enough to be unlikely as a generic phrase."
        ),
    )

    @model_validator(mode="after")
    def _agentic_fields_consistent(self) -> "ScenarioSpec":
        if self.workload == "agentic":
            if not self.tools_used:
                raise ValueError("agentic workload requires non-empty tools_used")
            if self.episodes is None or len(self.episodes) != self.session_plan.total_sessions:
                raise ValueError(
                    "agentic workload requires episodes with len == session_plan.total_sessions"
                )
            if self.target_type != "action_effect":
                # S34 scope: action_effect on agentic. Other types in agentic workload are
                # out of scope (intention re-test, habit) per the sprint plan.
                raise ValueError(
                    f"agentic workload only supports target_type=action_effect (got {self.target_type!r})"
                )
        else:
            # Chat workload must not carry agentic-only fields (keeps fixtures clean).
            if self.tools_used or self.episodes or self.gold_action_tokens:
                raise ValueError(
                    "tools_used/episodes/gold_action_tokens are agentic-only; set "
                    "workload='agentic' to use them"
                )
        return self

    @model_validator(mode="after")
    def _gold_fact_matches_target(self) -> "ScenarioSpec":
        if self.gold_fact.fact_type != self.target_type:
            raise ValueError(
                f"gold_fact.fact_type ({self.gold_fact.fact_type}) must equal target_type ({self.target_type})"
            )
        frag_idxs = self.gold_fact.fragment_indices
        for idx in frag_idxs:
            if not (0 <= idx < self.session_plan.total_sessions):
                raise ValueError(f"gold fragment session_index {idx} out of range for total_sessions")
        if frag_idxs != sorted(self.session_plan.gold_session_indices):
            raise ValueError(
                f"gold fragment indices {frag_idxs} must equal session_plan.gold_session_indices "
                f"{sorted(self.session_plan.gold_session_indices)}"
            )
        return self


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class GeneratedSession(BaseModel):
    session_id: str
    date: str | None = None
    messages: list[Message]


class GeneratedConversation(BaseModel):
    """Output of the generation step — a frozen, natural multi-session dialogue."""

    scenario_id: str
    target_type: TargetType
    sessions: list[GeneratedSession]
    question: str
    gold_answer: str
    question_date: str | None = None
    gold_session_ids: list[str] = Field(default_factory=list)


class EmbeddingGateResult(BaseModel):
    passed: bool
    gold_fact_found: bool
    expected_fact_type: str
    found_fact_type: str | None = None
    detail: str = ""


class DiscriminationGateResult(BaseModel):
    passed: bool
    full_correct: bool = Field(..., description="E7 (full) judge.correct")
    weo_correct: bool = Field(..., description="E11 (world/experience/opinion only) judge.correct")
    detail: str = ""


class GateResult(BaseModel):
    scenario_id: str
    embedding_gate: EmbeddingGateResult
    discrimination_gate: DiscriminationGateResult | None = None
    accepted: bool = False
