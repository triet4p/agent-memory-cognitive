# Sprint S27: Relationship Completeness — Entity Blocklist + Cross-Session Links + Pass 3

**Trạng thái:** ✅ Done (tasks 789-793)

**Phụ thuộc:** S26 complete

---

## Mục tiêu sprint

Giải quyết dứt điểm 3 tầng vấn đề về relationship trong graph memory:
1. **Tầng 1 — Entity hub noise:** Entity "User" kết nối toàn bộ facts với nhau → graph activation không phân biệt → blocklist các entity generic.
2. **Tầng 2 — Inter-session:** Mọi 7 loại edge hiện tại đều intra-session. Cross-session chỉ có entity hub "User" (vô nghĩa). Bổ sung semantic + entity cross-session links.
3. **Tầng 3 — Intra-session inter-chunk causal/transition:** Causal/transition chỉ hoạt động trong phạm vi 1 LLM call (1 chunk). Pass 3 bổ sung quan hệ cross-chunk trong session.

**Bối cảnh:** Phân tích trên bank `COGMEM_EXP_v11_e567_c003` cho thấy Casper mattress fact (CE score 0.998, tồn tại trong bank) bị rank 168/600+ trong RRF vì: 0 cross-session links, 0 temporal links (relative date), 68 entity links toàn qua hub "User".

---

## Task 789 — Entity blocklist: lọc generic entities khỏi link creation

**Vấn đề:** `process_entities_batch()` tạo entity link cho mọi shared entity kể cả "User". Vì 100% facts đều có entity "User" → hub gần fully-connected (~N² edges) → BFS spreading activation uniform noise.

**Fix:**
```python
_ENTITY_BLOCKLIST: frozenset[str] = frozenset({
    "user", "the user", "i", "me", "my", "we", "our",
})
```

Trong `process_entities_batch()`, lọc entity trước khi tạo link:
```python
for entity in fact.entities:
    normalized = _normalize_entity_name(entity)
    if entity and entity.strip() and normalized not in _ENTITY_BLOCKLIST:
        merged_entities.add(entity.strip())
```

**File:** `cogmem_api/engine/retain/entity_processing.py`

**Artifact:** `tests/artifacts/test_task789_entity_blocklist.py`

---

## Task 790 — Phase B: Cross-session semantic links via pgvector ANN

**Vấn đề:** `create_semantic_links_batch()` chỉ compare embeddings TRONG batch hiện tại. Cross-session semantic similarity không bao giờ được tính.

**Fix — thêm `create_cross_bank_semantic_links_batch()` vào `link_creation.py`:**
```python
async def create_cross_bank_semantic_links_batch(
    conn, bank_id: str, unit_ids: list[str], embeddings: list[list[float]],
    threshold: float = 0.6, top_k: int = 10
) -> int:
    """Cross-session: for each new fact, find top-k similar existing facts via ANN."""
    for unit_id, embedding in zip(unit_ids, embeddings):
        rows = await conn.fetch("""
            SELECT id::text, 1 - (embedding <=> $1::vector) AS similarity
            FROM memory_units
            WHERE bank_id = $2
              AND id::text != ALL($3::text[])
              AND 1 - (embedding <=> $1::vector) >= $4
            ORDER BY embedding <=> $1::vector
            LIMIT $5
        """, embedding, bank_id, exclude_set, threshold, top_k)
        # create bidirectional links
```

**Wire vào `orchestrator.py`** sau block in-batch link creation:
```python
await link_creation.create_cross_bank_semantic_links_batch(
    conn, bank_id, created_unit_ids, embeddings_for_links
)
```

**Config:**
- `COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_THRESHOLD` (default: `0.6`)
- `COGMEM_API_RETAIN_CROSS_BANK_SEMANTIC_TOP_K` (default: `10`)

**Files:** `cogmem_api/engine/retain/link_creation.py`, `cogmem_api/engine/retain/orchestrator.py`

**Artifact:** `tests/artifacts/test_task790_cross_bank_semantic.py`

---

## Task 791 — Phase B: Cross-session entity links (non-hub entities)

**Vấn đề:** Entity links trong `process_entities_batch()` chỉ pair units TRONG batch hiện tại. Session A có "coffee" và session B có "coffee" → không được link vì 2 retain_batch() riêng.

**Fix — thêm `build_cross_bank_entity_links()` vào `entity_processing.py`:**

Với mỗi new fact, với mỗi non-blocked entity name → tìm existing units connected through entity đó từ previous sessions → tạo bidirectional entity link.

**Files:** `cogmem_api/engine/retain/entity_processing.py`, `cogmem_api/engine/retain/orchestrator.py`

**Artifact:** `tests/artifacts/test_task791_cross_bank_entity.py`

