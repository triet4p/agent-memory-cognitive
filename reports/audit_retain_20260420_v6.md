# Audit Report — Retain Tests
Date: 2026-04-20 23:35
Mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b
Runner: uv run python

## Summary

| Test file | Status | Note |
|-----------|--------|------|
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_abandoned_intention.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py | [FAIL] | AssertionError line 137 |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_all_six_types.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_conference_experience.py | [FAIL] | AssertionError line 105 |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_confidence_gradient.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_devalue_sensitive.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_goal_setting.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_habit_routine.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_implicit_cause_effect.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_intention_lifecycle.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_mixed_vi.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_onboarding.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_refactoring_outcome.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_researcher_profile.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_strong_opinion.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_team_collaboration.py | [FAIL] | AssertionError line 108 |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_fact_type_allowlist.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_json_repair_resilience.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_metadata_action_effect_fields.py | [PASS] | — |
| F:\ai-ml\agent-memory-cognitive\tests\retain\test_temporal_sanitization.py | [PASS] | — |

Total: 17 passed, 3 failed, 0 errors

## Failure Details

### [1] F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 137, in <module>
    main()
    ~~~~^^
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_action_effect.py", line 132, in main
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
    assert cache_fact is not None, (
           ^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Expected a caching/Redis action_effect fact. Entities: [['system']], Texts: ['Timeouts resolved with connection pooling']
```

**Assertion thất bại:**
- AssertionError: Expected a caching/Redis action_effect fact. Entities: [['system']], Texts: ['Timeouts resolved with connection pooling']

**Nguyên nhân sơ bộ (quan sát):**
- Test thất bại do assertion không thỏa với output thực tế ở lần chạy này.

### [2] F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_conference_experience.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_conference_experience.py", line 105, in <module>
    main()
    ~~~~^^
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_conference_experience.py", line 100, in main
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
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_conference_experience.py", line 80, in run_test
    assert any("neurips" in e for e in all_entities), (
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Entity 'NeurIPS' not found. All entities: ['attended', 'december', 'december', 'presented', 'december', 'room']
```

**Assertion thất bại:**
- AssertionError: Entity 'NeurIPS' not found. All entities: ['attended', 'december', 'december', 'presented', 'december', 'room']

**Nguyên nhân sơ bộ (quan sát):**
- Test thất bại do assertion không thỏa với output thực tế ở lần chạy này.

### [3] F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_team_collaboration.py — FAIL

**Traceback (nguyên văn):**
```text
Traceback (most recent call last):
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_team_collaboration.py", line 108, in <module>
    main()
    ~~~~^^
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_team_collaboration.py", line 103, in main
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
  File "F:\ai-ml\agent-memory-cognitive\tests\retain\test_dialogue_team_collaboration.py", line 89, in run_test
    assert "habit" in fact_types, f"Missing 'habit' fact. Got: {fact_types}"
           ^^^^^^^^^^^^^^^^^^^^^
AssertionError: Missing 'habit' fact. Got: {'experience', 'world'}
```

**Assertion thất bại:**
- AssertionError: Missing 'habit' fact. Got: {'experience', 'world'}

**Nguyên nhân sơ bộ (quan sát):**
- Test thất bại do assertion không thỏa với output thực tế ở lần chạy này.

## Notes

- Không có file source nào được sửa trong quá trình audit này.
- Audit chạy ở mode: real LLM (https://unvacillating-braden-worriless.ngrok-free.dev/v1); model=ministral3-3b
