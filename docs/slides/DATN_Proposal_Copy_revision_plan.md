# DATN Defense Slide Revision Plan

Source deck: `docs/slides/DATN_Proposal - Copy.pptx`

Target format: 10-15 minute thesis defense presentation, focused on what was built, why it matters, and how each contribution is supported by evidence.

## 1. Current Deck Audit

The current deck has 16 slides and is still closer to a proposal deck than a final defense deck.

Strengths:
- It already introduces CogMem as a cognitive-science-based long-term conversational memory architecture.
- It has useful visual slides for the 3-pipeline architecture, six memory networks, SUM spreading activation, cycle guards, and weighted query routing.
- It already contains the core vocabulary needed for the thesis: retain, recall, generation, typed nodes, raw snippets, SUM activation, and adaptive routing.

Problems to fix:
- The evaluation slide is outdated: it reports only 12 LongMemEval conversations and `10/12 = 83%`, while the thesis now reports LongMemEval v16, LoCoMo, and the graph-only SUM-vs-MAX control.
- The story starts directly from architecture, but a defense deck needs a clearer problem-to-solution arc.
- Several method slides are too dense for a 10-15 minute talk. They should be converted into visual explanation slides with one key message each.
- Contributions are described as design choices, but not yet proved through results, ablations, or honest limitations.
- Internal experiment identifiers must not appear in the final audience-facing slides unless explicitly explained. Prefer reader-facing labels such as `Best multi-channel`, `Graph-only SUM`, `Graph-only MAX`, and `Final LoCoMo evidence-guard configuration`.

## 2. Recommended Narrative

Core message:

> CogMem turns long conversations into a typed memory graph, retrieves evidence through complementary channels, and uses cognitive-inspired graph activation to make long-term conversational memory more reliable. The final system is validated with manual evaluation on LongMemEval and LoCoMo, while the SUM activation contribution is isolated with a graph-only control.

Talk arc:
1. Why LLM long-term memory is hard.
2. Why plain vector memory is not enough.
3. CogMem overview: retain -> memory graph -> recall -> grounded answer.
4. Key method: six typed memory networks and raw snippets.
5. Key method: multi-channel recall and adaptive routing.
6. Key method: SUM graph activation and cycle guards.
7. Walk through one example query.
8. Show evaluation protocol and manual scoring.
9. Show LongMemEval results.
10. Show SUM vs MAX control.
11. Show LoCoMo results.
12. Show qualitative necessity evidence for intention and action-effect.
13. State contribution proof and limitations honestly.
14. Close with what was achieved and what should be tested next in realistic scenarios.

## 3. Proposed Final Deck

Use 15 main slides plus a Q&A slide. This gives about 45-60 seconds per slide, leaving time for transitions and Q&A.

### Slide 1. Title

Use current slide 1 as base.

Title:
- `CogMem: Cognitive-Grounded Long-Term Memory for Conversational Agents`

Subtitle:
- `A typed memory graph with multi-channel recall and SUM spreading activation`

Visual:
- Keep cover visual if it looks polished.
- Add one small architecture icon strip: `Conversation -> Memory Graph -> Evidence -> Answer`.

Talk goal:
- Establish that this is no longer only a proposal; it is an implemented and evaluated system.

### Slide 2. Problem: Long Conversations Break Short Context

Rewrite current slide 2.

Main question:
- `How can an assistant remember useful facts across many sessions without confusing old, new, causal, temporal, and preference information?`

Pain points:
- Long conversations exceed context windows.
- Vector search alone retrieves similar text but may miss relations, dates, and multi-hop evidence.
- Raw logs are too noisy; compressed facts can lose details.
- Automatic judges can be unreliable, so final evaluation needs manual checking.

Visual:
- A timeline of many chat sessions, with three highlighted facts far apart.
- Add a warning label: `Same user, many sessions, conflicting facts`.

Talk goal:
- Make the audience feel the problem before seeing the architecture.

### Slide 3. Solution Overview: CogMem in One Picture

