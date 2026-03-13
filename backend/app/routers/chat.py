import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.models.models import Session, Message, Event, User, Preference
from app.schemas.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.agents import router_agent, preference_agent, need_state_agent, recommendation_agent
from app.services import openai_service
from app.auth import get_optional_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

_conversation_state: dict[str, dict] = {}


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, user: Optional[User] = Depends(get_optional_user), db: DBSession = Depends(get_db)):
    session_id = body.session_id
    message = body.message.strip()

    if session_id:
        sess = db.query(Session).filter(Session.id == session_id).first()
    else:
        sess = None

    if not sess:
        session_id = uuid.uuid4().hex[:16]
        sess = Session(id=session_id, user_id=user.id if user else None, started_at=datetime.utcnow(), message_count=0)
        db.add(sess)
        db.commit()

    # Ensure session is linked to logged-in user
    if user and not sess.user_id:
        sess.user_id = user.id
        db.commit()

    user_msg = Message(session_id=sess.id, role="user", content=message, timestamp=datetime.utcnow())
    db.add(user_msg)
    sess.message_count += 1
    db.commit()

    # Route
    route_result = router_agent.route(sess.id, db)
    path = route_result["path"]
    route_user_id = route_result["user_id"]

    if not sess.path:
        sess.path = path
        db.commit()

    recommendations = []
    response_text = ""

    if path == "preference" and route_user_id:
        recs = preference_agent.get_recommendations(route_user_id, db, limit=5)
        recommendations = recs
        # Try OpenAI for a natural welcome
        ai_text = openai_service.generate_recommendation_intro(message, {}, len(recs)) if recs else None
        if ai_text:
            response_text = ai_text
        elif recs:
            uname = user.name if user else 'there'
            response_text = f"Welcome back, {uname}! Here are some pieces curated just for you:"
        else:
            uname = user.name if user else 'there'
            response_text = f"Welcome back, {uname}! Let me find something exquisite for you."
            recs = recommendation_agent.recommend(db, limit=5)
            recommendations = recs
    else:
        # Need-state path
        state = _conversation_state.get(sess.id, {})

        # Build conversation history for OpenAI
        history = []
        prev_msgs = db.query(Message).filter(
            Message.session_id == sess.id
        ).order_by(Message.timestamp).all()
        for m in prev_msgs[-6:]:
            history.append({"role": m.role, "content": m.content})

        result = need_state_agent.process_message(message, state, history)
        _conversation_state[sess.id] = result["constraints"]

        if result["ready"]:
            recs = recommendation_agent.recommend(db, constraints=result["constraints"], limit=5)
            recommendations = recs
            ai_text = openai_service.generate_recommendation_intro(
                message, result["constraints"], len(recs)
            )
            if ai_text and recs:
                response_text = ai_text
            elif recs:
                response_text = "Based on your preferences, here are my top recommendations:"
            else:
                response_text = "I couldn't find exact matches. Here are some popular pieces:"
                recs = recommendation_agent.recommend(db, limit=5)
                recommendations = recs
        else:
            response_text = result["text"]

    item_ids = [r["id"] for r in recommendations] if recommendations else None
    assistant_msg = Message(
        session_id=sess.id, role="assistant", content=response_text,
        timestamp=datetime.utcnow(), item_ids_shown=item_ids,
    )
    db.add(assistant_msg)
    sess.message_count += 1

    if recommendations:
        evt = Event(
            session_id=sess.id, type="rec_shown",
            payload={"item_ids": item_ids}, timestamp=datetime.utcnow(),
        )
        db.add(evt)

    db.commit()

    return ChatResponse(session_id=sess.id, text=response_text, recommendations=recommendations)


@router.post("/feedback")
def feedback(body: FeedbackRequest, user: Optional[User] = Depends(get_optional_user), db: DBSession = Depends(get_db)):
    sess = db.query(Session).filter(Session.id == body.session_id).first()
    if not sess:
        return {"ok": False, "error": "Session not found"}

    evt = Event(
        session_id=sess.id,
        type="rec_clicked" if body.action == "like" else "rec_dismissed",
        payload={"item_id": body.item_id, "action": body.action},
        timestamp=datetime.utcnow(),
    )
    db.add(evt)

    if user:
        pref = db.query(Preference).filter(Preference.user_id == user.id).first()
        if pref:
            if body.action == "like":
                likes = pref.past_likes or []
                if body.item_id not in likes:
                    likes.append(body.item_id)
                    pref.past_likes = likes
            elif body.action == "dislike":
                dislikes = pref.past_dislikes or []
                if body.item_id not in dislikes:
                    dislikes.append(body.item_id)
                    pref.past_dislikes = dislikes
        else:
            state = _conversation_state.get(body.session_id, {})
            pref = Preference(
                user_id=user.id,
                categories=[state.get("category")] if state.get("category") else [],
                styles=[state.get("style")] if state.get("style") else [],
                past_likes=[body.item_id] if body.action == "like" else [],
                past_dislikes=[body.item_id] if body.action == "dislike" else [],
            )
            db.add(pref)

    db.commit()
    return {"ok": True}