---

## Task 792 — Pass 3: Intra-session inter-chunk relationship identification

**Vấn đề:** Causal/transition/action_effect relations chỉ hoạt động INTRA-CHUNK. Pass 1 chunk 0 và chunk 1 có index space riêng → không có causal link cross-chunk.

Ví dụ: Session về diet → chunk 0 extract "User had back pain" (experience), chunk 1 extract "User started yoga" (habit). Causal link "yoga caused by back pain" không được tạo.

**Fix — Pass 3 LLM call sau `dedup_facts()` trong `fact_extraction.py`:**

1. Build Pass 3 prompt: danh sách numbered facts + yêu cầu identify relations
2. LLM call → JSON `{"relations": [{"source": 0, "target": 3, "type": "causal", "strength": 0.8}, ...]}`
3. Merge results: ghi `edge_intent` vào `final_facts[source_index]`

**Pass 3 prompt (`cogmem_api/prompts/retain/pass3.py`):**
- Allowed types: `causal`, `fulfilled_by`, `a_o_causal`
- Rules: source/target are 0-based indices; strength >= 0.6; causal source_index < target_index
- Cap: skip Pass 3 nếu `len(final_facts) > pass3_max_facts` (default: 30)

**Config:**
- `COGMEM_API_RETAIN_PASS3_ENABLED` (default: `true`)
- `COGMEM_API_RETAIN_PASS3_MAX_FACTS` (default: `30`)

**Files:** `cogmem_api/prompts/retain/pass3.py`, `cogmem_api/engine/retain/fact_extraction.py`, `cogmem_api/engine/retain/types.py`

**Artifact:** `tests/artifacts/test_task792_pass3_relations.py`

---

## Task 793 — Phase B: Cross-session temporal, s_r_link, a_o_causal, transition

**Vấn đề:** Sau Task 790–791, inter-session còn 4 loại edge chưa có: `temporal`, `s_r_link`, `a_o_causal`, `transition`.

**Fix — thêm `create_cross_bank_structural_links_batch()` vào `link_creation.py`:**

- **Temporal cross-session**: Với mỗi new fact có `event_date`, query existing facts trong ±24h.
- **s_r_link cross-session**: Với mỗi new habit fact, tìm existing non-habit facts sharing non-blocked entities.
- **a_o_causal cross-session**: Với mỗi new action_effect fact, tìm existing non-action_effect facts sharing entities.
- **transition cross-session (heuristic)**: Với mỗi new experience fact, tìm existing intention facts (status='planning') sharing entities → create tentative fulfilled_by edge (weight 0.7).

**Files:** `cogmem_api/engine/retain/link_creation.py`, `cogmem_api/engine/retain/orchestrator.py`

**Artifact:** `tests/artifacts/test_task793_cross_bank_structural.py`

---

## Coverage Matrix sau S27

| Edge type | Intra-chunk | Inter-chunk intra-session | Inter-session |
|-----------|-------------|--------------------------|---------------|
| `entity` | ✅ hiện tại | ✅ hiện tại | ✅ Task 791 |
| `semantic` | ✅ hiện tại | ✅ hiện tại | ✅ Task 790 |
| `temporal` | ✅ hiện tại | ✅ hiện tại | ✅ Task 793 |
| `causal` | ✅ hiện tại | ✅ Task 792 (Pass 3) | ❌ excluded |
| `s_r_link` | ✅ hiện tại | ✅ hiện tại | ✅ Task 793 |
| `a_o_causal` | ✅ hiện tại | ✅ hiện tại | ✅ Task 793 |
| `transition` | ✅ hiện tại | ✅ Task 792 (Pass 3) | ✅ Task 793 (heuristic) |

---

## Verification Sprint S27

```bash
uv run python tests/artifacts/test_task789_entity_blocklist.py
uv run python tests/artifacts/test_task790_cross_bank_semantic.py
uv run python tests/artifacts/test_task791_cross_bank_entity.py
uv run python tests/artifacts/test_task792_pass3_relations.py
```

**Integration check — c003 mattress recall:**
1. Re-retain bank với S27 changes
2. Check cross-session semantic link EXISTS giữa furniture facts
3. Recall "what furniture have I bought or assembled?" → mattress phải xuất hiện trong top-25 (hiện tại rank 168)
4. Re-run eval batch → expect c003 pass (score 1.0 thay vì 0.0)

**Exit gate Sprint S27:**
1. Tất cả 4 artifact tests PASS.
2. Cross-session semantic links tồn tại giữa furniture facts trong c003 bank.
3. Entity "User" không xuất hiện trong bất kỳ entity link nào.
4. Recall rank của mattress fact ≤ 25 sau re-retain.
