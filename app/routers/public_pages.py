"""Public SSR pages: publication search and coauthorship tree."""

from __future__ import annotations

from fastapi import Query, Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.dependencies.session import SessionDep
from app.services import research
from app.services.publication_tree import DEFAULT_MAX_DEPTH, build_publication_tree

from . import router, templates


async def _optional_user(request: Request, db: SessionDep, logged_in: bool):
    if not logged_in:
        return None
    try:
        return await get_current_user(request, db)
    except Exception:
        return None


@router.get("/search", response_class=HTMLResponse, name="search_view")
async def search_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
    title: str | None = Query(default=None),
    author: str | None = Query(default=None),
    year: int | None = Query(default=None),
    venue: str | None = Query(default=None),
):
    filters = {
        "title": (title or "").strip() or None,
        "author": (author or "").strip() or None,
        "year": year,
        "venue": (venue or "").strip() or None,
    }
    queried = any(v is not None and v != "" for v in filters.values())
    results = research.search_publications(**filters) if queried else []

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "user": await _optional_user(request, db, user_logged_in),
            "filters": {
                "title": title or "",
                "author": author or "",
                "year": year if year is not None else "",
                "venue": venue or "",
            },
            "queried": queried,
            "results": results,
        },
    )


@router.get("/tree", response_class=HTMLResponse, name="tree_view")
async def tree_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
    author_id: int | None = Query(default=None),
    max_depth: int | None = Query(default=None),
):
    authors = research.list_authors()
    depth = DEFAULT_MAX_DEPTH if max_depth is None else max(0, min(max_depth, 8))
    tree_result = None
    selected = None
    if author_id is not None:
        selected = author_id
        tree_result = build_publication_tree(author_id, max_depth=depth)

    return templates.TemplateResponse(
        request=request,
        name="tree.html",
        context={
            "user": await _optional_user(request, db, user_logged_in),
            "authors": authors,
            "selected_author_id": selected,
            "max_depth": depth,
            "tree_result": tree_result,
        },
    )