Reuse thesis image:
- `reports/final_reports/src/Images/cogmem_pipeline_overview.png`

Overlay labels:
- `Retain`
- `Typed Memory Graph`
- `Recall`
- `Grounded Answer`
- `Feedback / Future Retain`

Key bullets:
- Retain: extract typed facts from conversation.
- Store: build a heterogeneous memory graph.
- Recall: combine semantic, BM25, graph, and temporal evidence.
- Generate: answer only from recalled evidence and snippets.

Talk goal:
- Give the end-to-end map before diving into details.

### Slide 4. What Is Stored: Two-Layer Memory

Merge current slides 9 and 11.

Message:
- CogMem stores both compressed meaning and source-grounded details.

Layout:
- Left: `Narrative fact` with embedding, type, date, entities.
- Right: `Raw snippet` with original source text and metadata.
- Bottom: one example transformation.

Example:
- Conversation: `I stayed in Seattle before flying to Chicago.`
- Fact: `User was in Seattle before traveling to Chicago.`
- Raw snippet: original sentence, kept for generation.

Visual:
- Small two-layer card diagram.

Talk goal:
- Explain why the system is not just vector DB over raw chat and not just lossy summaries.

### Slide 5. Six Memory Networks

Reuse thesis image:
- `reports/final_reports/src/Images/cogmem_memory_graph.png`

Keep it visual; do not use a dense full table.

Show six cards:
- `World`: stable factual knowledge.
- `Experience`: dated events.
- `Opinion`: preferences and beliefs.
- `Habit`: repeated routines.
- `Intention`: future plans and lifecycle.
- `Action-effect`: precondition -> action -> outcome.

Important honesty note:
- `Habit` is a plausible representation, but current benchmarks did not strongly prove its uplift.
- `Intention` and `action-effect` are more naturally tested by realistic or targeted scenarios.

Talk goal:
- State the first contribution: typed memory nodes allow different kinds of memory to keep their semantics.

### Slide 6. Recall: Four Channels, One Evidence List

Rewrite current slide 7 and current slide 14 into one slide.

Channels:
- Semantic similarity.
- BM25 lexical match.
- Graph traversal.
- Temporal retrieval.

Routing:
- Query type changes the retrieval weights: semantic, temporal, causal, prospective, preference, multi-hop.

Visual:
- Four colored streams feeding one ranked evidence list.
- Add examples:
  - `When...?` -> temporal channel matters.
  - `Why...?` -> graph/causal evidence matters.
  - `What did I prefer...?` -> preference and semantic evidence matter.

Talk goal:
- Show why the final system is multi-channel, not graph-only.

### Slide 7. Graph Recall: SUM Instead of MAX

Use current slide 12 as base but simplify heavily.

Message:
- MAX keeps the strongest single path.
- SUM accumulates multiple weak paths that point to the same relevant memory.

Visual:
- Left: MAX diagram, only one path highlighted.
- Right: SUM diagram, three weak paths converging into the answer node.

Key equation:
- MAX: `A(v) = max(neighbor signal)`
- SUM: `A(v) += total incoming signal`

Cycle guards:
- Refractory period.
- Firing quota.
- Saturation threshold.

Talk goal:
- Explain the SUM contribution intuitively enough for non-implementation reviewers.

### Slide 8. Running Example: From Query to Answer

New slide.

Use one concrete example, not a benchmark case ID.

Example query:
- `Which city was the user in before traveling to Chicago?`

Flow:
1. Query analyzer detects a before/travel temporal relation.
2. Recall brings dated memories around Seattle and Chicago.
3. Temporal hint / evidence guard prevents guessing.
4. Generation answers: `Seattle`.

Visual:
- Timeline: `Seattle` before `Chicago`.
- Memory cards connected to evidence list.

Talk goal:
- Turn the abstract pipeline into something the committee can follow.

### Slide 9. Evaluation Protocol: Manual, Evidence-Based

Reuse thesis image:
- `reports/final_reports/src/Images/manual_evaluation_flow.png`

