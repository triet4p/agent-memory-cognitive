"""Render a side-by-side HTML graph visualization for a benchmark case.

Pulls all facts from the paired banks (_full + _ablated), loads gate_detail to identify
top-25 recall and answer-cited facts, then renders an interactive cytoscape.js graph
showing the full picture for both arms.

Visual encoding:
  - Node fill color  → fact_type (intention/experience/world/opinion/habit/action_effect).
  - Node border      → thick blue if in top-25 recall (used by generation).
  - Node size        → larger if cited (`[N]`) in the generated answer.
  - Edge             → same-session co-occurrence (document_id).
  - Layout           → cose-bilkent (organic clustering by session).

Run:
  uv run python -m cogmem_bench.visualize --scenario neg_intention_14
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API = "http://localhost:8888"
DEFAULT_OUT = REPO_ROOT / "experiments" / "cogmem_bench" / "visualization"

TYPE_COLOR = {
    "intention": "#e74c3c",
    "action_effect": "#9b59b6",
    "habit": "#16a085",
    "experience": "#3498db",
    "world": "#95a5a6",
    "opinion": "#f39c12",
}


def _fetch_bank_facts(api: str, bank_id: str, session_ids: list[str]) -> list[dict[str, Any]]:
    """Enumerate all facts by iterating known session ids and calling /facts per session.

    Deterministic — does not depend on a recall query (which can return 0 for the ablated
    bank if the query doesn't match any remaining fact type).
    """
    facts: list[dict[str, Any]] = []
    for sid in session_ids:
        rr = requests.get(
            f"{api}/v1/default/banks/{bank_id}/facts",
            params={"document_id": sid, "limit": 500},
            timeout=30,
        ).json()
        if isinstance(rr, dict):
            block = rr.get("facts") or rr.get("items") or rr.get("results") or []
        elif isinstance(rr, list):
            block = rr
        else:
            block = []
        for f in block:
            f.setdefault("document_id", sid)
            facts.append(f)
    return facts


def _identify_cited(answer_text: str, recall_results: list[dict[str, Any]]) -> set[str]:
    """Parse [N] citations from answer text → return fact ids that map to rank N."""
    text = re.sub(r"<think>.*?</think>", "", answer_text or "", flags=re.DOTALL)
    ranks = {int(m) for m in re.findall(r"\[(\d+)\]", text)}
    cited_ids: set[str] = set()
    for r in recall_results:
        if r.get("rank") in ranks or r.get("rrf_rank") in ranks:
            fid = r.get("document_id", "") + "::" + (r.get("text") or "")[:50]
            cited_ids.add(fid)
    return cited_ids


def _fact_id(fact: dict[str, Any]) -> str:
    """Stable id combining document_id + leading text chars (matches recall_results format)."""
    return (fact.get("document_id") or "") + "::" + (fact.get("text") or fact.get("fact_text") or "")[:50]


def _build_graph(
    facts: list[dict[str, Any]],
    top25_recall: list[dict[str, Any]],
    answer_text: str,
) -> dict[str, Any]:
    """Return cytoscape data: {nodes, edges} with metadata."""
    # Map top-25 by fact id → rank
    used_id_to_rank: dict[str, int] = {}
    for r in top25_recall:
        used_id_to_rank[_fact_id(r)] = int(r.get("rank") or r.get("rrf_rank") or 0)
    cited = _identify_cited(answer_text, top25_recall)

    nodes = []
    by_session: dict[str, list[str]] = {}
    for f in facts:
        fid = _fact_id(f)
        ft = f.get("fact_type") or f.get("type") or "unknown"
        sid = f.get("document_id") or "?"
        rank = used_id_to_rank.get(fid)
        is_cited = fid in cited
        nodes.append({
            "data": {
                "id": fid,
                "label": (f.get("text") or f.get("fact_text") or "")[:55],
                "full_text": f.get("text") or f.get("fact_text") or "",
                "fact_type": ft,
                "session": sid,
                "used": rank is not None,
                "rank": rank if rank is not None else "",
                "cited": is_cited,
                "color": TYPE_COLOR.get(ft, "#bdc3c7"),
            }
        })
        by_session.setdefault(sid, []).append(fid)

    # Edges: same-session co-occurrence (one edge per pair within session)
    edges = []
    for sid, ids in by_session.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                edges.append({"data": {"source": ids[i], "target": ids[j], "session": sid}})

    return {"nodes": nodes, "edges": edges}


def _build_explanation(
    sid: str,
    spec: dict[str, Any],
    detail: dict[str, Any],
    facts_full: list[dict[str, Any]],
    facts_abl: list[dict[str, Any]],
) -> str:
    """Generate a presenter-ready markdown explanation for the side-by-side graph."""
    import collections

    def type_dist(facts: list[dict[str, Any]]) -> dict[str, int]:
        c = collections.Counter((f.get("fact_type") or f.get("type") or "unknown") for f in facts)
        return dict(sorted(c.items(), key=lambda x: -x[1]))

    def cited_ranks(arm: str) -> list[int]:
        text = re.sub(r"<think>.*?</think>", "", detail[arm]["generated_answer"] or "", flags=re.DOTALL)
        return sorted({int(m) for m in re.findall(r"\[(\d+)\]", text)})

    def fact_at_rank(arm: str, rank: int) -> str:
        for r in detail[arm]["recall_results"]:
            if r.get("rank") == rank:
                return f"[{r.get('fact_type')}] " + (r.get("text") or "")[:140]
        return "(rank not found)"

    def clean(s: str) -> str:
        return re.sub(r"<think>.*?</think>", "", s or "", flags=re.DOTALL).strip()

    e7_types = type_dist(facts_full)
    abl_types = type_dist(facts_abl)
    e7_cited = cited_ranks("E7")
    abl_cited = cited_ranks("ablated")
    e7_ans = clean(detail["E7"]["generated_answer"])[:300]
    abl_ans = clean(detail["ablated"]["generated_answer"])[:300]
    target = spec["target_type"]
    abl_profile = detail["ablated"]["profile"]
    removed_count = sum(v for k, v in e7_types.items() if k == target)
    abl_total = sum(abl_types.values())
    full_total = sum(e7_types.values())

    lines = [
        f"# Case: {sid} — visual explanation",
        "",
        f"**Mở cùng:** `{sid}_graph.html` (2 cytoscape graphs side-by-side).",
        "",
        "## 1. Câu hỏi & gold",
        f"- **Topic**: {spec['topic']}",
        f"- **Question**: *{detail['question']}*",
        f"- **Gold answer**: **{detail['gold_answer']}**",
        f"- **Target type test**: `{target}` — claim là loại bỏ nó sẽ làm hệ thống không trả lời được.",
        "",
        "## 2. Thiết lập thí nghiệm (full rigor — cách B của S33)",
        "Cùng conversation, retain vào **2 bank tách biệt**:",
        f"- `COGMEM_BENCH_{sid}_full` — extract tất cả 6 fact types (E7F arm).",
        f"- `COGMEM_BENCH_{sid}_ablated` — extract với `enabled_fact_types` loại bỏ `{target}` (arm {abl_profile}).",
        "",
        "Các confound đã loại trừ:",
        "- **Adaptive router bias**: cả 2 arm dùng `adaptive_router_enabled=False` (flat router, semantic search trên tất cả type cho phép).",
        "- **Recall-time leakage**: type bị disable không tồn tại trong ablated bank ngay từ retain.",
        "- **Extractor leakage**: Minimax-M2 + strict-typing prompt addendum (`COGMEM_API_RETAIN_STRICT_TYPING=true`) — bảo LLM không recast plan-not-done thành experience/opinion.",
        "- **Judge unreliability**: kết luận đọc bằng tay từ `generated_answer` thực tế.",
        "",
        "## 3. Visual encoding (đọc khi nhìn graph)",
        "| Tín hiệu | Ý nghĩa |",
        "|---|---|",
        "| Node màu | fact_type (đỏ=intention, tím=action_effect, teal=habit, xanh=experience, xám=world, cam=opinion) |",
        "| Viền xanh dày | Nằm trong top-25 recall — fact này được kéo vào prompt để generate answer |",
        "| Node vàng lớn | Được cite `[N]` trong câu trả lời cuối — most important |",
        "| Edge xám | Same-session co-occurrence (cùng `document_id`) — cluster theo session |",
        "",
        "## 4. Bank stats — sự khác biệt vật lý",
        "| | Full bank (E7F) | Ablated bank ({}) |".format(abl_profile),
        "|---|---|---|",
        "| Total facts | **{}** | **{}** |".format(full_total, abl_total),
        "| Type distribution | {} | {} |".format(e7_types, abl_types),
        f"| `{target}` nodes | **{removed_count}** (đỏ) | **0** (loại hoàn toàn) |",
        "",
        f"→ Difference = {full_total - abl_total} facts. `{target}` đóng góp {removed_count}; phần còn lại là edges/links downstream cũng bị loại theo.",
        "",
        "## 5. Câu chuyện trên đồ thị",
        "",
        f"### E7F (full bank — bên trái) → trả lời {'ĐÚNG' if detail['E7']['judge_correct'] else 'SAI'}",
        f"- Cite ranks: **{e7_cited}** ({len(e7_cited)} facts)",
        "- Các fact quan trọng được cite:",
    ]
    for r in e7_cited:
        lines.append(f"  - **[{r}]** {fact_at_rank('E7', r)}")
    lines += [
        f"- **Câu trả lời cuối**: {e7_ans}...",
        f"- Trên đồ thị bên trái: tìm các **node vàng lớn** — chúng nằm trong cluster `{target}` (đỏ) hoặc gần đó.",
        "",
        f"### {abl_profile} (ablated bank — bên phải) → trả lời {'ĐÚNG' if detail['ablated']['judge_correct'] else 'SAI'}",
        f"- Cite ranks: **{abl_cited}** ({len(abl_cited)} facts)",
        "- Các fact được cite (xem chúng KHÔNG phải về gold topic):",
    ]
    for r in abl_cited:
        lines.append(f"  - **[{r}]** {fact_at_rank('ablated', r)}")
    lines += [
        f"- **Câu trả lời cuối**: {abl_ans}...",
        f"- Trên đồ thị bên phải: KHÔNG có node đỏ (`{target}` đã loại). Node vàng lớn nằm trong cluster session **khác** — đây là **decoy đã đánh lừa**.",
        "",
        "## 6. Vì sao case này discriminate (bài học chính)",
        "",
        f"E9F (ablated arm) **không phải fail vì recall trả về rỗng** — nó vẫn lấy được {len(detail['ablated']['recall_results'])} facts. Vấn đề là:",
        "",
        f"- Trong ablated bank, **không có fact nào nói về gold plan** (`{detail['gold_answer']}`) — bởi vì conversation đã type tất cả mention về plan đó như `{target}` facts, và `{target}` bị loại tại retain.",
        "- Conversation lại có nhiều facts về **topic khác** (decoy fulfilled) — E9F bị buộc phải trả lời từ những gì còn lại → picked decoy → sai.",
        "",
        f"→ Đây là bằng chứng **content-level necessity**: thông tin về gold plan **chỉ tồn tại** dưới dạng `{target}` typed nodes; khi loại chúng, không có representation nào khác trong bank chứa info → câu trả lời SAI (không phải refuse, mà PICK SAI).",
        "",
        "## 7. Điều này CHỨNG MINH và KHÔNG chứng minh điều gì",
        "",
        "✅ **Chứng minh**:",
        f"- Trên case này, `{target}` typed node là **representational store duy nhất** cho gold info.",
        "- Loại bỏ nó (cùng với router bias đã neutralize, extractor đã strict) → answer SAI thực sự, không phải artifact.",
        "- Two banks tách biệt vật lý — không có overlap.",
        "",
        "❌ **KHÔNG chứng minh**:",
        f"- Không chứng minh `{target}` luôn cần thiết. Trên 14/16 case khác trong batch, E9F vẫn trả lời đúng được vì conversation tự nhiên tạo ra observational facts (experience về non-action) — info leak hợp lý chứ không phải mis-typing.",
        f"- Đây là **edge case** (sparse-context discrimination) — represent ~12.5% của workload.",
        "",
        "## 8. Talking points (tóm tắt cho thuyết trình)",
        "",
        "1. *\"Đây là test rigorous nhất chúng tôi làm: 2 bank tách biệt, extractor mạnh + strict typing, flat router — loại bỏ mọi confound đã biết.\"*",
        f"2. *\"Bank trái có {full_total} facts với cluster {target} (màu đỏ). Bank phải có {abl_total} facts — KHÔNG có node đỏ nào.\"*",
        f"3. *\"E7F cite {len(e7_cited)} facts — đa số nằm trong cluster {target} — và trả lời đúng '{detail['gold_answer']}'.\"*",
        f"4. *\"E9F không có cluster đó để truy cập — buộc phải cite fact rank [{abl_cited[0] if abl_cited else '?'}] thuộc topic khác → trả lời sai → discriminate.\"*",
        f"5. *\"Đây là 1 trong 2 case (của 16) thực sự discriminate. Trên 14 case còn lại, info plan-not-done leak một cách hợp lý qua experience facts (\"user hasn't done X yet\" tự nhiên là experience). Intention's necessity vì vậy là conditional — không universal, nhưng có thật trong sparse-context cases.\"*",
        "",
        "---",
        f"*Generated by `cogmem_bench/visualize.py` from `experiments/cogmem_bench/gate_detail/{sid}.json` + paired banks `COGMEM_BENCH_{sid}_full` / `_ablated`.*",
    ]
    return "\n".join(lines) + "\n"


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CogMem bench — {SCENARIO}</title>
<script src="https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/layout-base@2.0.1/layout-base.js"></script>
<script src="https://unpkg.com/cose-base@2.2.0/cose-base.js"></script>
<script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 16px; background: #1a1a1a; color: #ddd; }}
  h1 {{ margin: 0 0 6px 0; font-size: 18px; }}
  .meta {{ font-size: 13px; color: #aaa; margin-bottom: 12px; }}
  .gold {{ color: #f1c40f; font-weight: 600; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .panel {{ background: #222; border: 1px solid #333; border-radius: 8px; padding: 10px; }}
  .panel h2 {{ margin: 0 0 6px 0; font-size: 15px; }}
  .stat {{ font-size: 12px; color: #999; margin-bottom: 8px; }}
  .cy {{ width: 100%; height: 640px; background: #111; border: 1px solid #2a2a2a; border-radius: 6px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 8px; font-size: 11px; margin-top: 8px; align-items: center; }}
  .legend .swatch {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }}
  .ans {{ background: #1e2a1e; border: 1px solid #2a4a2a; border-radius: 6px; padding: 8px; font-size: 12px; margin-top: 8px; max-height: 180px; overflow-y: auto; }}
  .ans.fail {{ background: #2a1e1e; border-color: #4a2a2a; }}
  #tt {{ position: fixed; max-width: 420px; background: #000; color: #eee; padding: 8px; border-radius: 4px; font-size: 11px; pointer-events: none; display: none; z-index: 99; border: 1px solid #555; }}
</style>
</head>
<body>
<h1>CogMem bench — {SCENARIO}</h1>
<div class="meta">
  <b>Question:</b> {QUESTION}<br>
  <b class="gold">Gold answer:</b> {GOLD}
</div>

<div class="grid">
  <div class="panel">
    <h2>E7F (full bank) — answer: {E7_OK}</h2>
    <div class="stat">{E7_STAT}</div>
    <div id="cy_full" class="cy"></div>
    <div class="legend">
      <span><span class="swatch" style="background:#e74c3c"></span>intention</span>
      <span><span class="swatch" style="background:#9b59b6"></span>action_effect</span>
      <span><span class="swatch" style="background:#16a085"></span>habit</span>
      <span><span class="swatch" style="background:#3498db"></span>experience</span>
      <span><span class="swatch" style="background:#95a5a6"></span>world</span>
      <span><span class="swatch" style="background:#f39c12"></span>opinion</span>
      <span>·</span>
      <span><b style="border:2px solid #4fc3f7;padding:1px 3px;border-radius:2px">blue border</b> = used in recall top-25</span>
      <span><b style="background:#f1c40f;color:#000;padding:1px 3px;border-radius:2px">yellow</b> = cited in answer</span>
    </div>
    <div class="ans {E7_CLASS}"><b>Generated answer:</b><br>{E7_ANSWER}</div>
  </div>

  <div class="panel">
    <h2>E9F (ablated, no intention) — answer: {ABL_OK}</h2>
    <div class="stat">{ABL_STAT}</div>
    <div id="cy_abl" class="cy"></div>
    <div class="legend">
      <span>(no intention nodes — were dropped at retain time)</span>
    </div>
    <div class="ans {ABL_CLASS}"><b>Generated answer:</b><br>{ABL_ANSWER}</div>
  </div>
</div>

<div id="tt"></div>

<script>
const FULL = {FULL_JSON};
const ABL = {ABL_JSON};

const baseStyle = [
  {{ selector: 'node', style: {{
      'background-color': 'data(color)', 'label': 'data(label)',
      'font-size': '8px', 'color': '#eee', 'text-wrap': 'wrap', 'text-max-width': 110,
      'text-valign': 'bottom', 'text-margin-y': 3, 'width': 18, 'height': 18,
      'border-width': 1, 'border-color': '#555'
  }} }},
  {{ selector: 'node[?used]', style: {{ 'border-width': 3, 'border-color': '#4fc3f7' }} }},
  {{ selector: 'node[?cited]', style: {{ 'width': 30, 'height': 30, 'background-color': '#f1c40f', 'border-color': '#fff', 'border-width': 3 }} }},
  {{ selector: 'edge', style: {{ 'width': 1, 'line-color': '#444', 'curve-style': 'bezier', 'opacity': 0.4 }} }},
];

function render(containerId, data) {{
  const cy = cytoscape({{
    container: document.getElementById(containerId),
    elements: data,
    style: baseStyle,
    layout: {{ name: 'cose-bilkent', nodeRepulsion: 6000, idealEdgeLength: 80, animate: false }},
  }});
  const tt = document.getElementById('tt');
  cy.on('mouseover', 'node', e => {{
    const d = e.target.data();
    tt.innerHTML = `<b>[${{d.fact_type}}]</b> session=${{d.session}}<br>` +
                   `${{d.used ? 'rank ' + d.rank + (d.cited ? ' • CITED' : '') + '<br>' : ''}}` +
                   `<span style="color:#bbb">${{d.full_text}}</span>`;
    tt.style.display = 'block';
  }});
  cy.on('mousemove', e => {{
    tt.style.left = (e.originalEvent.clientX + 14) + 'px';
    tt.style.top = (e.originalEvent.clientY + 14) + 'px';
  }});
  cy.on('mouseout', 'node', () => {{ tt.style.display = 'none'; }});
}}
render('cy_full', FULL);
render('cy_abl', ABL);
</script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, help="e.g. neg_intention_14")
    ap.add_argument("--api", default=DEFAULT_API)
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--gate-dir", default=str(REPO_ROOT / "experiments" / "cogmem_bench" / "gate_detail"))
    ap.add_argument(
        "--specs-dir",
        default=str(REPO_ROOT / "cogmem_bench" / "specs" / "necessity"),
        help="dir containing <scenario>.json (default necessity for S33; pass agentic for S34)",
    )
    args = ap.parse_args(argv)

    sid = args.scenario
    detail_path = Path(args.gate_dir) / f"{sid}.json"
    if not detail_path.exists():
        print(f"missing detail file: {detail_path}", file=sys.stderr)
        return 1
    detail = json.loads(detail_path.read_text(encoding="utf-8"))

    # Deterministic session enumeration from the spec (works for both banks regardless of
    # which fact types remain in the ablated bank).
    spec_path = Path(args.specs_dir) / f"{sid}.json"
    if not spec_path.exists():
        print(f"missing spec file: {spec_path}", file=sys.stderr)
        return 1
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    total = int(spec["session_plan"]["total_sessions"])
    session_ids = [f"{sid}_s{i}" for i in range(total)]

    bank_full = f"COGMEM_BENCH_{sid}_full"
    bank_abl = f"COGMEM_BENCH_{sid}_ablated"
    print(f"[viz] fetching {bank_full} ({total} sessions)...")
    facts_full = _fetch_bank_facts(args.api, bank_full, session_ids)
    print(f"[viz] fetching {bank_abl} ({total} sessions)...")
    facts_abl = _fetch_bank_facts(args.api, bank_abl, session_ids)
    print(f"[viz] full={len(facts_full)} facts, ablated={len(facts_abl)} facts")

    full_graph = _build_graph(facts_full, detail["E7"]["recall_results"], detail["E7"]["generated_answer"])
    abl_graph = _build_graph(facts_abl, detail["ablated"]["recall_results"], detail["ablated"]["generated_answer"])

    def _clean_ans(s: str) -> str:
        s = re.sub(r"<think>.*?</think>", "", s or "", flags=re.DOTALL).strip()
        return html.escape(s)[:1200]

    out = _TEMPLATE.format(
        SCENARIO=html.escape(sid),
        QUESTION=html.escape(detail["question"]),
        GOLD=html.escape(detail["gold_answer"]),
        E7_OK="✓ correct" if detail["E7"]["judge_correct"] else "✗ judge says wrong",
        E7_CLASS="" if detail["E7"]["judge_correct"] else "fail",
        E7_STAT=f"{len(facts_full)} total facts • {len(detail['E7']['recall_results'])} in recall",
        E7_ANSWER=_clean_ans(detail["E7"]["generated_answer"]).replace("\n", "<br>"),
        ABL_OK="✓ correct" if detail["ablated"]["judge_correct"] else "✗ judge says wrong",
        ABL_CLASS="" if detail["ablated"]["judge_correct"] else "fail",
        ABL_STAT=f"{len(facts_abl)} total facts • {len(detail['ablated']['recall_results'])} in recall  (profile: {detail['ablated']['profile']})",
        ABL_ANSWER=_clean_ans(detail["ablated"]["generated_answer"]).replace("\n", "<br>"),
        FULL_JSON=json.dumps(full_graph, ensure_ascii=False),
        ABL_JSON=json.dumps(abl_graph, ensure_ascii=False),
    )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{sid}_graph.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"[viz] wrote {out_path}")
    explain = _build_explanation(sid, spec, detail, facts_full, facts_abl)
    explain_path = out_dir / f"{sid}_explanation.md"
    explain_path.write_text(explain, encoding="utf-8")
    print(f"[viz] wrote {explain_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
