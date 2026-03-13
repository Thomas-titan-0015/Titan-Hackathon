from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime, date


# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    receive_updates: bool = False

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    segment: str
    phone: Optional[str] = None
    phone_verified: int = 0
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    created_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

class ProfileUpdateRequest(BaseModel):
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    phone: Optional[str] = None

class PhoneOTPRequest(BaseModel):
    phone: str

class VerifyPhoneOTPRequest(BaseModel):
    phone: str
    otp: str

class TrackCategoryRequest(BaseModel):
    category: str

class ProfileCompletionOut(BaseModel):
    percentage: int
    missing: List[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class OTPResponse(BaseModel):
    message: str
    email: str


# ── Products ──────────────────────────────────────────
class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    subcategory: Optional[str] = None
    attributes: Optional[dict] = None
    description: str
    price: float
    original_price: Optional[float] = None
    image_url: str
    rating: float = 4.0
    reviews_count: int = 0
    in_stock: int = 1
    featured: int = 0

    class Config:
        from_attributes = True


# ── Cart ──────────────────────────────────────────────
class CartAddRequest(BaseModel):
    item_id: int
    quantity: int = 1

class CartItemOut(BaseModel):
    id: int
    item_id: int
    quantity: int
    item: ProductOut

    class Config:
        from_attributes = True


# ── Wishlist ──────────────────────────────────────────
class WishlistAddRequest(BaseModel):
    item_id: int

class WishlistItemOut(BaseModel):
    id: int
    item_id: int
    item: ProductOut

    class Config:
        from_attributes = True


# ── Chat ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class RecommendationCard(BaseModel):
    id: int
    name: str
    price: float
    image_url: str
    reason: str

class ChatResponse(BaseModel):
    session_id: str
    text: str
    recommendations: List[RecommendationCard] = []

class FeedbackRequest(BaseModel):
    session_id: str
    item_id: int
    action: str


# ── Orders ────────────────────────────────────────────
class OrderCreateRequest(BaseModel):
    promo_code: Optional[str] = None
    guest_session: Optional[str] = None

class OrderOut(BaseModel):
    id: int
    items: Any
    total: float
    discount: float = 0.0
    promo_code: Optional[str] = None
    placed_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────
class DashboardOverview(BaseModel):
    total_sessions: int
    new_users: int
    returning_users: int
    avg_messages_per_session: float
    total_orders: int
    total_revenue: float

class SessionOut(BaseModel):
    id: str
    user_id: Optional[int] = None
    started_at: datetime
    path: Optional[str] = None
    message_count: int

    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    item_ids_shown: Optional[list] = None

    class Config:
        from_attributes = True

class RecStat(BaseModel):
    session_id: str
    shown: int
    clicked: int
    dismissed: int
    ctr: float
