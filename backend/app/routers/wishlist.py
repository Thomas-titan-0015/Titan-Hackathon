from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import WishlistItem, Item, User
from app.schemas.schemas import WishlistAddRequest, WishlistItemOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("", response_model=List[WishlistItemOut])
def get_wishlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WishlistItem).filter(WishlistItem.user_id == user.id).all()


@router.post("", response_model=WishlistItemOut)
def add_to_wishlist(body: WishlistAddRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == body.item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == user.id, WishlistItem.item_id == body.item_id
    ).first()
    if existing:
        raise HTTPException(409, "Already in wishlist")

    wi = WishlistItem(user_id=user.id, item_id=body.item_id)
    db.add(wi)
    db.commit()
    db.refresh(wi)
    return wi


@router.delete("/{wishlist_item_id}")
def remove_from_wishlist(wishlist_item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wi = db.query(WishlistItem).filter(WishlistItem.id == wishlist_item_id, WishlistItem.user_id == user.id).first()
    if not wi:
        raise HTTPException(404, "Wishlist item not found")
    db.delete(wi)
    db.commit()
    return {"ok": True}
