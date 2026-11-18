"""Demo auth for research-plat JSON API (X-User-Id style)."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models.user import User
from app.utilities.security import verify_password


def login(email: str, password: str) -> dict[str, Any] | None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not verify_password(password, user.password):
            return None
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }


def get_user(user_id: int) -> dict[str, Any] | None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
