# S19.3 Manual Tutorial - cogmem_api/engine/cross_encoder.py

## Purpose (Mục đích)
- Định nghĩa abstraction reranker cross-encoder cho search pipeline.
- Hỗ trợ 3 chế độ provider: local, TEI remote, và rrf passthrough.
- Tạo factory theo cấu hình để chọn provider phù hợp runtime.

## Source File
- cogmem_api/engine/cross_encoder.py

## Symbol-by-symbol explanation
### CrossEncoderModel (ABC)
- Contract trừu tượng gồm provider_name, initialize(), predict().

### LocalSTCrossEncoder
- Provider local dùng sentence-transformers CrossEncoder.
- _executor (class-level): ThreadPoolExecutor dùng chung cho suy luận đồng bộ.
- initialize(): import động CrossEncoder, tải model, dựng executor.
- _predict_sync(): gọi model.predict cho danh sách (query, text).
- predict(): chuyển _predict_sync sang run_in_executor để tránh block event loop.

### RemoteTEICrossEncoder
- Provider gọi TEI endpoint qua HTTP.
- _global_semaphore (class-level): giới hạn concurrency toàn cục.
- initialize(): tạo AsyncClient và probe /info để fail-fast endpoint.
- _rerank_batch(): gọi POST /rerank cho một batch.
- predict(): gom pair theo query, chia batch theo batch_size, gọi song song rồi ghép kết quả về đúng index.

### RRFPassthroughCrossEncoder
- Provider no-op cho chế độ rrf.
- predict() trả điểm cố định 0.5, giữ thứ tự dựa vào pipeline trước đó.

### create_cross_encoder_from_env()
- Đọc config.reranker_provider.
- local -> LocalSTCrossEncoder.
- tei -> RemoteTEICrossEncoder (bắt buộc có URL).
- rrf -> RRFPassthroughCrossEncoder.
- Provider lạ: cảnh báo log và fallback về rrf passthrough.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- Pipeline reranking trong engine/search gọi factory hoặc provider methods để chấm điểm candidate.

### Outbound dependencies
- cogmem_api/config.py qua get_config().
- sentence_transformers (tùy chọn), httpx, asyncio, ThreadPoolExecutor.

## Runtime implications/side effects
- Local provider dùng thread pool, tăng throughput nhưng tiêu tốn CPU/RAM theo model.
- TEI provider phụ thuộc mạng; semaphore toàn cục giới hạn bùng nổ request.
- RRF passthrough ổn định nhất nhưng không thêm tín hiệu semantic sâu.

## Failure modes
- Thiếu sentence-transformers gây ImportError ở local provider.
- TEI URL sai hoặc service down gây lỗi HTTP trong initialize/predict.
- Cấu hình provider sai có thể fallback silent về rrf (chỉ có warning log).

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.cross_encoder import RRFPassthroughCrossEncoder; import asyncio; print(asyncio.run(RRFPassthroughCrossEncoder().predict([('q','t')])) )"
uv run python -c "from cogmem_api.engine.cross_encoder import create_cross_encoder_from_env; print(type(create_cross_encoder_from_env()).__name__)"
```
