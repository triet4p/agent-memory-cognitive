from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    mkdocs_path = repo_root / "mkdocs.yml"
    req_docs_path = repo_root / "requirements-docs.txt"
    workflow_path = repo_root / ".github" / "workflows" / "tutorials-app-cicd.yml"

    assert mkdocs_path.exists(), "Missing mkdocs.yml"
    assert req_docs_path.exists(), "Missing requirements-docs.txt"
    assert workflow_path.exists(), "Missing .github/workflows/tutorials-app-cicd.yml"

    mkdocs_text = mkdocs_path.read_text(encoding="utf-8")
    req_docs_text = req_docs_path.read_text(encoding="utf-8")
    workflow_text = workflow_path.read_text(encoding="utf-8")

    # mkdocs app contract
    assert "docs_dir: tutorials" in mkdocs_text
    assert "site_dir: site" in mkdocs_text
    assert "Per-file reading order: per-file/READING-ORDER.md" in mkdocs_text
    assert "name: material" in mkdocs_text

    # docs requirements contract
    assert "mkdocs" in req_docs_text.lower()
    assert "mkdocs-material" in req_docs_text.lower()

    # workflow contract for master branch deploy
    assert "branches:" in workflow_text
    assert "- master" in workflow_text
    assert "mkdocs build --config-file mkdocs.yml --site-dir site" in workflow_text
    assert "actions/upload-pages-artifact@v3" in workflow_text
    assert "actions/deploy-pages@v4" in workflow_text

    print("Task 731 tutorials CI/CD app checks passed.")


if __name__ == "__main__":
    main()
