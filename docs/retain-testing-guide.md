# Retain Pipeline — Testing Guide & Audit Protocol

## 1. Tổng quan test suite

Retain pipeline có hai nhóm test độc lập nhau, chạy khác nhau và phục vụ mục đích khác nhau.

### 1.1 Nhóm `tests/artifacts/` — Sprint artifact tests

Mục đích: xác nhận contract kỹ thuật của từng sprint task (file tồn tại, isolation khỏi `hindsight_api`, behavior với seeded facts không dùng LLM).

| File | Kiểm tra gì |
|------|------------|
| `test_task201_retain_baseline.py` | 6 fact types, temporal/entity/causal links, zero LLM usage |
| `test_task202_habit_network.py` | s_r_link từ habit node tới experience node đúng entity |
| `test_task203_intention_lifecycle.py` | intention_status, transition_relations |
| `test_task204_action_effect.py` | precondition/action/outcome, confidence, devalue_sensitive |
| `test_retain_slm_quality.py` | 40 tests: prompt structure, SLM quirk resilience, 6 network types |

Chạy một file:
```bash
uv run python tests/artifacts/test_task201_retain_baseline.py
```

### 1.2 Nhóm `tests/retain/` — Dialogue scenario tests

Mục đích: xác nhận pipeline trích xuất đúng fact type và metadata từ đoạn hội thoại thực tế, với hai chế độ LLM.

#### 1.2a Unit tests (không cần LLM — chạy offline hoàn toàn)

| File | Kiểm tra gì | Difficulty |
|------|-------------|-----------|
| `test_json_repair_resilience.py` | `parse_llm_json()` + json_repair recovery từ 3 dạng JSON lỗi: truncated, trailing comma, unquoted type | EASY |
| `test_temporal_sanitization.py` | `_sanitize_temporal_fact()`: xóa ngày hôm nay hallucinated, giữ nguyên khi có time keyword, xử lý ISO timestamp | EASY |
| `test_metadata_action_effect_fields.py` | action_effect luôn có precondition/action/outcome (kể cả khi LLM bỏ qua — fallback "N/A") | EASY |
| `test_fact_type_allowlist.py` | Fact type không hợp lệ (skill, preference, trait) bị remap/filter, chỉ giữ 6 type chuẩn | EASY |

#### 1.2b Dialogue tests — Easy (kỳ vọng pass với real LLM)

| File | Scenario | Assertion chính | Difficulty |
|------|----------|----------------|-----------|
| `test_dialogue_onboarding.py` | Bob joins TechVN | world + experience + intention(planning) + opinion; entities Bob, TechVN | EASY |
| `test_dialogue_habit_routine.py` | Morning email routine | habit + experience; repetition keyword; raw_snippet present | EASY |
| `test_dialogue_researcher_profile.py` | Dr. Kim at MIT — profile facts | 2+ world facts; entities Kim hoặc MIT | EASY |
| `test_dialogue_conference_experience.py` | NeurIPS attendance Dec 2025 | experience fact; entity NeurIPS; no temporal hallucination | EASY |
| `test_dialogue_strong_opinion.py` | TypeScript vs JavaScript opinions | 1+ opinion; confidence ∈ [0,1] | EASY-MEDIUM |

#### 1.2c Dialogue tests — Medium (nên pass với real LLM)

| File | Scenario | Assertion chính | Difficulty |
|------|----------|----------------|-----------|
| `test_dialogue_mixed_vi.py` | Alice/Anthropic mixed types | world + experience + opinion + habit; entity Alice | MEDIUM |
| `test_dialogue_action_effect.py` | Redis cache + connection pooling | 1+ action_effect; precondition/action/outcome; confidence ∈ [0,1] | MEDIUM |
| `test_dialogue_intention_lifecycle.py` | Plan → completed (85% coverage) | intention fulfilled hoặc planning; experience; entity payment | MEDIUM |
| `test_dialogue_goal_setting.py` | Eve — AWS cert goal by Q3 2026 | 1+ intention(planning); intention_status valid; entity Eve/AWS | MEDIUM |
| `test_dialogue_refactoring_outcome.py` | Frank — payment service refactor | 1+ action_effect; precondition/action/outcome; confidence valid | MEDIUM |
| `test_dialogue_team_collaboration.py` | Grace — FinCore team context | world + experience + habit; entity Grace/FinCore | MEDIUM |