Message:
- The final numbers are manually checked because the automatic judge is not trusted as ground truth.

Metrics:
- LongMemEval: manual PASS.
- LoCoMo: manual PASS, where PASS means the answer is fully correct or core-correct and usable.
- Do not show `PARTIAL` as a separate category in the final slide; mention orally only if asked.

Visual:
- Pipeline: benchmark question -> CogMem answer -> human verdict -> category totals.

Talk goal:
- Make evaluation credible before showing scores.

### Slide 10. LongMemEval v16 Results

Replace current slide 15.

Numbers:
- Best multi-channel: `29/35 PASS = 82.9%`.
- Full six-type multi-channel baseline: `26/35 PASS = 74.3%`.
- Graph-only configurations are lower, so graph recall is useful but should not replace multi-channel recall.

Visual:
- Bar chart with three groups:
  - `Best multi-channel`: 82.9%.
  - `Full six-type baseline`: 74.3%.
  - `Graph-only`: lower band, no need to overcrowd with every variant.

Interpretation:
- Multi-channel recall is the strongest general strategy.
- Typed memory is useful, but not every type contributes equally on every benchmark.

Talk goal:
- Show the first empirical proof: the system works end-to-end on a verified LongMemEval subset.

### Slide 11. Contribution Control: SUM Beats MAX in Graph-Only Recall

New or replace current slide 13 if time is tight.

Numbers:
- Graph-only SUM mean session recall@5: `0.8052`.
- Graph-only MAX mean session recall@5: `0.7624`.
- Absolute lift: `+0.0429`.
- Recall@10: both `0.8481`.
- SUM better in `2/35`, MAX better in `0/35`.

Visual:
- Small table plus a mini rank illustration.
- Show `Relevant evidence at rank 1-5` vs `Relevant evidence at rank 6-7`.

Honest claim:
- SUM does not create new evidence; it prioritizes relevant evidence earlier in the prompt budget.
- This proves the activation rule inside the graph-only channel, not that graph-only should replace multi-channel recall.

Talk goal:
- Isolate and prove one technical contribution cleanly.

### Slide 12. LoCoMo Results: Harder Long-Dialogue Benchmark

Replace current slide 15 eval content.

Numbers:
- Final manual PASS: `119/161 = 73.9%`.
- Previous baseline: `97/161 = 60.2%`.
- Improvement: `+22` PASS cases.
- Target: at least 70%, achieved.

Category breakdown:
- Causal: `10/11 = 90.9%`.
- Multi-hop: `11/12 = 91.7%`.
- Preference: `15/17 = 88.2%`.
- Single-hop: `78/109 = 71.6%`.
- Temporal: `5/12 = 41.7%`.

Visual:
- One big headline number: `73.9%`.
- Horizontal category bar chart.
- Highlight temporal as the remaining weak slice.

Talk goal:
- Show that the system crosses the main quality threshold on the harder benchmark while remaining honest about temporal limitations.

### Slide 13. Qualitative Proof: Intention Stores Unfinished Plans

New slide based on `data/bench/visualization/neg_intention_14_explanation.md`.

Audience-facing example:
- Question: `What sustainability habit did the user intend to start but has not?`
- Gold answer: `Composting.`

Paired-bank evidence:
- Full memory bank: `37` facts, including `4` intention nodes, answers `Composting`.
- Intention-ablated bank: `26` facts, `0` intention nodes, answers the decoy `rainwater collection`.

Visual:
- Recreate the paired visualization as a PowerPoint-native mini graph:
  - Left: full bank with red intention nodes around `plans composting`.
  - Right: ablated bank with no intention nodes and a decoy cluster around `rain barrel`.
  - Use text labels on every node so meaning does not depend only on color.

Honest interpretation:
- This does not prove intention is universally necessary.
- It proves content-level necessity in sparse plan-not-done cases where no experience fact carries the same content.

Talk goal:
- Make the typed intention contribution concrete and rigorous without relying on internal experiment labels.

