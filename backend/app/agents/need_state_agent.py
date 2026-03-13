"""Need-State Agent – conversational flow for new users (jewelry)."""
import re
from app.services import openai_service

CATEGORY_KEYWORDS = {
    "ring": "Rings", "rings": "Rings", "engagement": "Rings", "wedding band": "Rings",
    "necklace": "Necklaces", "necklaces": "Necklaces", "chain": "Necklaces",
    "earring": "Earrings", "earrings": "Earrings", "stud": "Earrings", "hoop": "Earrings",
    "bracelet": "Bracelets", "bracelets": "Bracelets", "tennis bracelet": "Bracelets",
    "pendant": "Pendants", "pendants": "Pendants", "locket": "Pendants",
    "watch": "Watches", "watches": "Watches", "timepiece": "Watches",
    "bangle": "Bangles", "bangles": "Bangles", "kada": "Bangles",
}

STYLE_KEYWORDS = {
    "classic": "classic", "traditional": "classic", "timeless": "classic",
    "modern": "modern", "contemporary": "modern", "minimalist": "modern",
    "vintage": "vintage", "antique": "vintage", "retro": "vintage",
    "statement": "statement", "bold": "statement", "luxe": "statement",
    "delicate": "delicate", "dainty": "delicate", "subtle": "delicate",
}

FALLBACK_QUESTIONS = {
    "category": "What type of jewelry are you looking for? (e.g., rings, necklaces, earrings, bracelets, watches, pendants, bangles)",
    "max_price": "Do you have a budget in mind? (e.g., under \u20b950,000)",
    "style": "Any style preference? (e.g., classic, modern, vintage, statement, delicate)",
}


def parse_constraints(message: str) -> dict:
    msg = message.lower()
    constraints = {}

    for kw, cat in CATEGORY_KEYWORDS.items():
        if kw in msg:
            constraints["category"] = cat
            break

    price_match = re.search(r'(?:under|below|max|budget|less than|up to)\s*[$₹]?\s*(\d[\d,]*)', msg)
    if price_match:
        constraints["max_price"] = float(price_match.group(1).replace(",", ""))
    else:
        price_match2 = re.search(r'[$₹](\d[\d,]*)', msg)
        if price_match2:
            constraints["max_price"] = float(price_match2.group(1).replace(",", ""))

    for kw, style in STYLE_KEYWORDS.items():
        if kw in msg:
            constraints["style"] = style
            break

    return constraints


OCCASION_KEYWORDS = {
    "birthday": "birthday", "anniversary": "anniversary", "wedding": "wedding",
    "engagement": "engagement", "gift": "gift", "self": "self",
    "valentine": "valentine", "diwali": "festival", "festival": "festival",
    "party": "party", "everyday": "everyday", "office": "everyday", "daily": "everyday",
}

GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "namaste"]

GENERAL_QUERIES = {
    "return": "We offer a hassle-free 30-day return policy on all pieces. Would you like to explore some jewelry today?",
    "shipping": "We provide free insured shipping across India! Delivery typically takes 3-5 business days. What kind of jewelry are you looking for?",
    "delivery": "Standard delivery takes 3-5 business days, and it's completely free and insured! Can I help you find something special?",
    "exchange": "Exchanges can be done within 30 days of purchase. Just visit any Tanishq store or contact us. Would you like to browse our new collection?",
    "warranty": "All Tanishq pieces come with a certificate of authenticity and lifetime maintenance warranty. How can I help you find the perfect piece?",
    "price": "Our collection ranges from affordable everyday pieces to premium luxury jewelry. Do you have a budget in mind?",
    "gold": "We have a beautiful range of gold jewelry — from 18K to 24K options. Would you like to explore rings, necklaces, or bracelets?",
    "diamond": "Our certified diamond collection includes solitaires, studded pieces, and cocktail rings. What kind of diamond piece interests you?",
    "silver": "While we primarily specialize in gold and diamond jewelry, we do have select sterling silver pieces. Want to see what we have?",
    "platinum": "Our platinum collection features elegant designs perfect for special occasions. Would you like to see rings or pendants?",
    "size": "For rings, we offer sizes 4-13. For bracelets and bangles, we have standard sizing. Would you like help finding the right fit?",
    "customize": "Yes, many of our pieces can be customized! You can choose metal type, stone settings, and engravings. What did you have in mind?",
    "store": "You can find Tanishq stores across India. Visit tanishq.co.in/stores for the nearest location. Can I help you with online shopping today?",
}


