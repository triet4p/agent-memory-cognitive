# S19.4 Manual Tutorial - [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py)

## Purpose (Mục đích)
- Điều phối tạo các loại links trong retain pipeline.
- Bao phủ temporal, semantic, causal, s_r_link, action_effect, transition.
- Áp dụng guard ngữ nghĩa cho typed transition và causal relation.

## Source File
- [cogmem_api/engine/retain/link_creation.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/retain/link_creation.py)

## Symbol-by-symbol explanation
### create_temporal_links_batch(conn, bank_id, unit_ids)
- Lấy event_date theo unit và tạo temporal links trong cửa sổ thời gian.

### create_semantic_links_batch(conn, bank_id, unit_ids, embeddings)
- Tạo semantic links dựa trên cosine similarity trong batch.

### create_causal_links_batch(conn, unit_ids, facts)
- Tạo causal links từ causal_relations, chỉ nhận relation_type caused_by.
- Chỉ cho phép target trước source để giữ hướng nhân quả.

### create_habit_sr_links_batch(conn, unit_ids, facts)
- Tạo s_r_link từ habit node sang fact khác khi có giao entities.
- Tính weight theo tỷ lệ overlap.

### create_transition_links_batch(conn, unit_ids, facts)
- Tạo transition typed edges theo TRANSITION_EDGE_RULES.
- Bỏ transition_type abandoned vì là status-only update.

### create_action_effect_links_batch(conn, unit_ids, facts)
- Đường chính: dùng action_effect_relations explicit.
- Đường fallback: suy target theo giao entities với non-action_effect facts.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- orchestrator.py gọi toàn bộ hàm create_*_links_batch sau khi facts đã lưu DB.

### Outbound dependencies
- retain/link_utils.py để build/insert link records.
- retain/types.py (ProcessedFact, TRANSITION_EDGE_RULES, clamp_relation_strength).

## Runtime implications/side effects
- Một batch lớn có thể sinh rất nhiều edge, ảnh hưởng tốc độ ghi và truy vấn graph downstream.
- Guard transition giúp tránh tạo cạnh lifecycle sai semantics.

## Failure modes
- target_fact_index ngoài phạm vi bị bỏ qua.
- embeddings thiếu hoặc lệch chiều làm semantic links giảm hoặc bằng 0.

## Verify commands
```powershell
uv run python -c "import inspect; from cogmem_api.engine.retain.link_creation import create_transition_links_batch; print(inspect.iscoroutinefunction(create_transition_links_batch))"
uv run python -c "from cogmem_api.engine.retain.types import TRANSITION_EDGE_RULES; print(sorted(TRANSITION_EDGE_RULES.keys()))"
```
