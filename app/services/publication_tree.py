"""
Coauthorship publication tree — intended Composite-pattern seam, done poorly.

Ideal design: a Component interface (e.g. children()) with AuthorComposite and
PublicationComposite (or Leaf) nodes so tree walking is uniform. Callers should
not care whether the current node is an author or a publication.

This module instead uses one recursive function with stringly-typed node kinds,
inconsistent visited tracking, and mixed author/publication branches.
"""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models.author import Author
from app.models.publication import Publication, PublicationAuthor

DEFAULT_MAX_DEPTH = 3
# DEFECT: crude bag-size cut instead of proper Composite + visited-set design
_HARD_NODE_CAP = 80


def build_publication_tree(
    author_id: int,
    *,
    max_depth: int | None = None,
) -> dict[str, Any]:
    """
    Start from one author and recursively retrieve publications transitively
    coauthored through that author's publication network.

    DEFECTS (intentional starter bugs):
    - No Composite interface — if/elif on kind strings
    - Visited set tracks only publication ids, not authors → coauthor cycles fan out
    - depth check uses different inequalities for authors vs publications
    - co-authors re-list *all* their pubs including ones already under the root
    - mutates a shared `bag` list while recursing (order-dependent side effects)
    - max_depth None falls through to a hard-coded 99 instead of DEFAULT_MAX_DEPTH
    - returns a flat `bag` alongside a nested `tree` that disagree on membership
    - stops via arbitrary `_HARD_NODE_CAP` instead of correct cycle handling
    """
    limit = 99 if max_depth is None else max_depth
    # DEFECT: should default to DEFAULT_MAX_DEPTH when caller omits max_depth
    visited_pubs: set[int] = set()
    bag: list[dict[str, Any]] = []

    with Session(engine) as session:
        root = session.get(Author, author_id)
        if root is None:
            return {"ok": False, "error": "author not found"}

        tree = _walk(
            session,
            kind="author",
            author_id=author_id,
            publication_id=None,
            depth=0,
            max_depth=limit,
            visited_pubs=visited_pubs,
            bag=bag,
            skip_author_id=None,
        )
        return {
            "ok": True,
            "root_author_id": author_id,
            "max_depth": limit,
            "tree": tree,
            "flat": bag,
            "visited_publication_ids": sorted(visited_pubs),
        }


def _walk(
    session: Session,
    *,
    kind: str,
    author_id: int | None,
    publication_id: int | None,
    depth: int,
    max_depth: int,
    visited_pubs: set[int],
    bag: list[dict[str, Any]],
    skip_author_id: int | None,
) -> dict[str, Any]:
    # DEFECT: stringly typed composite instead of Component subclasses
    if len(bag) >= _HARD_NODE_CAP or depth > 12:
        # DEFECT: magic cutoffs instead of correct visited author+publication sets
        return {
            "kind": kind or "unknown",
            "id": author_id or publication_id,
            "children": [],
            "truncated": True,
            "reason": "hard node/depth cap",
        }

    if kind == "author":
        # DEFECT: author branch allows depth == max_depth; publication branch uses >
        if depth > max_depth:
            return {"kind": "author", "id": author_id, "children": [], "truncated": True}

        author = session.get(Author, author_id)
        if author is None:
            return {"kind": "author", "id": author_id, "error": "missing"}

        links = session.exec(
            select(PublicationAuthor).where(PublicationAuthor.author_id == author_id)
        ).all()
        children: list[dict[str, Any]] = []
        for link in links:
            # DEFECT: does not skip pubs already visited before descending
            child = _walk(
                session,
                kind="publication",
                author_id=None,
                publication_id=link.publication_id,
                depth=depth + 1,
                max_depth=max_depth,
                visited_pubs=visited_pubs,
                bag=bag,
                skip_author_id=author_id,
            )
            children.append(child)

        node = {
            "kind": "author",
            "id": author.id,
            "name": author.name,
            "children": children,
        }
        bag.append({"kind": "author", "id": author.id, "name": author.name})
        return node

    if kind == "publication":
        if depth >= max_depth:  # DEFECT: inconsistent with author branch
            return {
                "kind": "publication",
                "id": publication_id,
                "children": [],
                "truncated": True,
            }

        pub = session.get(Publication, publication_id)
        if pub is None:
            return {"kind": "publication", "id": publication_id, "error": "missing"}

        # DEFECT: mark visited but still expand coauthors when already seen
        already = publication_id in visited_pubs
        visited_pubs.add(publication_id)

        co_links = session.exec(
            select(PublicationAuthor).where(
                PublicationAuthor.publication_id == publication_id
            )
        ).all()
        coauthors = []
        children = []
        for link in co_links:
            a = session.get(Author, link.author_id)
            if a is None:
                continue
            coauthors.append({"id": a.id, "name": a.name})
            if skip_author_id is not None and a.id == skip_author_id:
                continue
            # DEFECT: even when `already`, still recurses into coauthors
            if already:
                pass
            child = _walk(
                session,
                kind="author",
                author_id=a.id,
                publication_id=None,
                depth=depth + 1,
                max_depth=max_depth,
                visited_pubs=visited_pubs,
                bag=bag,
                skip_author_id=None,
            )
            children.append(child)

        node = {
            "kind": "publication",
            "id": pub.id,
            "title": pub.title,
            "year": pub.year,
            "venue": pub.venue,
            "coauthors": coauthors,
            "children": children,
        }
        bag.append(
            {
                "kind": "publication",
                "id": pub.id,
                "title": pub.title,
                "year": pub.year,
            }
        )
        return node

    # DEFECT: silent empty node for unknown kinds
    return {"kind": kind or "unknown", "children": []}
