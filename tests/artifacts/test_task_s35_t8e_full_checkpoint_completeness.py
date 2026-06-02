from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    checkpoint_dir = root / "experiments" / "v20_t8e_3bank" / "checkpoints"

    missing = []
    for idx in range(161):
        case_id = f"c{idx:03d}"
        path = checkpoint_dir / f"E7_full_{case_id}.json"
        if not path.exists():
            missing.append(path.name)

    if missing:
        raise SystemExit(
            "Missing full-eval checkpoints:\n" + "\n".join(missing)
        )

    print("All 161 E7 full checkpoints exist for v20_t8e_3bank.")


if __name__ == "__main__":
    main()
