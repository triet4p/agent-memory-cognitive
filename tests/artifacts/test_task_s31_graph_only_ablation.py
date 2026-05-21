"""Sprint 31 — Graph-Only Ablation: validate GraphOnlyQueryAnalyzer,
skip_reranker wiring, and E7G–E11G profile definitions.

Run: uv run python tests/artifacts/test_task_s31_graph_only_ablation.py
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── 1. Validate GraphOnlyQueryAnalyzer ──────────────────────────────────


class TestGraphOnlyQueryAnalyzer(unittest.TestCase):
    """Verify GraphOnlyQueryAnalyzer returns graph-only weights."""

    def setUp(self):
        from cogmem_api.engine.query_analyzer import GraphOnlyQueryAnalyzer

        self.analyzer = GraphOnlyQueryAnalyzer()

    def test_load_noop(self):
        """load() should not raise."""
        self.analyzer.load()

    def test_analyze_returns_multi_hop_type(self):
        """analyze() should report query_type='multi_hop'."""
        result = self.analyzer.analyze("any query")
        self.assertEqual(result.query_type, "multi_hop")

    def test_analyze_returns_graph_only_weights(self):
        """analyze() should set graph=1.0, all other channels=0.0."""
        result = self.analyzer.analyze("any query")
        expected = {"semantic": 0.0, "bm25": 0.0, "graph": 1.0, "temporal": 0.0}
        self.assertDictEqual(result.rrf_weights, expected)

    def test_analyze_no_temporal_constraint(self):
        """analyze() should return no temporal constraint."""
        result = self.analyzer.analyze("any query")
        self.assertIsNone(result.temporal_constraint)

    def test_analyze_with_reference_date(self):
        """analyze() should accept reference_date kwarg."""
        result = self.analyzer.analyze("any query", reference_date=datetime(2026, 5, 20))
        self.assertEqual(result.rrf_weights["graph"], 1.0)


# ── 2. Validate RecallRequest fields ───────────────────────────────────


class TestRecallRequest(unittest.TestCase):
    """Verify HTTP RecallRequest accepts skip_reranker and graph_only."""

    def setUp(self):
        from cogmem_api.api.http import RecallRequest

        self.request_cls = RecallRequest

    def test_defaults(self):
        """skip_reranker and graph_only should default to False."""
        req = self.request_cls(query="test")
        self.assertFalse(req.skip_reranker)
        self.assertFalse(req.graph_only)

    def test_explicit_true(self):
        """Both should be settable to True."""
        req = self.request_cls(query="test", skip_reranker=True, graph_only=True)
        self.assertTrue(req.skip_reranker)
        self.assertTrue(req.graph_only)

    def test_explicit_false(self):
        """Both should be settable to False."""
        req = self.request_cls(query="test", skip_reranker=False, graph_only=False)
        self.assertFalse(req.skip_reranker)
        self.assertFalse(req.graph_only)


# ── 3. Validate E7G–E11G profiles ──────────────────────────────────────


class TestGraphOnlyAblationProfiles(unittest.TestCase):
    """Verify AblationProfile dataclass and E7G–E11G profile definitions."""

    def setUp(self):
        from scripts.eval_cogmem import AblationProfile, ABLATION_PROFILES

        self.Profile = AblationProfile
        self.profiles = ABLATION_PROFILES

    def test_dataclass_has_new_fields(self):
        """AblationProfile should have skip_reranker and graph_only fields."""
        p = self.Profile(
            profile_id="test",
            description="test",
            enabled_networks=(),
            recall_fact_types=(),
            adaptive_router_enabled=False,
            sum_activation_enabled=False,
        )
        self.assertFalse(p.skip_reranker)
        self.assertFalse(p.graph_only)

    def test_e7g_exists(self):
        """E7G profile should be defined."""
        self.assertIn("E7G", self.profiles)

    def test_e8g_exists(self):
        """E8G profile should be defined."""
        self.assertIn("E8G", self.profiles)

    def test_e9g_exists(self):
        """E9G profile should be defined."""
        self.assertIn("E9G", self.profiles)

    def test_e10g_exists(self):
        """E10G profile should be defined."""
        self.assertIn("E10G", self.profiles)

    def test_e11g_exists(self):
        """E11G profile should be defined."""
        self.assertIn("E11G", self.profiles)

    def test_e7g_has_graph_only_flags(self):
        """E7G should have skip_reranker=True and graph_only=True."""
        p = self.profiles["E7G"]
        self.assertTrue(p.skip_reranker)
        self.assertTrue(p.graph_only)

    def test_e7g_full_networks(self):
        """E7G should include all 6 network types."""
        p = self.profiles["E7G"]
        expected = ("world", "experience", "opinion", "habit", "intention", "action_effect")
        self.assertTupleEqual(p.enabled_networks, expected)
        self.assertTupleEqual(p.recall_fact_types, expected)

    def test_e8g_no_habit(self):
        """E8G should exclude habit."""
        p = self.profiles["E8G"]
        self.assertNotIn("habit", p.enabled_networks)
        self.assertNotIn("habit", p.recall_fact_types)
        self.assertIn("intention", p.enabled_networks)
        self.assertIn("action_effect", p.enabled_networks)

    def test_e9g_no_intention(self):
        """E9G should exclude intention."""
        p = self.profiles["E9G"]
        self.assertNotIn("intention", p.enabled_networks)
        self.assertNotIn("intention", p.recall_fact_types)
        self.assertIn("habit", p.enabled_networks)
        self.assertIn("action_effect", p.enabled_networks)

    def test_e10g_no_action_effect(self):
        """E10G should exclude action_effect."""
        p = self.profiles["E10G"]
        self.assertNotIn("action_effect", p.enabled_networks)
        self.assertNotIn("action_effect", p.recall_fact_types)
        self.assertIn("habit", p.enabled_networks)
        self.assertIn("intention", p.enabled_networks)

    def test_e11g_only_three_base_types(self):
        """E11G should only have world, experience, opinion."""
        p = self.profiles["E11G"]
        expected = ("world", "experience", "opinion")
        self.assertTupleEqual(p.enabled_networks, expected)
        self.assertTupleEqual(p.recall_fact_types, expected)
        self.assertTrue(p.skip_reranker)
        self.assertTrue(p.graph_only)


# ── 4. Validate build_recall_payload includes new fields ───────────────


class TestBuildRecallPayload(unittest.TestCase):
    """Verify build_recall_payload emits skip_reranker and graph_only."""

    def setUp(self):
        from scripts.eval_cogmem import AblationProfile, build_recall_payload

        self.build = build_recall_payload
        self.Profile = AblationProfile

    def test_regular_profile_omits_flags(self):
        """Regular (non-graph-only) profile should emit skip_reranker=False, graph_only=False."""
        p = self.Profile(
            profile_id="test",
            description="test",
            enabled_networks=("world",),
            recall_fact_types=("world",),
            adaptive_router_enabled=False,
            sum_activation_enabled=False,
        )
        payload = self.build(p, "test query")
        self.assertIn("skip_reranker", payload)
        self.assertIn("graph_only", payload)
        self.assertFalse(payload["skip_reranker"])
        self.assertFalse(payload["graph_only"])

    def test_graph_only_profile_emits_true(self):
        """Graph-only profile should emit skip_reranker=True, graph_only=True."""
        from scripts.eval_cogmem import ABLATION_PROFILES

        p = ABLATION_PROFILES["E7G"]
        payload = self.build(p, "test query")
        self.assertTrue(payload["skip_reranker"])
        self.assertTrue(payload["graph_only"])


# ── 5. Validate memory_engine.py recall_async signature ────────────────


class TestRecallAsyncSignature(unittest.TestCase):
    """Verify recall_async accepts skip_reranker and graph_only."""

    def test_signature_has_new_params(self):
        """recall_async should have skip_reranker and graph_only params."""
        import inspect
        from cogmem_api.engine.memory_engine import MemoryEngine

        sig = inspect.signature(MemoryEngine.recall_async)
        params = sig.parameters
        self.assertIn("skip_reranker", params)
        self.assertIn("graph_only", params)
        # Check defaults
        self.assertIs(params["skip_reranker"].default, False)
        self.assertIs(params["graph_only"].default, False)


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    sys.exit(0 if result.result.wasSuccessful() else 1)
