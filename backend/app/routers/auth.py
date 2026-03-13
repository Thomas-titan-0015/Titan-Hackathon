import random
import smtplib
import os
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.models import User, Preference
from app.schemas.schemas import LoginRequest, RegisterRequest, VerifyOTPRequest, TokenResponse, UserOut, OTPResponse, ProfileUpdateRequest, ProfileCompletionOut, PhoneOTPRequest, VerifyPhoneOTPRequest, TrackCategoryRequest
from app.auth import hash_password, verify_password, create_token, get_current_user
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/api/auth", tags=["auth"])

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def _send_otp_email(to_email: str, otp: str, name: str = ""):
    """Attempt to send OTP email. Silently pass if SMTP not configured."""
    if not SMTP_USER or not SMTP_PASS:
        print(f"  [OTP] No SMTP configured. OTP for {to_email}: {otp}")
        return
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = "Tanishq — Verify Your Email"
        body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px;">
            <h2 style="color:#D4AF37;">Tanishq<span style="color:#fff;">.</span></h2>
            <p>Hi {name or 'there'},</p>
            <p>Your verification code is:</p>
            <div style="font-size:32px;font-weight:bold;letter-spacing:8px;text-align:center;
                        padding:16px;background:#1a1a1a;color:#D4AF37;border-radius:8px;">
                {otp}
            </div>
            <p style="color:#999;font-size:14px;">This code expires in 10 minutes.</p>
            <p>— The Tanishq Team</p>
        </div>
        """
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
    except Exception as e:
        print(f"  [OTP] Email send failed: {e}. OTP for {to_email}: {otp}")


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_seen = datetime.utcnow()
    db.commit()
    token = create_token(user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/register", response_model=OTPResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing and existing.email_verified:
        raise HTTPException(status_code=409, detail="Email already registered")

    otp = _generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    if existing and not existing.email_verified:
        # Re-send OTP for unverified user
        existing.name = body.name
        existing.password_hash = hash_password(body.password)
        existing.otp_code = otp
        existing.otp_expires = otp_expires
        existing.receive_updates = 1 if body.receive_updates else 0
        db.commit()
    else:
        user = User(
            name=body.name,
            email=body.email,
            password_hash=hash_password(body.password),
            role="user",
            segment="new",
            email_verified=0,
            otp_code=otp,
            otp_expires=otp_expires,
            receive_updates=1 if body.receive_updates else 0,
        )
        db.add(user)
        db.commit()

    _send_otp_email(body.email, otp, body.name)
    return OTPResponse(message="OTP sent to your email. Please verify to complete registration.", email=body.email)


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    if not user.otp_code or user.otp_code != body.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.otp_expires and datetime.utcnow() > user.otp_expires:
        raise HTTPException(status_code=400, detail="OTP expired. Please register again.")

    user.email_verified = 1
    user.otp_code = None
    user.otp_expires = None
    user.last_seen = datetime.utcnow()
    db.commit()

    token = create_token(user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/resend-otp", response_model=OTPResponse)
def resend_otp(body: LoginRequest, db: Session = Depends(get_db)):
    """Resend OTP for unverified users. Body uses email+password from LoginRequest."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified. Please login.")

    otp = _generate_otp()
    user.otp_code = otp
    user.otp_expires = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    _send_otp_email(body.email, otp, user.name)
    return OTPResponse(message="New OTP sent to your email.", email=body.email)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/profile-completion", response_model=ProfileCompletionOut)
def profile_completion(user: User = Depends(get_current_user)):
    fields = {"name": user.name, "email": user.email, "date_of_birth": user.date_of_birth, "anniversary_date": user.anniversary_date, "phone": user.phone}
    filled = sum(1 for v in fields.values() if v)
    total = len(fields)
    missing = [k for k, v in fields.items() if not v]
    return ProfileCompletionOut(percentage=int((filled / total) * 100), missing=missing)


@router.put("/profile", response_model=UserOut)
def update_profile(body: ProfileUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.date_of_birth is not None:
        user.date_of_birth = body.date_of_birth
    if body.anniversary_date is not None:
        user.anniversary_date = body.anniversary_date
    if body.phone is not None:
        import re
        phone = re.sub(r'[^\d+]', '', body.phone)
        user.phone = phone
    db.commit()
    db.refresh(user)
    return user


def _send_sms_otp(phone: str, otp: str):
    """Send OTP via SMS using Fast2SMS (free Indian SMS API).
    Falls back to console logging if no API key is configured."""
    fast2sms_key = os.getenv("FAST2SMS_KEY", "")
    # Clean phone number — remove +91 prefix if present
    clean_phone = phone.lstrip('+')
    if clean_phone.startswith('91') and len(clean_phone) > 10:
        clean_phone = clean_phone[2:]

    if not fast2sms_key:
        # Use 2Factor.in or fallback to Titan AI gateway SMS if available
        print(f"  [SMS] OTP for {phone}: {otp}")
        return True

    try:
        resp = httpx.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": fast2sms_key},
            data={
                "variables_values": otp,
                "route": "otp",
                "numbers": clean_phone,
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("return"):
            print(f"  [SMS] OTP sent to {phone}")
            return True
        else:
            print(f"  [SMS] Fast2SMS failed: {data}. OTP for {phone}: {otp}")
            return True  # Still allow verification with console OTP
    except Exception as e:
        print(f"  [SMS] Send failed: {e}. OTP for {phone}: {otp}")
        return True


@router.post("/send-phone-otp")
def send_phone_otp(body: PhoneOTPRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import re
    phone = re.sub(r'[^\d+]', '', body.phone)
    if len(phone.replace('+', '').replace('91', '', 1)) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    otp = _generate_otp()
    user.phone = phone
    user.phone_otp = otp
    user.phone_otp_expires = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    _send_sms_otp(phone, otp)
    return {"message": "OTP sent to your phone number", "phone": phone}


@router.post("/verify-phone-otp", response_model=UserOut)
def verify_phone_otp(body: VerifyPhoneOTPRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.phone_otp or user.phone_otp != body.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.phone_otp_expires and datetime.utcnow() > user.phone_otp_expires:
        raise HTTPException(status_code=400, detail="OTP expired")

    user.phone_verified = 1
    user.phone_otp = None
    user.phone_otp_expires = None
    db.commit()
    db.refresh(user)
    return user


@router.post("/track-category")
def track_category(body: TrackCategoryRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Track a category the user has viewed/browsed — updates their preference record."""
    pref = db.query(Preference).filter(Preference.user_id == user.id).first()
    if not pref:
        pref = Preference(user_id=user.id, categories=[body.category], styles=[], past_likes=[], past_dislikes=[])
        db.add(pref)
    else:
        cats = list(pref.categories or [])
        # Move to front if already there, otherwise prepend
        if body.category in cats:
            cats.remove(body.category)
        cats.insert(0, body.category)
        pref.categories = cats
        flag_modified(pref, "categories")
    db.commit()
    return {"ok": True, "categories": pref.categories}
