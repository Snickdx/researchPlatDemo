# COMP 3613 Research Platform (example starter)

Flawed baseline **0.1.0** built on [uwidcit/faststart](https://github.com/uwidcit/faststart) (`96ccfce`).

**Example use only** — not wired as a live course submodule / interview scenario until approved. FastStart provides the SSR shell, JWT cookie auth, SQLModel, `manage.py`, and Render/Docker wiring. The research-plat scenario adds domain models/services and a JSON API under `/api` (see `/docs`).

## Quick start

```text
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: Copy-Item .env.example .env
python manage.py init
python manage.py run
```

Open http://127.0.0.1:5000 — SSR auth shell; scenario JSON under `/api` and OpenAPI at `/docs`.

## Current features

### SSR UI (working)

| Feature | Route | Notes |
| --- | --- | --- |
| Landing | `/` | Nav to search, publication tree, and sign-in |
| Publication search | `/search` | Public filters: title, author, year, venue |
| Publication tree | `/tree` | Public; pick a root author and max depth |
| Sign-in / register | `/login`, `/register` | Username **or** email → JWT cookie |
| Logout | `/logout` | Clears session cookie |
| Password hashing | — | Argon2id; login responses omit password material |

### Research JSON API (working under `/api`, OpenAPI at `/docs`)

Demo auth: `POST /api/auth/login` with `{email, password}`, then send `X-User-Id` on admin mutations.

| Feature | Notes |
| --- | --- |
| API login | Email + password only (username is SSR-only) |
| List authors / publications | Open read; publications include coauthor lists |
| Create author | Admin-only; requires name + unique email |
| Create publication | Admin-only; title, year, ≥1 existing coauthor ids |
| Search publications | Filters by title, author, year, and/or venue; returns coauthors |

### Seeded accounts & data

| Login | Password | Role |
| --- | --- | --- |
| `admin` / `admin@example.com` | `admin-dev` | admin |

Seeded authors: Ada Okonkwo, Ben Rivera, Cai Chen, Dee Singh — with a small coauthorship graph for the publication tree.

### Not properly implemented yet

- **Author profile edit UI** (Req 1 — see branch `1-implement-r1`)
- **Publication tree semantics** (API and SSR share the flawed starter walker: default depth / visited handling)
- **Admin-only API tree** still requires `X-User-Id` of an admin; the public `/tree` page does not
- **`/config` ops panel** disabled unless `CONFIG_PASSWORD` is set
- PDF upload, citation metrics, and ORCID sync are out of graded MVP

## Student brief

See [`ASSIGNMENT.md`](ASSIGNMENT.md) and [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md).

## Tests

```bash
python -m pytest tests -q
```
