# Sprint S26: Recall Quality Fixes — Query Routing + Channel Trace + Generation Prompt

**Trạng thái:** ✅ Done (tasks 786-788)

**Phụ thuộc:** S25 complete

---

## Mục tiêu sprint
1. Sửa bug misrouting khiến mọi câu hỏi có `question_date` bị classify là `temporal` → weight 2.2 bias RRF.
2. Thêm per-fact 4-channel trace vào recall response để debug được tại sao mỗi fact đứng ở rank hiện tại.
3. Fix generation prompt: tách MEMORIES (extracted facts) và REFERENCES (raw snippets) rõ ràng.

---

## Task 786 — Fix adaptive query routing: decouple `temporal_constraint` khỏi query type classification ✅

**Vấn đề:**

`classify_query_type` trong `cogmem_api/engine/query_analyzer.py`:
```python
if temporal_constraint is not None or _TEMPORAL_HINT_PATTERN.search(text):
    return "temporal"
```

`temporal_constraint is not None` fire bất cứ khi nào `question_date` được truyền vào — dù query không hỏi gì về thời gian. Kết quả: mọi câu hỏi LongMemEval đều route thành `temporal` với weight `{"temporal": 2.2}`. Ví dụ: "How many model kits have I worked on?" → B-29 (có "last weekend") chiếm rank 1-2 score 0.65, Spitfire/Tiger I bị dìm xuống 0.002.

**Fix:**
1. Bỏ `temporal_constraint is not None` khỏi điều kiện routing.
2. Mở rộng `_MULTI_HOP_PATTERN` để bắt aggregation/count queries:
   ```python
   # Thêm: r"\b(how many|how much|list all|what are all|count|total|all the|across all)\b"
   ```
3. `temporal_constraint` vẫn được truyền xuống temporal retrieval channel — chỉ không dùng để quyết định query type nữa.

**Files:** `cogmem_api/engine/query_analyzer.py` — `_MULTI_HOP_PATTERN` (line 42) và `classify_query_type()`.

**Verification:**
```python
assert classify_query_type("How many model kits have I worked on or bought?", temporal_constraint=<non-None>) == "multi_hop"
assert classify_query_type("List all the places I've visited", temporal_constraint=None) == "multi_hop"
assert classify_query_type("What did I do last week?", temporal_constraint=None) == "temporal"
assert classify_query_type("When did I buy the B-29?", temporal_constraint=None) == "temporal"
assert classify_query_type("I prefer Vallejo paints", temporal_constraint=None) == "preference"
```

**Artifact:** `tests/artifacts/test_task786_query_routing.py`

---

## Task 787 — Full per-fact 4-channel trace trong recall response

**Vấn đề:**

Trace hiện tại chỉ expose: `query_type`, `rrf_weights`, `fact_types`, `timings`, `cross_encoder_ok`. Không có thông tin về điểm số của từng fact theo từng channel.

**Trace shape mong muốn** (thêm vào `trace.per_result` khi `enable_trace=True`):
```json
{
  "per_result": [
    {
      "id": "...",
      "text": "User purchased a 1/72 scale B-29 bomber...",
      "channels": {
        "semantic": {"rank": 1, "contributed": true},
        "bm25":     {"rank": 4, "contributed": true},
        "graph":    {"rank": null, "contributed": false},
        "temporal": {"rank": 1, "contributed": true}
      },
      "rrf_score": 0.653,
      "cross_encoder_score": 0.631
    }
  ]
}
```

`rank` = thứ hạng trong channel đó (1-based), `null` nếu channel không retrieve được fact này.

**Files:**
- `cogmem_api/engine/search/fusion.py` — `weighted_reciprocal_rank_fusion()`: ghi lại `{doc_id: {source_name: rank}}` khi `enable_trace=True`
- `cogmem_api/engine/search/retrieval.py` — đính kèm per-doc channel map vào trace dict khi `enable_trace=True`
- `cogmem_api/engine/search/tracer.py` hoặc `trace.py` — thêm `per_result` field vào trace schema

