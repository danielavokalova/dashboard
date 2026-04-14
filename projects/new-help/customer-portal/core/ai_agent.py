import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

SYSTEM_PROMPT = """You are a helpful support agent for Travelport's GOL IBE system.
You help travel agency employees navigate the ticket management and agency configuration system.
Answer questions clearly and in the context of the provided documentation.
If you don't know the answer, say so honestly and suggest contacting support.
Respond in the same language the user writes in."""

def get_response(user_query: str, docs: str, history: list[dict]) -> str:
    """Call Claude with user query + injected documentation context."""
    client = _get_client()

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    context_block = f"\n\n<documentation>\n{docs}\n</documentation>\n\n" if docs else ""
    messages.append({"role": "user", "content": f"{context_block}{user_query}"})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text if response.content else "No response."
