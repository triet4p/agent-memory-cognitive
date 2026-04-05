# S19.5 Manual Tutorial - cogmem_api/engine/search/graph_retrieval.py

## Purpose (Mục đích)
- Định nghĩa abstraction cho graph retrieval strategy.
- Cung cấp implementation BFS spreading activation có guard chống vòng lặp.

## Source File
- cogmem_api/engine/search/graph_retrieval.py

## Symbol-by-symbol explanation
### GraphRetriever
- Abstract interface cho chiến lược graph retrieval, trả tuple results và mpfp timings.

### BFSGraphRetriever.__init__
- Nhận các tham số điều khiển BFS:
  - entry point limit và threshold,
  - activation decay, min activation,
  - batch size,
  - refractory steps, firing quota, activation saturation.

### BFSGraphRetriever.retrieve
- Mở connection và gọi _retrieve_with_conn.

### BFSGraphRetriever._retrieve_with_conn
- Pipeline BFS:
  - tìm entry points semantic,
  - lan truyền activation kiểu SUM,
  - áp cycle guards,
  - fetch neighbors theo link weight,
  - boost causal links,
  - sort theo activation và lọc tags hoặc tag groups.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py gọi retriever.retrieve trong bước graph retrieval.

### Outbound dependencies
- db_utils.acquire_with_retry, memory_engine.fq_table.
- tags.py cho SQL filter và post-filter.
- search/types.py (RetrievalResult, MPFPTimings).

## Runtime implications/side effects
- Guard refractory, firing quota, saturation giúp tránh activation nổ trên đồ thị dày.
- Graph traversal có thể vượt qua ngữ cảnh ban đầu nên post-filter tags rất quan trọng.

## Failure modes
- Không tìm thấy entry points thì trả rỗng.
- budget nhỏ hoặc min_activation cao có thể làm traversal dừng sớm.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.graph_retrieval import BFSGraphRetriever; print(BFSGraphRetriever().name)"
```
