"""OpenAI service for Tanishq jewelry chatbot — uses Titan AI Gateway."""
import os
from openai import OpenAI

_client = None
OPENAI_AVAILABLE = False

SYSTEM_PROMPT = """You are Tanishq's luxury jewelry consultant — warm, knowledgeable, and elegant.
Help customers discover the perfect piece. Ask about occasion, style preference,
budget, and who the piece is for. Keep responses concise (2-3 sentences max).
Never mention competitors. Use a refined, friendly tone."""


def init():
    global _client, OPENAI_AVAILABLE
    # Try Titan AI Gateway first
    gateway = os.getenv("AI_GATEWAY", "")
    titan_key = os.getenv("TITAN_AI_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    if gateway and titan_key:
        try:
            _client = OpenAI(api_key=titan_key, base_url=gateway)
            OPENAI_AVAILABLE = True
            print(f"  [AI] Connected to Titan AI Gateway: {gateway}")
            return
        except Exception as e:
            print(f"  [AI] Titan Gateway init failed: {e}")

    # Fallback to direct OpenAI key
    if openai_key and not openai_key.startswith("sk-your"):
        try:
            _client = OpenAI(api_key=openai_key)
            OPENAI_AVAILABLE = True
            print("  [AI] Connected to OpenAI directly")
        except Exception:
            OPENAI_AVAILABLE = False
    else:
        print("  [AI] No AI key configured — using local fallback responses")


def chat(messages: list[dict], **kwargs) -> str | None:
    """Call OpenAI chat completions. Returns None if unavailable."""
    if not OPENAI_AVAILABLE or _client is None:
        return None
    try:
        resp = _client.chat.completions.create(
            model="azure/gpt-5-nano",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
            **kwargs,
        )
        return resp.choices[0].message.content
    except Exception:
        return None


def generate_response(user_message: str, conversation_history: list[dict] | None = None) -> str | None:
    """Generate a conversational response for the jewelry chatbot."""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        msgs.extend(conversation_history)
    msgs.append({"role": "user", "content": user_message})
    return chat(msgs)


def generate_recommendation_intro(user_message: str, constraints: dict, count: int) -> str | None:
    """Generate a natural intro for recommendations."""
    prompt = f"""The customer said: "{user_message}"
Their preferences: {constraints}
We found {count} matching pieces. Write a brief, elegant 1-2 sentence intro
to present these recommendations. Do not list the products."""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
    return chat(msgs)
