from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    note = ROOT / "Node.txt"
    if not note.exists():
        raise AssertionError("Node.txt was not created")

    text = note.read_text(encoding="utf-8")
    required = [
        "uv sync",
        "uv run cogmem-api",
        ".\\scripts\\docker.ps1 -Mode embedded",
        "docker/docker-compose/external-pg/docker-compose.yaml",
        "Experiments.txt",
        "reports/final_reports/src/main.tex",
        "Do not casually rerun scripts/distill_dataset.py",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(f"Node.txt missing required runbook entries: {missing}")

    print("Node.txt runbook checks passed")


if __name__ == "__main__":
    main()