### Slide 14. Qualitative Proof: Action-Effect Stores Tool Outcomes

New slide based on `data/bench/visualization/agentic_ae_01_http_429_explanation.md`.

Audience-facing example:
- Question: `When Stripe returns HTTP 429 with Retry-After, what does the agent do and what happens?`
- Gold answer: retry with exponential backoff while respecting `Retry-After`; subsequent calls return `200`.

Paired-bank evidence:
- Full memory bank: `13` facts, including `7` action-effect nodes, answers the action and outcome.
- Action-effect-ablated bank: `12` facts, `0` action-effect nodes, can only say generic backoff information is available.
- Across the mocked agentic workload, `5/12` traces cleanly discriminate.

Visual:
- Recreate the paired visualization as a PowerPoint-native mini graph:
  - Left: `HTTP 429 + Retry-After -> sleep/retry -> 200`.
  - Right: generic `429 has header` plus `backoff added`, but no exact causal triple.

Honest interpretation:
- This is conditional evidence, not universal proof; short mocked traces sometimes let the extractor re-type causal rules as world facts.

Talk goal:
- Show why action-effect nodes matter for realistic tool-use memory, while keeping the methodological claim honest.

### Slide 15. What Was Proved, What Remains

New final content slide before Thank You.

Use a proof matrix:

| Claim | Evidence | Status |
| --- | --- | --- |
| Multi-channel memory recall helps long conversations | LongMemEval best multi-channel 29/35; LoCoMo 119/161 | Strong |
| SUM graph activation improves graph-only top-k evidence priority | SUM 0.8052 vs MAX 0.7624 recall@5 | Strong but scoped |
| Raw snippets and evidence guard improve answer grounding | LoCoMo +22 PASS over previous baseline | Strong practical evidence |
| Typed intention/action-effect nodes are useful for realistic agent memory | Paired qualitative ablations: composting sparse-plan and HTTP 429 tool trace | Conditional |
| Habit nodes need routine-focused workloads | Current benchmarks do not show strong uplift | Limitation |

Future work:
- Realistic assistant scenarios, not only benchmark tuning.
- Prospective memory cases for plans, cancellations, and unfulfilled intentions.
- Dense real agentic action-effect traces for tool-use learning.
- Multi-week diary workload for habits.

Talk goal:
- End with balanced confidence: real system, real gains, clear scope, clear next step.

### Slide 16. Thank You / Q&A

Use current slide 16.

Add small footer:
- `Code, experiments, and manual verdict artifacts are preserved in the repository.`

## 4. Current Slide Mapping

| Current slide | Action |
| --- | --- |
| 1 Title | Keep, rewrite title/subtitle. |
| 2 Problem | Rewrite with sharper long-term memory problem. |
| 3 Data LongMemEval-S | Replace with evaluation protocol or move dataset details into results slides. |
| 4 CogMem 3 pipeline | Keep visual if readable; otherwise replace with thesis pipeline overview image. |
| 5 CogMem 3 pipeline | Merge/drop to avoid duplicate pipeline slide. |
| 6 Retain details | Compress into two-layer memory slide. |
| 7 Recall/generation details | Compress into four-channel recall slide. |
| 8 Six network visual | Keep, add labels if the image is unlabeled. |
| 9 Six network table | Replace dense table with six cards. |
| 10 Action-effect table | Move into proof/future-work discussion or backup slide. |
| 11 Raw snippets | Merge into two-layer memory slide. |
| 12 SUM spreading activation | Keep, simplify into SUM-vs-MAX intuition. |
| 13 Cycle guards | Merge into SUM slide; keep only three guard names. |
| 14 Weighted routing | Merge into four-channel recall slide. |
| 15 Eval | Replace completely with final LongMemEval, SUM-vs-MAX, and LoCoMo result slides. |
| 16 Thank you | Keep. |

## 5. Visual Asset Plan