**Constraint:** trace chỉ build khi `enable_trace=True`. Không thêm overhead vào normal recall path.

**Verification:**
```bash
curl -X POST http://localhost:8888/v1/default/banks/.../memories/recall \
  -d '{"query":"How many model kits","top_k":10,"trace":true}' \
  | python -c "import sys,json; t=json.load(sys.stdin)['trace']; print(json.dumps(t['per_result'][:3],indent=2))"
# Expected: 3 objects, mỗi object có channels.semantic.rank, channels.temporal.rank, rrf_score, cross_encoder_score
```

**Artifact:** `tests/artifacts/test_task787_recall_trace.py`

---

## Task 788 — Fix generation prompt: MEMORIES + REFERENCES format

**Vấn đề:**

`build_generation_prompt` trong `cogmem_api/prompts/eval/generate.py`:
```python
snippet = item.get("raw_snippet") or item.get("text", "")
```

Ưu tiên `raw_snippet` hơn `text`. Raw snippet là toàn bộ multi-turn conversation (hàng nghìn từ) → evidence block ~30,000–50,000 token. Generation LLM bị ngập trong nhiễu, đọc raw snippet dài nhất và respond theo nó thay vì trả lời câu hỏi.

Ví dụ cụ thể: E7 với query "How many model kits" — `generated_answer` nói về "Laptop Stand: Anker" vì raw_snippet của rank 8 là session về mua laptop ở Best Buy. Trong khi `text` của rank 8 lại là "User picks up model kits on impulse during hobby store trips" — đúng và ngắn gọn.

**Fix — MEMORIES + REFERENCES format:**

Tách thành 2 section rõ ràng trong prompt:

```
Answer the question using MEMORIES as primary evidence.
REFERENCES provide raw context — prioritize MEMORIES.

Question: {query}

MEMORIES (extracted facts — answer primarily from these):
[1] User purchased a 1/72 scale B-29 bomber model kit for photo-etching practice
[2] User purchased B-29 + '69 Camaro at a model show last weekend
...

REFERENCES (supporting raw context for each memory, if needed):
[1-ref] "I'm looking for some tips on photo-etching for my new 1/72 scale B-29..."
...

Instructions:
- Answer PRIMARILY from MEMORIES. Only consult REFERENCES if a memory is ambiguous.
- If MEMORIES contain partial information, enumerate what you found and state the list may be incomplete.
- Do NOT say "information not available" when partial evidence exists in MEMORIES.
- Cite by index, e.g. [1] or [2].
```

**Quy tắc implementation:**
- `text` → MEMORIES (luôn dùng, ngắn gọn, đã extracted)
- `raw_snippet` → REFERENCES (giữ nguyên, optional — chỉ thêm nếu snippet tồn tại)
- Item không có `raw_snippet` → không xuất hiện trong REFERENCES block
- MEMORIES đặt trước REFERENCES

**File:** `cogmem_api/prompts/eval/generate.py` — `build_generation_prompt()`

**Verification:**
```python
evidence = [
    {"text": "User bought B-29 kit", "raw_snippet": "I just got this B-29 kit..."},
    {"text": "User finished F-15 Eagle", "raw_snippet": None},
    {"text": "User started Tiger I diorama", "raw_snippet": "I started a diorama..."},
]
prompt = build_generation_prompt("How many kits?", evidence)
assert "MEMORIES" in prompt
assert "REFERENCES" in prompt
assert "[1] User bought B-29 kit" in prompt
assert "[1-ref]" in prompt
assert "[2-ref]" not in prompt   # F-15 không có snippet
assert "[3-ref]" in prompt       # Tiger I có snippet
assert prompt.index("MEMORIES") < prompt.index("REFERENCES")
```

**Artifact:** `tests/artifacts/test_task788_generation_prompt.py`
