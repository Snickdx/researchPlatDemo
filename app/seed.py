"""Seed admin user and a small coauthorship graph for PubTree demos."""

from __future__ import annotations

from sqlmodel import Session, select

from app.database import drop_all, ensure_db_and_tables, engine
from app.models.author import Author
from app.models.publication import Publication, PublicationAuthor
from app.models.user import User
from app.utilities.security import encrypt_password


def seed(*, reset: bool = False) -> None:
    import app.models  # noqa: F401

    if reset:
        try:
            drop_all()
        except Exception:
            pass
    ensure_db_and_tables()

    with Session(engine) as session:
        if session.exec(select(User)).first() is not None:
            return

        session.add(
            User(
                username="admin",
                email="admin@example.com",
                password=encrypt_password("admin-dev"),
                role="admin",
            )
        )

        ada = Author(
            name="Ada Okonkwo",
            affiliation="DCIT",
            email="ada@example.com",
        )
        ben = Author(
            name="Ben Rivera",
            affiliation="DCIT",
            email="ben@example.com",
        )
        cai = Author(
            name="Cai Chen",
            affiliation="Math",
            email="cai@example.com",
        )
        dee = Author(
            name="Dee Singh",
            affiliation="Library",
            email="dee@example.com",
        )
        session.add(ada)
        session.add(ben)
        session.add(cai)
        session.add(dee)
        session.commit()

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
