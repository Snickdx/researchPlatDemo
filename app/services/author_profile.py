"""Author profile lookup/update linked to a logged-in User by email."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models.author import Author
from app.models.user import User


def get_profile_for_user(user: User) -> dict[str, Any] | None:
    with Session(engine) as session:
        author = session.exec(
            select(Author).where(Author.email == str(user.email).lower())
        ).first()
        if author is None:
            # Case-insensitive fallback for mixed-case emails in legacy rows
            author = session.exec(
                select(Author).where(Author.email == str(user.email))
            ).first()
        if author is None:
            return None
        return author.model_dump()


def ensure_profile_for_user(user: User) -> dict[str, Any]:
    """Return the author's profile, creating a blank one from the user account if needed."""
    existing = get_profile_for_user(user)
    if existing:
        return existing

    with Session(engine) as session:
        email = str(user.email).strip().lower()
        row = Author(
            name=user.username,
            email=email,
            affiliation="",
            active=True,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row.model_dump()


def update_profile_for_user(
    user: User,
    *,
    name: str,
    affiliation: str = "",
    email: str | None = None,
) -> dict[str, Any]:
    name = (name or "").strip()
    affiliation = (affiliation or "").strip()
    if not name:
        return {"ok": False, "error": "display name required"}

    with Session(engine) as session:
        author = session.exec(
            select(Author).where(Author.email == str(user.email).lower())
        ).first()
        if author is None:
            author = session.exec(
                select(Author).where(Author.email == str(user.email))
            ).first()

        new_email = (email or str(user.email)).strip().lower()
        if not new_email:
            return {"ok": False, "error": "email required"}

        if author is None:
            conflict = session.exec(
                select(Author).where(Author.email == new_email)
            ).first()
            if conflict:
                return {"ok": False, "error": "email already used by another author"}
            author = Author(
                name=name,
                email=new_email,
                affiliation=affiliation,
                active=True,
            )
            session.add(author)
        else:
            if new_email != author.email:
                conflict = session.exec(
                    select(Author).where(
                        Author.email == new_email, Author.id != author.id
                    )
                ).first()
                if conflict:
                    return {"ok": False, "error": "email already used by another author"}
                author.email = new_email
                # Keep login email in sync when the author owns this account
                db_user = session.get(User, user.id)
                if db_user is not None:
                    db_user.email = new_email
                    session.add(db_user)
            author.name = name
            author.affiliation = affiliation
            session.add(author)

        session.commit()
        session.refresh(author)
        return {"ok": True, "author": author.model_dump()}
