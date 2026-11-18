# Research Platform — public acceptance criteria

Derived from elicitable stakeholder needs (Phase 1). Instructor private defects are **not** listed here.

## Roles & scope

1. Admins create author profiles and register publications with co-authors.
2. Users can search publications by title, author, year, and/or venue.
3. PDF upload, citation metrics, and ORCID sync are out of graded MVP.
4. Passwords hashed; login never returns password material.

## Authors & publications

5. Author profiles require a display name and unique email.
6. A publication requires title, year, and at least one existing co-author.
7. Search returns matching publications including their co-author lists.

## Publication tree

8. From a root author, the system builds a tree of that author's publications and recursively expands publications of transitive co-authors.
9. Already-visited publications are not re-expanded as new branches.
10. Expansion respects a configured maximum depth (default **3**).
