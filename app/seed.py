"""Seed admin user, author logins, and a small coauthorship graph for PubTree demos."""

from __future__ import annotations

from sqlmodel import Session, select

from app.database import drop_all, ensure_db_and_tables, engine
from app.models.author import Author
from app.models.publication import Publication, PublicationAuthor
from app.models.user import User
from app.utilities.security import encrypt_password

AUTHOR_SEED_PASSWORD = "author-dev"

_AUTHOR_USERS = (
    ("ada", "ada@example.com", "Ada Okonkwo", "DCIT"),
    ("ben", "ben@example.com", "Ben Rivera", "DCIT"),
    ("cai", "cai@example.com", "Cai Chen", "Math"),
    ("dee", "dee@example.com", "Dee Singh", "Library"),
)


def seed(*, reset: bool = False) -> None:
    import app.models  # noqa: F401

    if reset:
        try:
            drop_all()
        except Exception:
            pass
    ensure_db_and_tables()

    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if admin is None:
            session.add(
                User(
                    username="admin",
                    email="admin@example.com",
                    password=encrypt_password("admin-dev"),
                    role="admin",
                )
            )
            session.commit()

        authors_by_email: dict[str, Author] = {}
        for username, email, name, affiliation in _AUTHOR_USERS:
            author = session.exec(select(Author).where(Author.email == email)).first()
            if author is None:
                author = Author(name=name, affiliation=affiliation, email=email)
                session.add(author)
                session.commit()
                session.refresh(author)

            user = session.exec(select(User).where(User.email == email)).first()
            if user is None:
                session.add(
                    User(
                        username=username,
                        email=email,
                        password=encrypt_password(AUTHOR_SEED_PASSWORD),
                        role="regular_user",
                    )
                )
                session.commit()

            authors_by_email[email] = author

        if session.exec(select(Publication)).first() is not None:
            return

        ada = authors_by_email["ada@example.com"]
        ben = authors_by_email["ben@example.com"]
        cai = authors_by_email["cai@example.com"]
        dee = authors_by_email["dee@example.com"]

        # Graph:
        #   Ada+Ben → Patterns in SE
        #   Ben+Cai → Graph Queries
        #   Cai+Dee → Metadata Standards
        #   Ada+Cai → Composite Walks  (creates a cycle-ish path Ada↔Cai)
        pubs = [
            ("Patterns in Software Engineering", 2022, "COMP Conf", [ada, ben]),
            ("Graph Queries at Scale", 2023, "DB Workshop", [ben, cai]),
            ("Metadata Standards for Repositories", 2021, "LibTech", [cai, dee]),
            ("Composite Walks over Coauthors", 2024, "SE Notes", [ada, cai]),
        ]
        for title, year, venue, authors in pubs:
            pub = Publication(title=title, year=year, venue=venue)
            session.add(pub)
            session.commit()
            session.refresh(pub)
            for a in authors:
                session.add(
                    PublicationAuthor(publication_id=pub.id, author_id=a.id)
                )
        session.commit()