#### 1.2d Dialogue tests — Hard (có thể không pass với zero-shot Ministral-3B)

| File | Scenario | Assertion chính | Difficulty |
|------|----------|----------------|-----------|
| `test_dialogue_abandoned_intention.py` | Henry — CockroachDB plan cancelled | intention(abandoned) OR abandonment trong fact text | HARD |
| `test_dialogue_implicit_cause_effect.py` | Ivy — connection pool implicit causality | action_effect present OR 2+ facts covering cause & effect | HARD |
| `test_dialogue_all_six_types.py` | Jake — tất cả 6 type trong 1 dialogue | ≥ 4/6 type present (HARD: all 6) | HARD |
| `test_dialogue_confidence_gradient.py` | Lena — 3 opinions với certainty khác nhau | 2+ opinions; confidence ∈ [0,1] nếu có | HARD |
| `test_dialogue_devalue_sensitive.py` | Mia — feature flag rollback | action_effect present; devalue_sensitive=True là bonus | HARD |

Chạy một file:
```bash
uv run python tests/retain/test_dialogue_onboarding.py
```

Chạy toàn bộ nhóm offline (FakeLLM):
```bash
for f in tests/retain/test_*.py; do echo "=== $f ==="; COGMEM_API_LLM_BASE_URL="" uv run python "$f" 2>&1 | tail -2; done
```

---

## 2. Shared infrastructure (`tests/retain/_shared.py`)

Tất cả các dialogue test đều import từ đây. Không được duplicate logic này vào từng file.

```python
from tests.retain._shared import make_config, resolve_llm
```

### `resolve_llm(fake_response)`

| Điều kiện | Hành vi |
|-----------|---------|
| `COGMEM_API_LLM_BASE_URL` được set | Tạo `LLMConfig` thật, gọi qua NGROK → Ministral-3B |
| Không set | Trả `_BaseFakeLLM(fake_response)` — không cần network |

In ra dòng `[LLM] real — <url>` hoặc `[LLM] offline — FakeLLM` để biết đang chạy mode nào.

### `make_config(mode="concise")`

Đọc các env var sau, fallback về default nếu không set:

| Env var | Default |
|---------|---------|
| `COGMEM_API_RETAIN_EXTRACTION_MODE` | `"concise"` |
| `COGMEM_API_RETAIN_MAX_COMPLETION_TOKENS` | `13000` |
| `COGMEM_API_RETAIN_CHUNK_SIZE` | `3000` |
| `COGMEM_API_RETAIN_MISSION` | `None` |
| `COGMEM_API_RETAIN_CUSTOM_INSTRUCTIONS` | `None` |

---

## 3. Chạy với LLM thật (Ministral-3B qua NGROK)

Khi Kaggle notebook đang chạy và NGROK tunnel đã bật:

```bash
# Windows PowerShell
$env:COGMEM_API_LLM_BASE_URL = "https://<ngrok-subdomain>.ngrok-free.app/v1"
$env:COGMEM_API_LLM_MODEL = "ministral3-3b"
$env:COGMEM_API_LLM_API_KEY = "ollama"
$env:COGMEM_API_RETAIN_LLM_TIMEOUT = "600"

uv run python tests/retain/test_dialogue_action_effect.py
```

```bash
# bash / Linux
COGMEM_API_LLM_BASE_URL="https://<ngrok-subdomain>.ngrok-free.app/v1" \
COGMEM_API_LLM_MODEL="ministral3-3b" \
uv run python tests/retain/test_dialogue_action_effect.py
```

Assertions được thiết kế soft (kiểm tra fact_type có mặt, entity xuất hiện) nên cùng một test chạy được cả hai mode.

---

## 4. Viết test dialogue mới

Mỗi scenario mới tạo **một file riêng** trong `tests/retain/`. Template:

