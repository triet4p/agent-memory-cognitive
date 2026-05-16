"""Sprint S29 G-6 artifact test — temporal link weight differentiation.

Run:  uv run python tests/artifacts/test_s29_g6_temporal_weight.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta


def test_g6_temporal_weight_differentiation():
    """Intra-session temporal weights now span 0.3-1.0 instead of all 1.0."""
    from cogmem_api.engine.retain.link_utils import build_temporal_links

    base = datetime(2024, 6, 1, 10, 0, 0)
    # Facts spaced 1 min, 5 min, 30 min, 1 hour, 2 hours apart
    dates = {
        "a": base,
        "b": base + timedelta(minutes=1),
        "c": base + timedelta(minutes=5),
        "d": base + timedelta(minutes=30),
        "e": base + timedelta(hours=1),
        "f": base + timedelta(hours=2),
    }

    links = build_temporal_links(dates, window_hours=24)

    # Build weight map: (from, to) → weight
    weight_map: dict[tuple[str, str], float] = {}
    for from_id, to_id, ltype, ttype, eid, w in links:
        if ltype == "temporal":
            weight_map[(from_id, to_id)] = w

    # 1-min pair should have highest weight
    w_1m = weight_map.get(("a", "b"), weight_map.get(("b", "a"), 0))
    assert w_1m > 0.9, f"1-min pair weight {w_1m:.4f} should be >0.9"

    # 30-min pair should have noticeably lower weight than 1-min
    w_30m = weight_map.get(("a", "d"), weight_map.get(("d", "a"), 0))
    assert w_30m < w_1m, f"30-min weight {w_30m:.4f} should be < 1-min weight {w_1m:.4f}"

    # 30-min weight should be around 0.5
    assert 0.4 <= w_30m <= 0.7, f"30-min weight {w_30m:.4f} should be ~0.5"

    # 1-hour pair should be lower than 30-min
    w_1h = weight_map.get(("a", "e"), weight_map.get(("e", "a"), 0))
    assert w_1h <= w_30m + 0.05, f"1-hour weight {w_1h:.4f} should be ≤ 30-min weight {w_30m:.4f}"

    # 2-hour pair should be clamped to 0.3
    w_2h = weight_map.get(("a", "f"), weight_map.get(("f", "a"), 0))
    assert w_2h == 0.3, f"2-hour pair weight {w_2h:.4f} should be 0.3"

    print("G-6 PASS: temporal weights span 0.3-1.0 with proper differentiation")
    print(f"        1-min={w_1m:.4f} 30-min={w_30m:.4f} 1-hour={w_1h:.4f} 2-hour={w_2h:.4f}")


def test_g6_same_timestamp_still_high():
    """Identical timestamps still produce weight ~1.0."""
    from cogmem_api.engine.retain.link_utils import build_temporal_links

    base = datetime(2024, 6, 1, 10, 0, 0)
    dates = {"a": base, "b": base}
    links = build_temporal_links(dates)
    weight_map = {}
    for from_id, to_id, ltype, ttype, eid, w in links:
        if ltype == "temporal":
            weight_map[(from_id, to_id)] = w

    w = weight_map.get(("a", "b"), 0)
    assert w == 1.0, f"Identical timestamps should give weight 1.0, got {w:.4f}"
    print("G-6 PASS: identical timestamps still weight = 1.0")


def test_g6_window_respected():
    """Facts beyond window_hours produce no temporal link."""
    from cogmem_api.engine.retain.link_utils import build_temporal_links

    base = datetime(2024, 6, 1, 10, 0, 0)
    dates = {"a": base, "b": base + timedelta(hours=25)}
    links = build_temporal_links(dates, window_hours=24)
    assert len(links) == 0, f"25-hour gap with 24h window should have 0 links, got {len(links)}"
    print("G-6 PASS: 24h window still respected")


if __name__ == "__main__":
    tests = [
        ("weight-differentiation", test_g6_temporal_weight_differentiation),
        ("same-timestamp", test_g6_same_timestamp_still_high),
        ("window-respected", test_g6_window_respected),
    ]

    failures = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f"FAIL G-6/{name}: {e}")
            failures += 1

    print()
    if failures:
        print(f"RESULT: {len(tests) - failures}/{len(tests)} PASS, {failures} FAIL")
        sys.exit(1)
    else:
        print(f"RESULT: {len(tests)}/{len(tests)} PASS — G-6 temporal weight gates PASS")
        sys.exit(0)
