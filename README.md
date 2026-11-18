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

## Seeded API accounts

| Email | Password | Role |
| --- | --- | --- |
| `admin@example.com` | `admin-dev` | admin |

Seeded authors: Ada Okonkwo, Ben Rivera, Cai Chen, Dee Singh — with a small coauthorship graph for the publication tree.

JSON login: `POST /api/auth/login` with `{"email","password"}`. Domain routes take `X-User-Id` (demo auth).

## Student brief

See [`ASSIGNMENT.md`](ASSIGNMENT.md) and [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md).

## Tests

```bash
python -m pytest tests -q
```
