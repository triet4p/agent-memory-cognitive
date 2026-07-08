from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    path = ROOT / "reports/final_reports/DATN_TomTat_ThanhQua.md"
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    required = [
        "Mục tiêu",
        "CogMem",
        "31/35",
        "88,6%",
        "119/161",
        "73,9%",
        "CogMem Bench",
        "Điểm tôi đánh giá cao nhất",
        "khối lượng công việc",
    ]
    missing = [item for item in required if item.lower() not in lowered]
    if missing:
        raise AssertionError(f"summary is missing required content: {missing}")
    print("DATN summary attachment checks passed")


if __name__ == "__main__":
    main()
