"""
search.py
─────────
Omnisearch – instant keyword search across the knowledge base.
Uses rapidfuzz for fuzzy matching (no GPU / model required).

Future upgrade:
  Replace score_article() with a semantic similarity call via
  sentence-transformers embeddings stored in a FAISS index.
"""

from __future__ import annotations
from rapidfuzz import fuzz
from core.doc_loader import get_articles, Article

# Minimum similarity score (0–100) to include a result
THRESHOLD = 45


def _score_article(article: Article, query: str) -> float:
    q = query.lower()
    title_score   = fuzz.partial_ratio(q, article.title.lower())
    summary_score = fuzz.partial_ratio(q, article.summary.lower())
    tag_score     = max((fuzz.ratio(q, t.lower()) for t in article.tags), default=0)
    body_score    = fuzz.partial_ratio(q, article.body[:500].lower())  # first 500 chars only
    return max(title_score, summary_score, tag_score * 0.9, body_score * 0.7)


def omnisearch_results(query: str, top_n: int = 8) -> list[dict]:
    """
    Return up to `top_n` articles matching `query`, ranked by relevance.

    Each result dict contains:
        icon, title, category, summary, page_link, score
    """
    if not query or len(query) < 2:
        return []

    articles = get_articles()
    scored = [
        (article, _score_article(article, query))
        for article in articles
    ]
    scored = [(a, s) for a, s in scored if s >= THRESHOLD]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        {
            "icon":      a.icon,
            "title":     a.title,
            "category":  a.category_label,
            "summary":   a.summary,
            "page_link": "pages/2_Walkthroughs.py",  # TODO: deep-link to article
            "score":     round(s, 1),
        }
        for a, s in scored[:top_n]
    ]