```python
"""Retain pipeline — Dialogue: <Tên scenario>.

Scenario:
  <Mô tả ngắn bằng tiếng Anh.>

Expected extraction (at minimum):
  - 1+ "<fact_type>"  : <lý do>
  ...
"""
from __future__ import annotations
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.retain._shared import make_config, resolve_llm  # noqa: E402

DIALOGUE = """\
USER: ...
ASSISTANT: ...
"""

_FAKE_RESPONSE = {
    "facts": [
        {"fact_type": "<type>", "what": "<text>", "entities": ["<entity>"]},
    ]
}

async def run_test() -> None:
    from cogmem_api.engine.retain.fact_extraction import extract_facts_from_contents
    from cogmem_api.engine.retain.types import RetainContent

    content = RetainContent(
        content=DIALOGUE,
        context="<context_label>",
        event_date=datetime(2026, 1, 1, 9, 0, tzinfo=UTC),
    )
    facts, _chunks, _usage = await extract_facts_from_contents(
        contents=[content],
        llm_config=resolve_llm(_FAKE_RESPONSE),
        agent_name="test",
        config=make_config("concise"),
    )

    fact_types = {f.fact_type for f in facts}
    assert "<expected_type>" in fact_types, f"Missing '<expected_type>'. Got: {fact_types}"
    # ... thêm assertion

    print("OK  <mô tả assertion>")

def main() -> None:
    asyncio.run(run_test())
    print("All <scenario> dialogue retain tests passed.")

if __name__ == "__main__":
    main()
```

**Quy tắc assertion:**
- Dùng `assert <condition>, f"<message với giá trị thực tế>"` — không dùng assert trần.
- Assertion phải pass khi LLM thật trả về kết quả hợp lý (soft check), không hardcode text cụ thể.
- Với `action_effect`: luôn kiểm tra `metadata["precondition"]`, `metadata["action"]`, `metadata["outcome"]`.
- Với `intention`: luôn kiểm tra `metadata["intention_status"]` không phải `None`.

---

## 5. Quy trình Audit Lỗi Trung Thực (READ-ONLY)

> **NGUYÊN TẮC BẤT BIẾN: Khi chạy audit, Agent TUYỆT ĐỐI KHÔNG được sửa bất kỳ file nào — source code, test, log, hay document. Nhiệm vụ duy nhất là quan sát và báo cáo trung thực.**

### 5.1 Khi nào cần audit

- Trước khi bắt đầu một sprint mới để xác nhận baseline.
- Khi một test thất bại bất ngờ sau khi code thay đổi.
- Khi cần xác nhận xem các test hiện tại có còn phản ánh đúng behavior hay không.

### 5.2 Các bước audit

**Bước 1 — Thu thập kết quả thô**

Chạy từng test một và ghi lại toàn bộ stdout/stderr nguyên văn. Không được bỏ qua output.

```bash
uv run python tests/artifacts/test_task201_retain_baseline.py 2>&1
uv run python tests/artifacts/test_task202_habit_network.py 2>&1
uv run python tests/artifacts/test_task203_intention_lifecycle.py 2>&1
uv run python tests/artifacts/test_task204_action_effect.py 2>&1
uv run python tests/retain/test_dialogue_onboarding.py 2>&1
uv run python tests/retain/test_dialogue_habit_routine.py 2>&1
uv run python tests/retain/test_dialogue_action_effect.py 2>&1
uv run python tests/retain/test_dialogue_intention_lifecycle.py 2>&1
uv run python tests/retain/test_dialogue_mixed_vi.py 2>&1
```

**Bước 2 — Phân loại từng test**

Mỗi test được phân vào một trong ba trạng thái:

| Trạng thái | Ký hiệu | Ý nghĩa |
|-----------|---------|---------|
| PASS | `[PASS]` | Chạy đến cuối, không có exception, in ra dòng "... passed." |
| FAIL | `[FAIL]` | `AssertionError` hoặc exception trong `run_test()` / `main()` |
| ERROR | `[ERROR]` | Import error, `ModuleNotFoundError`, lỗi trước khi test logic chạy |

