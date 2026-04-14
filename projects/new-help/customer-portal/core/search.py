from pathlib import Path
from thefuzz import process

DOCS_DIR = Path("data/docs")

def _build_index() -> dict[str, str]:
    """Build a {title: content} index from all .md files."""
    index = {}
    if DOCS_DIR.exists():
        for md_file in DOCS_DIR.rglob("*.md"):
            title = md_file.stem.replace("-", " ").replace("_", " ").title()
            index[title] = md_file.read_text(encoding="utf-8")
    return index

def search(query: str, top_n: int = 5) -> list[dict]:
    """Fuzzy search across documentation titles. Returns list of {title, score, snippet}."""
    index = _build_index()
    if not index or not query.strip():
        return []

    results = process.extract(query, list(index.keys()), limit=top_n)
    hits = []
    for title, score in results:
        if score >= 40:
            snippet = index[title][:200].replace("\n", " ")
            hits.append({"title": title, "score": score, "snippet": snippet})
    return hits
