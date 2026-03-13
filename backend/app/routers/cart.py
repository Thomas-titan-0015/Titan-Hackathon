from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import CartItem, Item, User
from app.schemas.schemas import CartAddRequest, CartItemOut
from app.auth import get_optional_user

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _get_guest_id(x_guest_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_guest_id


@router.get("", response_model=List[CartItemOut])
def get_cart(
    user: Optional[User] = Depends(get_optional_user),
    guest_id: Optional[str] = Depends(_get_guest_id),
    db: Session = Depends(get_db),
):
    if user:
        return db.query(CartItem).filter(CartItem.user_id == user.id).all()
    elif guest_id:
        return db.query(CartItem).filter(CartItem.session_id == guest_id).all()
    return []


@router.post("", response_model=CartItemOut)
def add_to_cart(
    body: CartAddRequest,
    user: Optional[User] = Depends(get_optional_user),
    guest_id: Optional[str] = Depends(_get_guest_id),
    db: Session = Depends(get_db),
):
    item = db.query(Item).filter(Item.id == body.item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    if user:
        existing = db.query(CartItem).filter(
            CartItem.user_id == user.id, CartItem.item_id == body.item_id
        ).first()
        if existing:
            existing.quantity += body.quantity
            db.commit()
            db.refresh(existing)
            return existing
        cart_item = CartItem(user_id=user.id, item_id=body.item_id, quantity=body.quantity)
    elif guest_id:
        existing = db.query(CartItem).filter(
            CartItem.session_id == guest_id, CartItem.item_id == body.item_id
        ).first()
        if existing:
            existing.quantity += body.quantity
            db.commit()
            db.refresh(existing)
            return existing
        cart_item = CartItem(session_id=guest_id, item_id=body.item_id, quantity=body.quantity)
    else:
        raise HTTPException(400, "Login or provide a guest session ID")

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    user: Optional[User] = Depends(get_optional_user),
    guest_id: Optional[str] = Depends(_get_guest_id),
    db: Session = Depends(get_db),
):
    if user:
        ci = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == user.id).first()
    elif guest_id:
        ci = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.session_id == guest_id).first()
    else:
        raise HTTPException(400, "Login or provide a guest session ID")

    if not ci:
        raise HTTPException(404, "Cart item not found")
    db.delete(ci)
    db.commit()
    return {"ok": True}
