import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.preference import UserPreference
from app.models.user import AppUser
from app.schemas.auth import RegisterRequest


bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt, digest = hashed_password.split("$", maxsplit=1)
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return hmac.compare_digest(digest, candidate.hex())


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return f"{salt}${digest.hex()}"


def get_user_by_email(db: Session, email: str) -> AppUser | None:
    return db.query(AppUser).filter(AppUser.email == email).first()


def create_user(db: Session, payload: RegisterRequest) -> AppUser:
    user = AppUser(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(UserPreference(user_id=user.id, persona=payload.persona))
    db.commit()
    return user


def authenticate_user(db: Session, email: str, password: str) -> AppUser | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.access_token_expire_hours)
    to_encode.update({"exp": expire.isoformat()})
    payload = json.dumps(to_encode, separators=(",", ":")).encode("utf-8")
    token = base64.urlsafe_b64encode(payload).decode("utf-8")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{token}.{signature}"


def decode_access_token(raw_token: str) -> dict:
    token, signature = raw_token.rsplit(".", maxsplit=1)
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid token.")

    payload = json.loads(base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8"))
    expires_at = datetime.fromisoformat(payload["exp"])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired.")
    return payload


def get_token_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials:
        return credentials.credentials
    return request.cookies.get("studymate_token")


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AppUser:
    raw_token = get_token_from_request(request, credentials)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    try:
        payload = decode_access_token(raw_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc

    user = db.query(AppUser).filter(AppUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


def get_current_user_from_cookie(request: Request, db: Session) -> AppUser | None:
    raw_token = request.cookies.get("studymate_token")
    if not raw_token:
        return None
    try:
        payload = decode_access_token(raw_token)
    except HTTPException:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(AppUser).filter(AppUser.id == int(user_id)).first()
