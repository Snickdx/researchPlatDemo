"""Research platform JSON API (OpenAPI /docs)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.services import research
from app.services import research_auth as auth

router = APIRouter(tags=["research-plat"])


class LoginBody(BaseModel):
    email: str
    password: str


class AuthorBody(BaseModel):
    name: str
    email: str
    affiliation: str = ""


class PublicationBody(BaseModel):
    title: str
    year: int
    author_ids: list[int] = Field(min_length=1)
    venue: str = ""


def _actor_id(x_user_id: str | None) -> int:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        return int(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-User-Id must be int") from exc


@router.post("/auth/login")
def login(body: LoginBody) -> dict[str, Any]:
    user = auth.login(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"user": user}


@router.get("/authors")
def authors() -> dict[str, Any]:
    return {"authors": research.list_authors()}


@router.post("/authors")
def create_author(
    body: AuthorBody, x_user_id: str | None = Header(default=None)
) -> dict[str, Any]:
    result = research.create_author(
        _actor_id(x_user_id),
        name=body.name,
        email=body.email,
        affiliation=body.affiliation,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/publications")
def publications() -> dict[str, Any]:
    return {"publications": research.list_publications()}


@router.post("/publications")
def create_publication(
    body: PublicationBody, x_user_id: str | None = Header(default=None)
) -> dict[str, Any]:
    result = research.add_publication(
        _actor_id(x_user_id),
        title=body.title,
        year=body.year,
        author_ids=body.author_ids,
        venue=body.venue,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/publications/search")
def search(
    title: str | None = Query(default=None),
    author: str | None = Query(default=None),
    year: int | None = Query(default=None),
    venue: str | None = Query(default=None),
) -> dict[str, Any]:
    return {
        "publications": research.search_publications(
            title=title, author=author, year=year, venue=venue
        )
    }


@router.get("/authors/{author_id}/publication-tree")
def publication_tree(
    author_id: int,
    max_depth: int | None = Query(default=None),
    x_user_id: str | None = Header(default=None),
) -> dict[str, Any]:
    result = research.publication_tree(
        _actor_id(x_user_id),
        author_id=author_id,
        max_depth=max_depth,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
