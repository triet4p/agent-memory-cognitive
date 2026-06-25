from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "docs" / "slides" / "DATN_Proposal - Copy.pptx"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def _slide_text(zip_file: zipfile.ZipFile, slide_no: int) -> str:
    root = ET.fromstring(zip_file.read(f"ppt/slides/slide{slide_no}.xml"))
    return "\n".join(node.text or "" for node in root.findall(".//a:t", NS))


def main() -> None:
    assert PPTX.exists(), f"missing deck: {PPTX}"
    with zipfile.ZipFile(PPTX) as zip_file:
        intention = _slide_text(zip_file, 13)
        assert "Question: What sustainability habit" in intention
        assert "Gold answer: Composting" in intention
        assert "FULL BANK: gold representation exists" in intention
        assert "[intention] plans to start composting" in intention
        assert "[1] keeps meaning to compost" in intention
        assert "ABLATED BANK: gold representation removed" in intention
        assert "Missing component: no node says" in intention
        assert "[experience] rain barrel / rainwater garden" in intention
        assert "Discrimination claim: the gold answer exists only as typed intention facts" in intention
        assert "Speaker cue:" not in intention

        action_effect = _slide_text(zip_file, 14)
        assert "Question: What does the agent do when Stripe returns HTTP 429" in action_effect
        assert "Gold: backoff, sleep, then 200" in action_effect
        assert "FULL BANK: causal triple is explicit" in action_effect
        assert "precondition: HTTP 429 + Retry-After ignored" in action_effect
        assert "action: respect Retry-After + exponential backoff" in action_effect
        assert "outcome: subsequent calls return 200" in action_effect
        assert "ABLATED BANK: causal bridge is missing" in action_effect
        assert "Missing component: no typed link from condition -> action -> 200 outcome" in action_effect
        assert "Discrimination claim: action_effect stores the executable causal chain" in action_effect
        assert "Speaker cue:" not in action_effect

    print("task_s44_datn_proposal_experiment_extraction artifact checks passed")


if __name__ == "__main__":
    main()
