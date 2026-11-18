"""Author profiles, publications, and search for research-plat."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models.author import Author
from app.models.publication import Publication, PublicationAuthor
from app.services.publication_tree import DEFAULT_MAX_DEPTH, build_publication_tree
from app.services.research_auth import get_user


def _require_admin(actor_id: int) -> dict[str, Any] | None:
    user = get_user(actor_id)
    if not user or user["role"] != "admin":
        return None
    return user


def list_authors() -> list[dict[str, Any]]:
    with Session(engine) as session:
        rows = session.exec(select(Author).order_by(Author.id)).all()
        return [r.model_dump() for r in rows]


def create_author(
    actor_id: int,
    *,
    name: str,
    email: str,
    affiliation: str = "",
) -> dict[str, Any]:
    if not _require_admin(actor_id):
        return {"ok": False, "error": "admin only"}
    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name:
        return {"ok": False, "error": "name required"}
    if not email:
        return {"ok": False, "error": "email required"}

    with Session(engine) as session:
        existing = session.exec(select(Author).where(Author.email == email)).first()
        if existing:
            return {"ok": False, "error": "email already used"}
        row = Author(name=name, email=email, affiliation=affiliation or "")
        session.add(row)
        session.commit()
        session.refresh(row)
        return {"ok": True, "author": row.model_dump()}


def _publication_dict(session: Session, pub: Publication) -> dict[str, Any]:
    links = session.exec(
        select(PublicationAuthor).where(PublicationAuthor.publication_id == pub.id)
    ).all()
    authors = []
    for link in links:
        a = session.get(Author, link.author_id)
        if a:
            authors.append({"id": a.id, "name": a.name, "email": a.email})
    data = pub.model_dump()
    data["coauthors"] = authors
    return data


def list_publications() -> list[dict[str, Any]]:
    with Session(engine) as session:
        rows = session.exec(select(Publication).order_by(Publication.id)).all()
        return [_publication_dict(session, p) for p in rows]


def add_publication(
    actor_id: int,
    *,
    title: str,
    year: int,
    author_ids: list[int],
    venue: str = "",
) -> dict[str, Any]:
    if not _require_admin(actor_id):
        return {"ok": False, "error": "admin only"}
    title = (title or "").strip()
    if not title:
        return {"ok": False, "error": "title required"}
    if not isinstance(year, int) or year < 1900 or year > 2100:
        return {"ok": False, "error": "year invalid"}
    ids = [int(x) for x in (author_ids or [])]
    if not ids:
        return {"ok": False, "error": "at least one coauthor required"}

    with Session(engine) as session:
        for aid in ids:
            if session.get(Author, aid) is None:
                return {"ok": False, "error": f"author {aid} not found"}

        # DEFECT-ish soft: duplicate title+year allowed (acceptance wants reject/flag)
        pub = Publication(title=title, year=year, venue=venue or "")
        session.add(pub)
        session.commit()
        session.refresh(pub)
        for aid in ids:
            session.add(
                PublicationAuthor(publication_id=pub.id, author_id=aid)
            )
        session.commit()
        session.refresh(pub)
        return {"ok": True, "publication": _publication_dict(session, pub)}


def search_publications(
    *,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    venue: str | None = None,
) -> list[dict[str, Any]]:
    with Session(engine) as session:
        pubs = session.exec(select(Publication).order_by(Publication.id)).all()
        out: list[dict[str, Any]] = []
        for pub in pubs:
            data = _publication_dict(session, pub)
            if title and title.lower() not in pub.title.lower():
                continue
            if venue and venue.lower() not in (pub.venue or "").lower():
                continue
            if year is not None and pub.year != year:
                continue
            if author:
                names = " ".join(a["name"] for a in data["coauthors"]).lower()
                emails = " ".join(a["email"] for a in data["coauthors"]).lower()
                needle = author.lower()
                if needle not in names and needle not in emails:
                    continue
            out.append(data)
        return out


def publication_tree(
    actor_id: int,
    *,
    author_id: int,
    max_depth: int | None = None,
) -> dict[str, Any]:
    if not _require_admin(actor_id):
        return {"ok": False, "error": "admin only"}
    # Pass through None so the flawed tree module mis-defaults (starter defect).
    if max_depth is None:
        return build_publication_tree(author_id, max_depth=None)
    return build_publication_tree(author_id, max_depth=max_depth)


def default_depth() -> int:
    return DEFAULT_MAX_DEPTH
