# S19.5 Manual Tutorial - [cogmem_api/engine/search/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/__init__.py)

## Purpose (Mục đích)
- Tạo public API cho search package.
- Re-export graph retrievers, reranker và helper quản lý default graph retriever.

## Source File
- [cogmem_api/engine/search/__init__.py](https://github.com/triet4p/agent-memory-cognitive/blob/master/cogmem_api/engine/search/__init__.py)

## Symbol-by-symbol explanation
### GraphRetriever, BFSGraphRetriever, MPFPGraphRetriever
- Re-export các chiến lược graph retrieval chính.

### CrossEncoderReranker
- Re-export thành phần rerank cho recall pipeline.

### ParallelRetrievalResult
- Re-export kiểu kết quả retrieval 4-kênh.

### get_default_graph_retriever, set_default_graph_retriever
- API để lấy hoặc ghi đè graph retriever mặc định.

### __all__
- Khai báo public surface chính thức của search package.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- memory_engine.recall_async và các module runtime có thể import từ package search.

### Outbound dependencies
- graph_retrieval.py, mpfp_retrieval.py, reranking.py, retrieval.py.

## Runtime implications/side effects
- Import package search kéo import các module con đã re-export.

## Failure modes
- Lỗi import từ module con làm import search package thất bại.

## Verify commands
```powershell
uv run python -c "import cogmem_api.engine.search as s; print(sorted(s.__all__))"
```
