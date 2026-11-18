"""SSR author profile editor (requires login)."""

from __future__ import annotations

from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.services import author_profile
from app.utilities.flash import flash

from . import router, templates


@router.get("/profile", response_class=HTMLResponse, name="profile_view")
async def profile_view(request: Request, user: AuthDep):
    profile = author_profile.ensure_profile_for_user(user)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "profile": profile,
        },
    )


@router.post("/profile", response_class=HTMLResponse, name="profile_action")
async def profile_action(
    request: Request,
    user: AuthDep,
    name: str = Form(),
    affiliation: str = Form(""),
    email: str = Form(),
):
    result = author_profile.update_profile_for_user(
        user,
        name=name,
        affiliation=affiliation,
        email=email,
    )
    if not result.get("ok"):
        flash(request, result.get("error") or "Could not save profile", "danger")
    else:
        flash(request, "Profile saved", "success")
    return RedirectResponse(
        url=request.url_for("profile_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
