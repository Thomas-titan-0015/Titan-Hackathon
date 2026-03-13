from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
from app.db.database import get_db
from app.models.models import CartItem, Order, Item, User
from app.schemas.schemas import OrderCreateRequest, OrderOut
from app.auth import get_optional_user

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Promo: TANISHQ1000 gives logged-in users ₹1000 off
PROMO_CODES = {
    "TANISHQ1000": {"discount": 1000.0, "requires_login": True, "description": "Flat ₹1,000 OFF for members"},
}


def _get_guest_id(x_guest_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_guest_id


@router.post("", response_model=OrderOut)
def place_order(
    body: OrderCreateRequest,
    user: Optional[User] = Depends(get_optional_user),
    guest_id: Optional[str] = Depends(_get_guest_id),
    db: DBSession = Depends(get_db),
):
    if user:
        cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    elif guest_id:
        cart_items = db.query(CartItem).filter(CartItem.session_id == guest_id).all()
    else:
        raise HTTPException(400, "Login or provide a guest session ID")

    if not cart_items:
        raise HTTPException(400, "Cart is empty")

    order_items = []
    subtotal = 0.0
    for ci in cart_items:
        item = db.query(Item).filter(Item.id == ci.item_id).first()
        if item:
            order_items.append({"item_id": item.id, "name": item.name, "qty": ci.quantity, "price": item.price})
            subtotal += item.price * ci.quantity

    discount = 0.0
    promo = body.promo_code.strip().upper() if body.promo_code else None
    if promo:
        code_info = PROMO_CODES.get(promo)
        if not code_info:
            raise HTTPException(400, "Invalid promo code")
        if code_info["requires_login"] and not user:
            raise HTTPException(400, "Please log in to use this promo code")
        discount = min(code_info["discount"], subtotal)

    total = round(max(subtotal - discount, 0), 2)

    order = Order(
        user_id=user.id if user else None,
        session_id=guest_id if not user else None,
        items=order_items,
        total=total,
        discount=round(discount, 2),
        promo_code=promo,
        placed_at=datetime.utcnow(),
    )
    db.add(order)

    for ci in cart_items:
        db.delete(ci)

    db.commit()
    db.refresh(order)
    return order


@router.get("/promo-info")
def get_promo_info(user: Optional[User] = Depends(get_optional_user)):
    """Returns promo info depending on login status."""
    if user:
        return {
            "promo_code": "TANISHQ1000",
            "message": "Use code TANISHQ1000 for flat ₹1,000 OFF!",
            "discount": 1000,
            "eligible": True,
        }
    else:
        return {
            "promo_code": None,
            "message": "Log in to get flat ₹1,000 OFF on your order!",
            "discount": 0,
            "eligible": False,
        }


@router.get("", response_model=List[OrderOut])
def get_orders(
    user: Optional[User] = Depends(get_optional_user),
    guest_id: Optional[str] = Depends(_get_guest_id),
    db: DBSession = Depends(get_db),
):
    if user:
        return db.query(Order).filter(Order.user_id == user.id).all()
    elif guest_id:
        return db.query(Order).filter(Order.session_id == guest_id).all()
    return []
