"""
ai_agent.py
───────────
AI Support Agent – answers user questions in natural language using
the GOL IBE knowledge base as context.

Model: Claude claude-sonnet-4-6 (fast, cost-effective for support use cases)

Usage:
    from core.ai_agent import ask_agent
    response = ask_agent("How do I reset a user's password?", history=[])

Integration note for IT:
  - Set ANTHROPIC_API_KEY in .env
  - Knowledge base context is injected automatically from data/docs/
  - `history` is a list of {"role": "user"|"assistant", "content": "..."} dicts
    (standard Anthropic messages format – pass st.session_state.messages directly)
"""

from __future__ import annotations
import os
from anthropic import Anthropic
from core.search import omnisearch_results

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example → .env and add your key."
            )
        _client = Anthropic(api_key=api_key)
    return _client


SYSTEM_PROMPT = """You are the GOL IBE Help Assistant – a friendly, expert support agent
for the GOL IBE Admin Console used by travel agencies.

Your role:
- Answer questions about the GOL IBE backoffice system clearly and concisely.
- Use the knowledge base excerpts provided in the user's message when relevant.
- If a step-by-step guide is needed, format it as a numbered list.
- Keep responses short – max 3 key points unless the user explicitly asks for more detail.
- If you are unsure, say so honestly and suggest contacting the support team.
- Always reply in the same language the user writes in.
- Never invent features or settings that don't exist in GOL IBE.

Tone: professional but warm, like a knowledgeable colleague – not a robot."""


def ask_agent(
    user_message: str,
    history: list[dict],
    inject_docs: bool = True,
) -> str:
    """
    Send a message to the AI agent and return its response as a string.

    Args:
        user_message:  The user's latest question.
        history:       Previous conversation turns (role/content dicts).
        inject_docs:   If True, prepend relevant knowledge base snippets
                       to the user message as context.
    """
    client = _get_client()

    # Enrich user message with relevant doc snippets
    context_block = ""
    if inject_docs:
        results = omnisearch_results(user_message, top_n=3)
        if results:
            snippets = "\n\n".join(
                f"[{r['category']} / {r['title']}]\n{r['summary']}"
                for r in results
            )
            context_block = (
                f"\n\n---\nRelevant documentation (use as context):\n{snippets}\n---"
            )

    enriched_message = user_message + context_block

    messages = history + [{"role": "user", "content": enriched_message}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text
