from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from typing import Optional, List
from app.db.database import get_db
from app.models.models import Session, Message, User, Event, Order
from app.schemas.schemas import DashboardOverview, SessionOut, MessageOut, UserOut, RecStat
from app.auth import require_admin

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(admin: User = Depends(require_admin), db: DBSession = Depends(get_db)):
    total_sessions = db.query(func.count(Session.id)).scalar() or 0
    new_users = db.query(func.count(User.id)).filter(User.segment == "new").scalar() or 0
    returning = db.query(func.count(User.id)).filter(User.segment == "returning").scalar() or 0
    avg_msg = db.query(func.avg(Session.message_count)).scalar() or 0.0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    revenue = db.query(func.sum(Order.total)).scalar() or 0.0
    return DashboardOverview(
        total_sessions=total_sessions, new_users=new_users, returning_users=returning,
        avg_messages_per_session=round(float(avg_msg), 1),
        total_orders=total_orders, total_revenue=round(float(revenue), 2),
    )


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(path: Optional[str] = None, admin: User = Depends(require_admin), db: DBSession = Depends(get_db)):
    q = db.query(Session)
    if path:
        q = q.filter(Session.path == path)
    return q.order_by(Session.started_at.desc()).all()


@router.get("/conversations", response_model=List[MessageOut])
def get_conversation(session_id: str, admin: User = Depends(require_admin), db: DBSession = Depends(get_db)):
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()


@router.get("/users", response_model=List[UserOut])
def list_users(admin: User = Depends(require_admin), db: DBSession = Depends(get_db)):
    return db.query(User).order_by(User.last_seen.desc()).all()


@router.get("/recommendation-stats", response_model=List[RecStat])
def rec_stats(admin: User = Depends(require_admin), db: DBSession = Depends(get_db)):
    sessions = db.query(Session).all()
    stats = []
    for s in sessions:
        shown = db.query(func.count(Event.id)).filter(Event.session_id == s.id, Event.type == "rec_shown").scalar() or 0
        clicked = db.query(func.count(Event.id)).filter(Event.session_id == s.id, Event.type == "rec_clicked").scalar() or 0
        dismissed = db.query(func.count(Event.id)).filter(Event.session_id == s.id, Event.type == "rec_dismissed").scalar() or 0
        if shown == 0 and clicked == 0:
            continue
        ctr = round(clicked / max(shown, 1) * 100, 1)
        stats.append(RecStat(session_id=s.id, shown=shown, clicked=clicked, dismissed=dismissed, ctr=ctr))
    return stats