def _detect_general_query(msg: str) -> str | None:
    """Check if the message is a general/FAQ query rather than a shopping intent."""
    for keyword, response in GENERAL_QUERIES.items():
        if keyword in msg:
            return response
    return None


def _detect_greeting(msg: str) -> bool:
    return any(g in msg.split() or msg.startswith(g) for g in GREETINGS)


def _build_natural_response(message: str, new_constraints: dict, collected: dict) -> str:
    """Build a natural, contextual response based on what the user said and what we've collected."""
    msg = message.lower()

    # Greetings
    if _detect_greeting(msg):
        return "Hello! Welcome to Tanishq. I'd love to help you find the perfect piece of jewelry. Are you looking for something specific, or would you like me to guide you?"

    # General queries
    general = _detect_general_query(msg)
    if general:
        return general

    # Thank-you responses
    if any(w in msg for w in ["thank", "thanks", "thx"]):
        return "You're welcome! Is there anything else I can help you with today?"

    # Detect occasion
    occasion = None
    for kw, occ in OCCASION_KEYWORDS.items():
        if kw in msg:
            occasion = occ
            break

    parts = []

    # Acknowledge what user just told us
    if "category" in new_constraints:
        cat = new_constraints["category"]
        if occasion:
            parts.append(f"Great choice! {cat} are perfect for {occasion} celebrations.")
        else:
            parts.append(f"Lovely! We have a stunning collection of {cat}.")
    elif "max_price" in new_constraints:
        budget = new_constraints["max_price"]
        parts.append(f"Got it — I'll find beautiful options within ₹{budget:,.0f}.")
    elif "style" in new_constraints:
        style = new_constraints["style"]
        parts.append(f"A {style} style — excellent taste!")
    elif occasion:
        parts.append(f"How wonderful! Finding the perfect piece for {occasion} is what we do best.")

    # Ask the next missing thing naturally
    if "category" not in collected:
        parts.append("What type of jewelry catches your eye? We have rings, necklaces, earrings, bracelets, watches, pendants, and bangles.")
    elif "max_price" not in collected:
        parts.append("Do you have a budget range in mind? This helps me find the best options for you.")
    elif "style" not in collected:
        parts.append("Any particular style you prefer? Classic, modern, vintage, statement, or delicate?")

    return " ".join(parts) if parts else "I'd love to help! Could you tell me a bit more about what you're looking for?"


def next_question(collected: dict) -> str | None:
    if "category" not in collected:
        return FALLBACK_QUESTIONS["category"]
    if "max_price" not in collected:
        return FALLBACK_QUESTIONS["max_price"]
    if "style" not in collected:
        return FALLBACK_QUESTIONS["style"]
    return None


def process_message(message: str, conversation_constraints: dict, history: list[dict] | None = None) -> dict:
    new_constraints = parse_constraints(message)
    merged = {**conversation_constraints, **new_constraints}

    question = next_question(merged)
    if question:
        # Try OpenAI first for the most natural response
        ai_response = None
        if openai_service.OPENAI_AVAILABLE and history:
            ai_response = openai_service.generate_response(message, history)
        # Fall back to our smart local response builder
        text = ai_response if ai_response else _build_natural_response(message, new_constraints, merged)
        return {"text": text, "constraints": merged, "ready": False}

    return {
        "text": "Wonderful! Let me curate the perfect pieces for you.",
        "constraints": merged,
        "ready": True,
    }