**Bước 3 — Với mỗi lỗi, ghi rõ**

1. **File**: đường dẫn đầy đủ từ repo root.
2. **Loại lỗi**: FAIL / ERROR.
3. **Traceback nguyên văn**: copy toàn bộ, không tóm tắt.
4. **Assertion thất bại** (nếu FAIL): dòng assertion và giá trị thực tế (`Got: ...`).
5. **Nguyên nhân sơ bộ**: mô tả ngắn gọn *quan sát được* từ traceback, không đoán mò.

### 5.3 Format báo cáo

```
# Audit Report — Retain Tests
Date: <YYYY-MM-DD HH:MM>
Mode: offline (FakeLLM) | real LLM (<base_url>)
Runner: uv run python

## Summary

| Test file | Status | Note |
|-----------|--------|------|
| tests/artifacts/test_task201_retain_baseline.py | [PASS] | — |
| tests/artifacts/test_task202_habit_network.py   | [FAIL] | AssertionError line 149 |
| tests/retain/test_dialogue_onboarding.py        | [PASS] | — |
| ...                                             | ...    | ... |

Total: X passed, Y failed, Z errors

## Failure Details

### [1] tests/artifacts/test_task202_habit_network.py — FAIL

**Traceback (nguyên văn):**
```
Traceback (most recent call last):
  File "tests/artifacts/test_task202_habit_network.py", line 172, in main
    asyncio.run(run_behavior_test(repo_root))
  File "tests/artifacts/test_task202_habit_network.py", line 149, in run_behavior_test
    assert len(habit_units) == 1, f"Expected exactly one habit node, got {len(habit_units)}"
AssertionError: Expected exactly one habit node, got 0
```

**Assertion thất bại:**
- Dòng: `assert len(habit_units) == 1`
- Giá trị thực tế: `habit_units = []`, `fact_types = {"world", "experience"}`

**Nguyên nhân sơ bộ (quan sát):**
Heuristic fallback không phân loại được "always checks her email" là habit — cần xem `_infer_fact_type()` trong `fact_extraction.py`.

---

### [2] tests/retain/test_dialogue_action_effect.py — ERROR

**Traceback (nguyên văn):**
```
ModuleNotFoundError: No module named 'tests.retain._shared'
```

**Nguyên nhân sơ bộ (quan sát):**
`_REPO_ROOT` chưa được insert vào `sys.path` trước khi import `_shared`.

---

## Notes

- Không có file nào bị sửa trong quá trình audit này.
- Audit chạy ở mode: offline (FakeLLM) vì `COGMEM_API_LLM_BASE_URL` không được set.
```

### 5.4 Quy tắc nghiêm ngặt khi viết báo cáo

1. **Không sửa bất kỳ file nào** — kể cả thêm dòng comment, xóa khoảng trắng, hay sửa typo. Nếu cần fix, đó là task riêng sau audit.
2. **Không "cải thiện" traceback** — copy nguyên văn, không rút gọn, không paraphrase.
3. **Không đoán nguyên nhân không có trong traceback** — chỉ viết những gì *quan sát được*.
4. **Không bỏ qua test PASS** — phải liệt kê tất cả trong bảng Summary, kể cả test pass.
5. **Ghi rõ mode LLM** — offline hay real, URL nào, model nào. Kết quả với real LLM có thể khác FakeLLM.
6. **Báo cáo đặt trong `reports/`** theo tên `audit_retain_<YYYYMMDD>.md`. Không đặt trong `logs/` (logs dành cho task summary).

### 5.5 Phân biệt audit và fix

| Hành động | Audit | Fix task |
|-----------|-------|----------|
| Chạy test và ghi output | Được phép | Được phép |
| Tạo file báo cáo mới | Được phép | Được phép |
| Sửa source code | **CẤM** | Được phép |
| Sửa test file | **CẤM** | Được phép |
| Sửa log/docs hiện có | **CẤM** | Được phép |
| Đề xuất fix | Được phép (trong báo cáo) | Thực hiện fix |

Sau khi audit xong, Agent báo cáo lên user và **chờ chỉ thị** — không tự ý chuyển sang fix.
