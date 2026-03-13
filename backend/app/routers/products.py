from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.models.models import Item, Preference, User
from app.schemas.schemas import ProductOut
from app.auth import get_optional_user
import random

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Item)
    if category:
        q = q.filter(Item.category == category)
    if min_price is not None:
        q = q.filter(Item.price >= min_price)
    if max_price is not None:
        q = q.filter(Item.price <= max_price)
    if featured:
        q = q.filter(Item.featured == 1)
    if search:
        q = q.filter(Item.name.ilike(f"%{search}%"))
    return q.all()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Item.category).distinct().all()
    return [c[0] for c in cats]


@router.get("/popup-recommendations", response_model=List[ProductOut])
def popup_recommendations(
    categories: Optional[str] = None,
    exclude: Optional[str] = None,
    limit: int = 3,
    db: Session = Depends(get_db),
):
    """Return AI-style popup product recommendations.
    categories: comma-separated list of categories the user has been browsing.
    exclude: comma-separated product IDs to exclude (already shown).
    """
    q = db.query(Item).filter(Item.in_stock == 1)

    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cat_list:
            q = q.filter(Item.category.in_(cat_list))

    exclude_ids = []
    if exclude:
        exclude_ids = [int(x) for x in exclude.split(",") if x.strip().isdigit()]
    if exclude_ids:
        q = q.filter(~Item.id.in_(exclude_ids))

    items = q.all()
    # Weighted random: featured items get 3x weight
    if len(items) > limit:
        weights = [3.0 if it.featured else 1.0 for it in items]
        items = random.choices(items, weights=weights, k=min(limit, len(items)))
    return items[:limit]


@router.get("/personalized-categories")
def personalized_categories(user: Optional[User] = Depends(get_optional_user), db: Session = Depends(get_db)):
    """Return categories ordered by user preference. Preferred categories first, then the rest."""
    all_cats = [c[0] for c in db.query(Item.category).distinct().all()]
    if not user:
        return all_cats

    pref = db.query(Preference).filter(Preference.user_id == user.id).first()
    if not pref or not pref.categories:
        return all_cats

    # Put preferred categories first, then remaining in original order
    preferred = [c for c in pref.categories if c in all_cats]
    remaining = [c for c in all_cats if c not in preferred]
    return preferred + remaining


@router.get("/{item_id}", response_model=ProductOut)
def get_product(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item
