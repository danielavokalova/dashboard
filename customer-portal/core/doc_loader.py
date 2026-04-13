"""
doc_loader.py
─────────────
Loads Markdown documentation from data/docs/ into memory.
Each .md file becomes a searchable article.

Future upgrade path:
  Replace the local file scan with a GitBook API call:
  GET https://api.gitbook.com/v1/spaces/{spaceId}/content
"""

from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass, field

DOCS_ROOT = Path(__file__).parent.parent / "data" / "docs"

# Category → icon mapping (mirrors GOL IBE sidebar)
CATEGORY_META: dict[str, dict] = {
    "agency":            {"icon": "🏢", "label": "Agency"},
    "dealers":           {"icon": "🤝", "label": "Dealers"},
    "customers":         {"icon": "👤", "label": "Customers"},
    "reservations":      {"icon": "🎫", "label": "Reservations"},
    "prices":            {"icon": "💰", "label": "Prices & Markup"},
    "code-lists":        {"icon": "📋", "label": "Code Lists"},
    "users":             {"icon": "👥", "label": "Users"},
    "notifications":     {"icon": "🔔", "label": "Notifications"},
    "supporting-texts":  {"icon": "📄", "label": "Supporting Texts"},
    "statistics":        {"icon": "📈", "label": "Statistics"},
    "settings":          {"icon": "⚙️",  "label": "Settings"},
}


@dataclass
class Article:
    id: str                      # e.g. "users/reset-password"
    category: str                # folder name under data/docs/
    title: str
    summary: str                 # first non-empty line after the heading
    body: str                    # full Markdown content
    tags: list[str] = field(default_factory=list)

    @property
    def icon(self) -> str:
        return CATEGORY_META.get(self.category, {}).get("icon", "📄")

    @property
    def category_label(self) -> str:
        return CATEGORY_META.get(self.category, {}).get("label", self.category.title())


def load_all_articles() -> list[Article]:
    """Walk data/docs/** and parse every .md file into an Article."""
    articles: list[Article] = []

    for cat_dir in sorted(DOCS_ROOT.iterdir()):
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name

        for md_file in sorted(cat_dir.glob("*.md")):
            raw = md_file.read_text(encoding="utf-8")
            lines = raw.splitlines()

            # Extract title from first H1
            title = md_file.stem.replace("-", " ").title()
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            # Extract summary (first paragraph after heading)
            summary = ""
            in_body = False
            for line in lines:
                if line.startswith("# "):
                    in_body = True
                    continue
                if in_body and line.strip():
                    summary = line.strip()
                    break

            # Simple tag extraction from front-matter-style comment <!-- tags: x,y,z -->
            tags: list[str] = []
            for line in lines:
                if line.startswith("<!-- tags:"):
                    tags = [t.strip() for t in line[10:].rstrip("-->").split(",")]

            articles.append(
                Article(
                    id=f"{category}/{md_file.stem}",
                    category=category,
                    title=title,
                    summary=summary or f"Learn about {title.lower()}.",
                    body=raw,
                    tags=tags,
                )
            )

    return articles


# Module-level cache – loaded once per Streamlit session
_cache: list[Article] | None = None


def get_articles() -> list[Article]:
    global _cache
    if _cache is None:
        _cache = load_all_articles()
    return _cache
