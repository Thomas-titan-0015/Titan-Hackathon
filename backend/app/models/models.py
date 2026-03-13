from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Anonymous")
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="user")  # "user" or "admin"
    email_verified = Column(Integer, default=0)
    otp_code = Column(String(10), nullable=True)
    otp_expires = Column(DateTime, nullable=True)
    receive_updates = Column(Integer, default=0)
    date_of_birth = Column(Date, nullable=True)
    anniversary_date = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    phone_verified = Column(Integer, default=0)
    phone_otp = Column(String(10), nullable=True)
    phone_otp_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    segment = Column(String(20), default="new")  # new / returning

    sessions = relationship("Session", back_populates="user")
    preferences = relationship("Preference", back_populates="user", uselist=False)
    cart_items = relationship("CartItem", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    path = Column(String(20), nullable=True)
    message_count = Column(Integer, default=0)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    events = relationship("Event", back_populates="session")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id"))
    role = Column(String(10))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    intent = Column(String(50), nullable=True)
    constraints = Column(JSON, nullable=True)
    item_ids_shown = Column(JSON, nullable=True)

    session = relationship("Session", back_populates="messages")


class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    categories = Column(JSON, default=list)
    styles = Column(JSON, default=list)
    past_likes = Column(JSON, default=list)
    past_dislikes = Column(JSON, default=list)
    constraints = Column(JSON, nullable=True)

    user = relationship("User", back_populates="preferences")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    category = Column(String(100))
    subcategory = Column(String(100), nullable=True)
    attributes = Column(JSON, nullable=True)
    description = Column(Text)
    price = Column(Float)
    original_price = Column(Float, nullable=True)
    image_url = Column(String(500))
    rating = Column(Float, default=4.0)
    reviews_count = Column(Integer, default=0)
    in_stock = Column(Integer, default=1)
    featured = Column(Integer, default=0)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id"))
    type = Column(String(30))
    payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="events")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(64), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart_items")
    item = relationship("Item")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(64), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist_items")
    item = relationship("Item")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(64), nullable=True)
    items = Column(JSON)
    total = Column(Float)
    discount = Column(Float, default=0.0)
    promo_code = Column(String(50), nullable=True)
    placed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
