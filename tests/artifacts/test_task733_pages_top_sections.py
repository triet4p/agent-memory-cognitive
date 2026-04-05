from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    mkdocs_path = repo_root / "mkdocs.yml"
    readme_path = repo_root / "README.md"
    idea_path = repo_root / "docs" / "CogMem-Idea.md"
    plan_path = repo_root / "docs" / "PLAN.md"
    wrapper_readme_path = repo_root / "tutorials" / "project-overview.md"
    wrapper_idea_path = repo_root / "tutorials" / "idea.md"
    wrapper_plan_path = repo_root / "tutorials" / "plan.md"

    assert mkdocs_path.exists(), "Missing mkdocs.yml"
    assert readme_path.exists(), "Missing README.md"
    assert idea_path.exists(), "Missing docs/CogMem-Idea.md"
    assert plan_path.exists(), "Missing docs/PLAN.md"
    assert wrapper_readme_path.exists(), "Missing tutorials/project-overview.md"
    assert wrapper_idea_path.exists(), "Missing tutorials/idea.md"
    assert wrapper_plan_path.exists(), "Missing tutorials/plan.md"

    mkdocs_text = mkdocs_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")
    wrapper_readme_text = wrapper_readme_path.read_text(encoding="utf-8")
    wrapper_idea_text = wrapper_idea_path.read_text(encoding="utf-8")
    wrapper_plan_text = wrapper_plan_path.read_text(encoding="utf-8")

    assert "docs_dir: tutorials" in mkdocs_text
    assert "- Dự án tổng quan: project-overview.md" in mkdocs_text
    assert "- Idea: idea.md" in mkdocs_text
    assert "- Plan: plan.md" in mkdocs_text
    assert "- Tutorials:" in mkdocs_text
    assert "- include-markdown" in mkdocs_text

    assert "../README.md" in wrapper_readme_text
    assert "../docs/CogMem-Idea.md" in wrapper_idea_text
    assert "../docs/PLAN.md" in wrapper_plan_text

    assert "## 4 mục lớn trên GitHub Pages" in readme_text
    assert "docs/CogMem-Idea.md" in readme_text
    assert "docs/PLAN.md" in readme_text
    assert "tutorials/INDEX.md" in readme_text

    print("Task 733 pages top sections checks passed.")


if __name__ == "__main__":
    main()
