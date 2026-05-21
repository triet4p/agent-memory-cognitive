"""CogMem benchmark-construction package.

Builds purpose-built multi-session conversation benchmarks whose gold answers
depend on the structured metadata of the cognitive node types (habit, intention,
action_effect) — to test whether those types are *necessary*, on questions a
world/experience/opinion-only system provably cannot answer.

Methodology is frozen in docs/Ablation-Flow.md. This package is separate from
cogmem_api (the memory API) and reuses its config + LLMConfig only.
"""
