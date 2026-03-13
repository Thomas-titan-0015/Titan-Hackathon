"""Preference Agent – personalised recommendations for returning users."""
from sqlalchemy.orm import Session as DBSession
from app.models.models import Preference, Item


def get_recommendations(user_id: int, db: DBSession, limit: int = 5) -> list[dict]:
    pref = db.query(Preference).filter(Preference.user_id == user_id).first()
    if not pref:
        return []

    liked_cats = pref.categories or []
    liked_styles = pref.styles or []
    past_likes = pref.past_likes or []

    query = db.query(Item).filter(Item.in_stock == 1)
    if liked_cats:
        preferred = query.filter(Item.category.in_(liked_cats)).all()
    else:
        preferred = query.all()

    scored = []
    for item in preferred:
        score = 0
        if item.category in liked_cats:
            score += 3
        attrs = item.attributes or {}
        if attrs.get("style") in liked_styles:
            score += 2
        if item.featured:
            score += 1
        if item.id not in past_likes:
            score += 1
        scored.append((score, item))

    scored.sort(key=lambda x: -x[0])
    results = []
    for score, item in scored[:limit]:
        reason = f"Based on your interest in {item.category}"
        if item.attributes and item.attributes.get("style") in liked_styles:
            reason += f" and {item.attributes['style']} style"
        results.append({
            "id": item.id, "name": item.name, "price": item.price,
            "image_url": item.image_url, "reason": reason,
        })
    return results
