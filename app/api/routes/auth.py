from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
)


router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = create_user(db, payload)
    token = create_access_token({"sub": str(user.id), "email": user.email})
    response.set_cookie(
        key="studymate_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )
    return AuthResponse(
        access_token=token,
        user={"id": user.id, "name": user.full_name, "email": user.email},
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    response.set_cookie(
        key="studymate_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )
    return AuthResponse(
        access_token=token,
        user={"id": user.id, "name": user.full_name, "email": user.email},
    )


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("studymate_token", path="/")
    return {"message": "Logged out successfully."}
