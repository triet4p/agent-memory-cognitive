from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METHODOLOGY = ROOT / "reports" / "final_reports" / "src" / "Chapter" / "3_Methodology.tex"
SUMMARY = ROOT / "logs" / "task_report_ch3_methodology_summary.md"


EXPECTED_SECTIONS = [
    "Tổng quan hệ thống bộ nhớ CogMem",
    "Kiến trúc xử lý ba pipeline của CogMem",
    "Đồ thị bộ nhớ kế thừa nhận thức",
    "Biểu diễn kép: ghi nhớ tóm tắt và dấu vết nguyên văn",
    "Truy vấn đa kênh và kết hợp bằng chứng",
    "Truy vấn đồ thị tích lũy và bảo vệ chu trình",
    "Định tuyến truy vấn thích ứng",
    "Tổng hợp câu trả lời có căn cứ",
]

EXPECTED_LABELS = [
    "fig:ch3_pipeline_overview",
    "fig:ch3_six_networks",
    "tab:node_schemas",
    "fig:ch4_habit_diary_workload",
    "fig:ch4_habit_memory",
    "tab:intention_lifecycle",
    "fig:ch4_intention_lifecycle",
    "fig:ch4_agentic_action_effect_trace",
    "fig:ch4_tec_network",
    "fig:ch3_sr_vs_ao",
    "fig:ch3_edge_types",
    "fig:ch3_two_layer_schema",
    "fig:ch4_fuzzy_trace",
    "fig:ch4_episodic_buffer",
    "tab:max_vs_sum",
    "fig:ch3_cycle_guards",
    "tab:adaptive_rrf",
    "fig:ch3_adaptive_routing",
    "fig:ch4_attentional_selection",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_methodology_uses_expanded_pipeline_query_synthesis_outline() -> None:
    text = _read(METHODOLOGY)
    sections = re.findall(r"^\\section\{(.+?)\}", text, flags=re.MULTILINE)
    assert sections == EXPECTED_SECTIONS, sections

    assert "Đóng góp 1" not in text
    assert "Đóng góp 2" not in text
    assert "Đóng góp 3" not in text
    assert "Đóng góp 4" not in text
    assert "Phân tích cơ sở khoa học nhận thức" not in text
    assert ("luận " + "án") not in text
    assert ("truy " + "hồi") not in text


def test_methodology_preserves_visual_and_table_blocks() -> None:
    text = _read(METHODOLOGY)
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    for label in EXPECTED_LABELS:
        assert label in labels, f"missing label: {label}"

    assert text.count(r"\begin{figure}") >= 14, "expected moved figure blocks to remain present"
    assert text.count(r"\begin{table}") >= 4, "expected moved table blocks to remain present"
    assert "Images/cogmem_pipeline_overview.png" in text
    assert "Images/cogmem_memory_graph.png" in text
    assert "Images/habit_diary_workload.png" in text
    assert "Images/agentic_action_effect_trace.png" in text


def test_reader_friendly_intention_and_routing_explanations() -> None:
    text = _read(METHODOLOGY)
    for phrase in [
        "planning}: kế hoạch đang tồn tại",
        "fulfilled}: kế hoạch đã được thực hiện",
        "abandoned}: kế hoạch đã bị hủy",
        "không phải một liên kết transition riêng",
        "Attentional Selection",
        "Câu hỏi ``khi nào''",
        "câu hỏi ``vì sao''",
    ]:
        assert phrase in text, f"missing explanatory phrase: {phrase}"


def test_first_time_reader_terms_are_explained_in_place() -> None:
    text = _read(METHODOLOGY)
    required_explanations = [
        "mỗi \\textit{fact} là một đơn vị thông tin",
        "Ba yêu cầu trên không được giải quyết bằng một cơ chế duy nhất",
        "Riêng yêu cầu về bằng chứng được xử lý bằng một quyết định khác",
        "ba luồng xử lý chính, mỗi luồng là một chuỗi bước nối tiếp nhau",
        "bốn kênh truy vấn song song",
        "Kênh ngữ nghĩa",
        "Kênh từ khóa BM25",
        "Kênh đồ thị",
        "Kênh thời gian",
        "Pipeline tổng hợp",
        "Vector nhúng là dạng biểu diễn bằng số của ý nghĩa câu",
        "Benchmark là bộ dữ liệu đánh giá",
        "raw\\_snippet} được giữ như bằng chứng nguyên văn",
        "prompt sinh câu trả lời để làm ngữ cảnh đầu vào",
        "đồ thị bộ nhớ dị thể, nơi nhiều loại đơn vị thông tin",
        "Các trường bổ sung này ghi những chi tiết",
        "LLM là mô hình ngôn ngữ lớn",
        "S-R là viết tắt của stimulus-response",
        "A-O là viết tắt của action-outcome",
        "schema hai lớp, một cấu trúc trường dữ liệu",
        "Lớp nguyên văn tạo grounding",
        "MAX, chỉ giữ đường có điểm cao nhất",
        "Episodic Buffer đóng vai trò như vùng làm việc tạm thời",
        "Với SUM, nhiều đường bằng chứng cùng được cộng",
        "gặp chu trình: đường đi theo các liên kết",
        "hạn mức kích hoạt",
        "ngưỡng bão hòa",
        "BM25 hữu ích khi câu hỏi chứa tên riêng",
        "RRF, cộng điểm theo thứ hạng",
        "không có đủ ký ức đã truy vấn",
    ]
    for phrase in required_explanations:
        assert phrase in text, f"missing in-place explanation: {phrase}"


def test_code_jargon_was_reduced_in_prose() -> None:
    text = _read(METHODOLOGY)
    for banned in [
        "re-typed",
        "ping-pong",
        "ping pong",
        "equal-weight fusion",
        "2-layer node schema",
        "Implementation hiện tại",
    ]:
        assert banned not in text, f"code-ish term leaked: {banned}"

    prose_only = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", text, flags=re.DOTALL)
    assert " node " not in prose_only.lower(), "English 'node' should not appear in prose"


def test_required_task_artifact_exists() -> None:
    assert SUMMARY.exists(), "missing required task summary log"
    summary = _read(SUMMARY)
    assert "3_Methodology.tex" in summary
    assert "Coverage Gate" in summary


def main() -> None:
    test_methodology_uses_expanded_pipeline_query_synthesis_outline()
    test_methodology_preserves_visual_and_table_blocks()
    test_reader_friendly_intention_and_routing_explanations()
    test_first_time_reader_terms_are_explained_in_place()
    test_code_jargon_was_reduced_in_prose()
    test_required_task_artifact_exists()
    print("task_report_ch3_methodology checks passed")


if __name__ == "__main__":
    main()
