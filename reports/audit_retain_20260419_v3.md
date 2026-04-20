# Audit Report — Retain Tests
Date: 2026-04-19 22:29
Mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b
Runner: uv run python

## Summary

| Test file | Status | Note |
|-----------|--------|------|
| tests/retain/test_dialogue_action_effect.py | [FAIL] | AssertionError line 108 |
| tests/retain/test_dialogue_habit_routine.py | [PASS] | — |
| tests/retain/test_dialogue_intention_lifecycle.py | [FAIL] | AssertionError line 90 |
| tests/retain/test_dialogue_mixed_vi.py | [PASS] | — |
| tests/retain/test_dialogue_onboarding.py | [FAIL] | AssertionError line 110 |

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
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 108, in run_test
    assert redis_fact is not None, (
           ^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected a Redis action_effect fact. Entities across ae_facts: [['Response'], ['Eliminated']]
```

**Assertion thất bại:**
- Dòng: `assert redis_fact is not None`
- Giá trị thực tế: `Entities across ae_facts: [['Response'], ['Eliminated']]`

**Nguyên nhân sơ bộ (quan sát):**
- Các `action_effect` được trích xuất nhưng entities không chứa tín hiệu Redis như test mong đợi.

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
- Kết quả hiện tại vẫn chỉ có `intention_status=planning`.

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
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_onboarding.py", line 110, in run_test
    assert usage.total_tokens > 0, "Token usage should be tracked"
           ^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Token usage should be tracked
```

**Assertion thất bại:**
- Dòng: `assert usage.total_tokens > 0`
- Giá trị thực tế: `usage.total_tokens = 0`

**Nguyên nhân sơ bộ (quan sát):**
- Thông tin token usage vẫn bằng 0 trong lần chạy thực tế này.

## Notes

- Không có file source nào được sửa trong quá trình audit này.
- Audit chạy ở mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b.