Reuse:
- `reports/final_reports/src/Images/cogmem_pipeline_overview.png` for solution overview.
- `reports/final_reports/src/Images/cogmem_memory_graph.png` for six memory networks.
- `reports/final_reports/src/Images/manual_evaluation_flow.png` for evaluation protocol.
- `reports/final_reports/src/Images/agentic_action_effect_trace.png` as optional backup or future-work slide.
- `reports/final_reports/src/Images/habit_diary_workload.png` as optional backup or future-work slide.
- `data/bench/visualization/neg_intention_14_explanation.md` as the source for the intention paired-bank mini graph.
- `data/bench/visualization/agentic_ae_01_http_429_explanation.md` as the source for the action-effect paired-bank mini graph.

New visuals to create in PowerPoint:
- Long-context problem timeline with scattered evidence.
- Two-layer memory card: narrative fact + raw snippet.
- Four-channel recall funnel.
- SUM vs MAX convergence diagram.
- Result dashboard with LongMemEval and LoCoMo bars.
- Two paired-bank qualitative proof graphs for intention and action-effect.
- Contribution proof matrix.

Design rule:
- Every visual should include text labels. Do not rely only on color, because reviewers need to understand the diagram from a distance.

## 6. Suggested 10-15 Minute Timing

| Segment | Slides | Time |
| --- | --- | --- |
| Opening and problem | 1-2 | 1.5-2 min |
| CogMem overview | 3 | 1 min |
| Memory representation | 4-5 | 2 min |
| Recall and graph activation | 6-7 | 2.5-3 min |
| Example walkthrough | 8 | 1-1.5 min |
| Evaluation setup | 9 | 1 min |
| Results | 10-12 | 3-4 min |
| Qualitative type proof | 13-14 | 1.5-2 min |
| Limitations and close | 15-16 | 1.5-2 min |

If limited to exactly 10 minutes:
- Merge Slide 4 and Slide 5.
- Merge Slide 10 and Slide 11 into one `LongMemEval + SUM Control` slide.
- Keep LoCoMo as its own slide because it is the strongest final benchmark result.
- Keep only one of the two qualitative proof slides if the defense slot is cut below 10 minutes.

## 7. Speaker Notes Skeleton

Opening:
- `The goal of this thesis is to make long-term conversational memory more structured and more reliable than raw logs or vector search alone.`

Problem:
- `A user may mention plans, preferences, locations, actions, and outcomes across many sessions. If we flatten everything into embeddings, we lose important distinctions.`

Solution:
- `CogMem keeps memory as a typed graph. The graph stores what happened, what the user believes, what they intend to do, what they often do, and what action caused what outcome.`

Method:
- `Retain extracts typed facts and raw snippets. Recall combines semantic, lexical, graph, and temporal channels. The graph channel uses SUM activation so multiple weak signals can reinforce each other.`

Example:
- `For a before-travel question, the system should not guess from a similar city mention. It needs dated evidence and the correct before/after relation.`

Results:
- `On LongMemEval, the best multi-channel setup reaches 82.9% manual PASS. On LoCoMo, the final system reaches 73.9%, crossing the 70% target.`

Contribution proof:
- `The SUM-vs-MAX control isolates one method choice: with the same banks and graph-only recall, SUM improves recall@5 from 0.7624 to 0.8052.`
- `For intention and action-effect, the proof is qualitative and paired-bank: when the target type is removed at retain time, the exact gold content disappears and the system either picks a decoy or admits missing detail.`

Limitation:
- `Temporal questions remain the weakest slice on LoCoMo, and Habit needs a better routine-focused workload to prove its value.`

Close:
- `The main result is not just a higher benchmark number. It is a working memory architecture with typed representations, grounded evidence, and measurable gains under manual evaluation.`

## 8. Backup Slides To Prepare

Prepare 3-5 backup slides in case reviewers ask deeper questions:
- Exact fact type table with metadata fields.
- Edge type table with examples.
- SUM cycle guard details.
- Full LoCoMo category table.
- Habit limitation and proposed diary workload.
