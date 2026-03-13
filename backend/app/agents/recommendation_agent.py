"""Recommendation Agent – scores products against constraints."""
from sqlalchemy.orm import Session as DBSession
from app.models.models import Item


def recommend(db: DBSession, constraints: dict | None = None, limit: int = 5) -> list[dict]:
    query = db.query(Item).filter(Item.in_stock == 1)

    if constraints:
        if "category" in constraints:
            query = query.filter(Item.category == constraints["category"])
        if "max_price" in constraints:
            query = query.filter(Item.price <= constraints["max_price"])

    items = query.all()

    scored = []
    for item in items:
        score = item.rating * 10
        if item.featured:
            score += 5
        if constraints and constraints.get("style"):
            attrs = item.attributes or {}
            if attrs.get("style") == constraints["style"]:
                score += 15
        scored.append((score, item))

    scored.sort(key=lambda x: -x[0])

    results = []
    for score, item in scored[:limit]:
        reason_parts = []
        if constraints:
            if "category" in constraints:
                reason_parts.append(f"Perfect {constraints['category'].lower()} choice")
            if "style" in constraints and (item.attributes or {}).get("style") == constraints["style"]:
                reason_parts.append(f"matches your {constraints['style']} style")
            if "max_price" in constraints:
                reason_parts.append("within your budget")
        if item.rating >= 4.5:
            reason_parts.append("highly rated")
        reason = " — ".join(reason_parts) if reason_parts else "Popular choice"

        results.append({
            "id": item.id, "name": item.name, "price": item.price,
            "image_url": item.image_url, "reason": reason,
        })
    return results
