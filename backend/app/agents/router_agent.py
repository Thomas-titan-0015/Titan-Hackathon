"""Router Agent – decides preference vs need-state path."""
from sqlalchemy.orm import Session as DBSession
from app.models.models import Session, Preference


def route(session_id: str | None, db: DBSession) -> dict:
    if session_id:
        sess = db.query(Session).filter(Session.id == session_id).first()
        if sess and sess.user_id:
            pref = db.query(Preference).filter(Preference.user_id == sess.user_id).first()
            if pref and (pref.past_likes or pref.categories):
                return {"path": "preference", "user_id": sess.user_id, "session": sess}
    return {"path": "need_state", "user_id": None, "session": None}
