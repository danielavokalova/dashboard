from pathlib import Path

DOCS_DIR = Path("data/docs")

def load_docs(max_chars: int = 12000) -> str:
    """Load all .md files from data/docs/ subdirectories into a single string."""
    if not DOCS_DIR.exists():
        return ""

    parts = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        section = md_file.stem.replace("-", " ").replace("_", " ").title()
        parts.append(f"## {section}\n{md_file.read_text(encoding='utf-8')}")

    combined = "\n\n".join(parts)
    return combined[:max_chars] if len(combined) > max_chars else combined
