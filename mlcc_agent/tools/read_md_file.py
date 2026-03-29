"""Tool for reading markdown reference files bundled with skills.

This tool allows the agent to read .md files from the skills/
directory at runtime, enabling the progressive-disclosure pattern
where SKILL.md points to detailed references that are loaded on demand.
"""

import os
from pathlib import Path

# Base directory: project root (one level above mlcc_agent/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SKILLS_DIR = _PROJECT_ROOT / "skills"

# Allowed directories the agent may read from
_ALLOWED_ROOTS = [
    _SKILLS_DIR,
    _PROJECT_ROOT,  # for top-level docs like mlcc_catalog_rag_master_ko.md
]


def read_md_file(file_path: str) -> dict:
    """Read a markdown (.md) reference file from the project.

    Use this tool when the skill instructions say
    "Read references/some-file.md" or when you need detailed
    code maps, workflow rules, prompt examples, or filtering logic
    that are stored in separate reference files.

    Supported path formats:
      - Relative to a skill:
          "skills/mlcc-rag-spec-selector/references/catalog-codebook.md"
          "skills/mlcc-optimal-design-doe/references/workflow-details.md"
      - Relative to project root:
          "mlcc_catalog_rag_master_ko.md"
          "rag문서 설명 및 실제 워크플로우 가이드.md"
      - Just the filename (will search inside skills/):
          "catalog-codebook.md"

    Args:
        file_path: Path to the markdown file to read.

    Returns:
        A dict with 'status', 'file_path', and 'content' on success,
        or 'status' and 'error' on failure.
    """
    resolved = _resolve_path(file_path)

    if resolved is None:
        return {
            "status": "error",
            "error": (
                f"File not found: '{file_path}'. "
                "Provide a path relative to the project root "
                "(e.g. 'skills/mlcc-rag-spec-selector/references/catalog-codebook.md') "
                "or just the filename (e.g. 'catalog-codebook.md')."
            ),
        }

    if not _is_allowed(resolved):
        return {
            "status": "error",
            "error": f"Access denied: '{resolved}' is outside the allowed project directories.",
        }

    if resolved.suffix.lower() not in (".md", ".txt", ".yaml", ".yml", ".json", ".jsonl"):
        return {
            "status": "error",
            "error": f"Unsupported file type: '{resolved.suffix}'. Only .md, .txt, .yaml, .json, .jsonl files are allowed.",
        }

    try:
        content = resolved.read_text(encoding="utf-8")
        return {
            "status": "success",
            "file_path": str(resolved.relative_to(_PROJECT_ROOT)),
            "content": content,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to read file: {e}",
        }


def _resolve_path(file_path: str) -> Path | None:
    """Try multiple strategies to find the file."""
    p = Path(file_path)

    # 1. Absolute path
    if p.is_absolute() and p.is_file():
        return p.resolve()

    # 2. Relative to project root
    candidate = _PROJECT_ROOT / p
    if candidate.is_file():
        return candidate.resolve()

    # 3. Bare filename -> search recursively under skills/
    if not p.parts[:-1]:  # just a filename, no directory component
        for match in _SKILLS_DIR.rglob(p.name):
            if match.is_file():
                return match.resolve()

    return None


def _is_allowed(resolved: Path) -> bool:
    """Ensure the resolved path is inside an allowed root."""
    return any(
        resolved == root or root in resolved.parents
        for root in _ALLOWED_ROOTS
    )
