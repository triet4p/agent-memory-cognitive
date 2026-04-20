# Audit Report — Retain Tests
Date: 2026-04-19 21:44
Mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b
Runner: uv run python

## Summary

| Test file | Status | Note |
|-----------|--------|------|
| tests/retain/test_dialogue_action_effect.py | [FAIL] | AssertionError line 113 |
| tests/retain/test_dialogue_habit_routine.py | [PASS] | — |
| tests/retain/test_dialogue_intention_lifecycle.py | [FAIL] | AssertionError line 90 |
| tests/retain/test_dialogue_mixed_vi.py | [PASS] | — |
| tests/retain/test_dialogue_onboarding.py | [FAIL] | AssertionError line 102 |

Total: 2 passed, 3 failed, 0 errors

## Failure Details

### [1] tests/retain/test_dialogue_action_effect.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 131, in <module>
		main()
		~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 126, in main
		asyncio.run(run_test())
		~~~~~~~~~~~^^^^^^^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 195, in run
		return runner.run(main)
					 ~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 118, in run
		return self._loop.run_until_complete(task)
					 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\base_events.py", line 719, in run_until_complete
		return future.result()
					 ~~~~~~~~~~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 113, in run_test
		assert len(ae_facts) >= 2, (
					 ^^^^^^^^^^^^^^^^^^
AssertionError: Expected 2 action_effect facts (Redis + connection pooling), got 1
```

**Assertion thất bại:**
- Dòng: `assert len(ae_facts) >= 2`
- Giá trị thực tế: `got 1`

**Nguyên nhân sơ bộ (quan sát):**
- Kết quả trích xuất từ LLM thật chỉ tạo được 1 fact `action_effect` trong scenario yêu cầu tối thiểu 2 facts.

### [2] tests/retain/test_dialogue_intention_lifecycle.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_intention_lifecycle.py", line 127, in <module>
		main()
		~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_intention_lifecycle.py", line 122, in main
		asyncio.run(run_test())
		~~~~~~~~~~~^^^^^^^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 195, in run
		return runner.run(main)
					 ~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 118, in run
		return self._loop.run_until_complete(task)
					 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\base_events.py", line 719, in run_until_complete
		return future.result()
					 ~~~~~~~~~~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_intention_lifecycle.py", line 90, in run_test
		assert "fulfilled" in statuses, (
					 ^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected at least one intention with status 'fulfilled'. Got: {'planning'}
```

**Assertion thất bại:**
- Dòng: `assert "fulfilled" in statuses`
- Giá trị thực tế: `statuses = {'planning'}`

**Nguyên nhân sơ bộ (quan sát):**
- Kết quả trích xuất chỉ có `intention_status=planning`, chưa có fact `intention` ở trạng thái `fulfilled` như test yêu cầu.

### [3] tests/retain/test_dialogue_onboarding.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_onboarding.py", line 126, in <module>
		main()
		~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_onboarding.py", line 121, in main
		asyncio.run(run_test())
		~~~~~~~~~~~^^^^^^^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 195, in run
		return runner.run(main)
					 ~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\runners.py", line 118, in run
		return self._loop.run_until_complete(task)
					 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
	File "C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\asyncio\base_events.py", line 719, in run_until_complete
		return future.result()
					 ~~~~~~~~~~~~~^^
	File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_onboarding.py", line 102, in run_test
		assert any("bob" in e for e in all_entities), \
					 ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Entity 'Bob' not found. All entities: ['techvn', 'works', 'python', 'plans', 'kubernetes', 'believes', 'django']
```

**Assertion thất bại:**
- Dòng: `assert any("bob" in e for e in all_entities)`
- Giá trị thực tế: `all_entities = ['techvn', 'works', 'python', 'plans', 'kubernetes', 'believes', 'django']`

**Nguyên nhân sơ bộ (quan sát):**
- Output trích xuất không chứa thực thể `Bob` trong danh sách entities, dẫn tới fail assertion entity bắt buộc.

## Notes

- Không có file source nào được sửa trong quá trình audit này.
- Audit chạy ở mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b.
