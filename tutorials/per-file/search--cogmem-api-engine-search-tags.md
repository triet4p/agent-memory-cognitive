# S19.5 Manual Tutorial - cogmem_api/engine/search/tags.py

## Purpose (Mục đích)
- Cung cấp tiện ích lọc kết quả recall theo tags.
- Hỗ trợ cả SQL filter builder và post-filter phía Python.
- Hỗ trợ điều kiện compound với and hoặc or hoặc not qua TagGroup.

## Source File
- cogmem_api/engine/search/tags.py

## Symbol-by-symbol explanation
### TagsMatch và _parse_tags_match
- Định nghĩa bốn mode lọc tags: any, all, any_strict, all_strict.

### build_tags_where_clause, build_tags_where_clause_simple
- Tạo SQL clause cho lọc tags theo mode và param offset.

### filter_results_by_tags
- Lọc phía Python cho trường hợp kết quả không đi qua SQL trực tiếp (ví dụ graph traversal).

### TagGroupLeaf, TagGroupAnd, TagGroupOr, TagGroupNot, TagGroup
- Model Pydantic cho cấu trúc filter lồng nhau.

### _build_group_clause, build_tag_groups_where_clause
- Build SQL clause đệ quy cho compound tag groups.

### _match_group, filter_results_by_tag_groups
- Đánh giá logic group đệ quy ở phía Python.

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- retrieval.py, graph_retrieval.py, link_expansion_retrieval.py, mpfp_retrieval.py.

### Outbound dependencies
- pydantic BaseModel và Field.

## Runtime implications/side effects
- any hoặc all mặc định giữ backward compatibility bằng cách cho phép untagged memories.
- strict modes loại untagged memories, có thể giảm recall nếu dữ liệu chưa được gắn tags đều.

## Failure modes
- TagGroup cấu hình sai có thể tạo filter quá chặt và trả rỗng.

## Verify commands
```powershell
uv run python -c "from cogmem_api.engine.search.tags import build_tags_where_clause_simple; print(build_tags_where_clause_simple(['u:a'], 3))"
uv run python -c "from cogmem_api.engine.search.tags import TagGroupLeaf; print(TagGroupLeaf(tags=['a']).match)"
```
