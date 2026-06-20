"""Admin portal backend routes for LUMI.

All routes require an admin or dev role (require_admin dependency).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import require_admin
from app.services.supabase_service import SupabaseRestClient, get_supabase_client

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log_admin_action(admin_id: str, action: str, target_user_id: str | None = None, details: dict | None = None) -> None:
    client = get_supabase_client()
    try:
        client.table("admin_audit_log").insert({
            "admin_id": admin_id,
            "action": action,
            "target_user_id": target_user_id,
            "details": details or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass  # Audit logging is best-effort


def _has_auth_admin_api(client: Any) -> bool:
    """Return True if the client supports auth.admin methods."""
    return hasattr(client, "auth") and hasattr(client.auth, "admin")


def _auth_user_to_dict(u: Any) -> dict:
    """Normalise a Supabase AuthUser (or dict fallback) to a plain dict."""
    if isinstance(u, dict):
        return {
            "id": u.get("id"),
            "email": u.get("email"),
            "created_at": u.get("created_at"),
            "email_confirmed_at": u.get("email_confirmed_at"),
            "last_sign_in_at": u.get("last_sign_in_at"),
        }
    return {
        "id": getattr(u, "id", None),
        "email": getattr(u, "email", None),
        "created_at": getattr(u, "created_at", None),
        "email_confirmed_at": getattr(u, "email_confirmed_at", None),
        "last_sign_in_at": getattr(u, "last_sign_in_at", None),
    }


# ---------------------------------------------------------------------------
# User Management — List
# ---------------------------------------------------------------------------

@router.get("/users")
async def list_users(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return a paginated list of users with roles, profiles and real emails."""
    client = get_supabase_client()

    profiles_resp = client.table("profiles").select("*").execute()
    profiles = profiles_resp.data or []

    roles_resp = client.table("user_roles").select("user_id, role").execute()
    roles = {r["user_id"]: r["role"] for r in (roles_resp.data or [])}

    # Try to enrich with real emails via Auth Admin API
    emails: dict[str, str] = {}
    if _has_auth_admin_api(client):
        try:
            auth_resp = client.auth.admin.list_users()
            auth_users = auth_resp.users if hasattr(auth_resp, "users") else (auth_resp.data or {}).get("users", [])
            for u in auth_users:
                ud = _auth_user_to_dict(u)
                emails[ud["id"]] = ud["email"] or ""
        except Exception:
            pass

    users = []
    for p in profiles:
        uid = p.get("id")
        users.append({
            "id": uid,
            "full_name": p.get("full_name"),
            "email": emails.get(uid, uid),
            "role": roles.get(uid, "user"),
            "plan": p.get("plan", "free"),
            "is_active": p.get("is_active", True),
            "created_at": p.get("created_at"),
        })

    _log_admin_action(user.get("sub"), "list_users")
    return {"users": users}


# ---------------------------------------------------------------------------
# User Management — Create
# ---------------------------------------------------------------------------

@router.post("/users")
async def create_user(
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Admin creates a new user account.

    Payload:
        email: str (required)
        full_name: str (optional)
        role: "user" | "admin" | "dev" (default "user")
        plan: "free" | "premium" (default "free")
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    client = get_supabase_client()
    if not _has_auth_admin_api(client):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth Admin API not available. Check SUPABASE_SERVICE_ROLE_KEY.",
        )

    temp_password = secrets.token_urlsafe(12)
    role = payload.get("role", "user")
    # Admins and devs are always premium
    plan = "premium" if role in ("admin", "dev") else payload.get("plan", "free")
    full_name = payload.get("full_name", "")

    try:
        auth_resp = client.auth.admin.create_user({
            "email": email,
            "password": temp_password,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name},
        })
        new_user = auth_resp.user if hasattr(auth_resp, "user") else (auth_resp.data or {}).get("user")
        user_id = new_user.id if hasattr(new_user, "id") else new_user.get("id")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create user: {exc}") from exc

    # Upsert profile + role (trigger may have already created them)
    try:
        client.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "plan": plan,
            "is_active": True,
        }).execute()
    except Exception:
        pass

    try:
        client.table("user_roles").upsert({
            "user_id": user_id,
            "role": role,
        }).execute()
    except Exception:
        pass

    _log_admin_action(
        admin_user.get("sub"),
        "create_user",
        target_user_id=user_id,
        details={"email": email, "role": role, "plan": plan},
    )
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "plan": plan,
        "temp_password": temp_password,
        "message": "User created. Share the temp password or have them use Forgot Password.",
    }


# ---------------------------------------------------------------------------
# User Management — Single User Detail
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return full profile, role and auth metadata for a single user."""
    client = get_supabase_client()

    profile_resp = client.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_resp.data or {}

    role_resp = client.table("user_roles").select("role").eq("user_id", user_id).single().execute()
    role = (role_resp.data or {}).get("role", "user") if role_resp.data else "user"

    # Try to get real email + auth metadata
    auth_info = {}
    if _has_auth_admin_api(client):
        try:
            auth_resp = client.auth.admin.get_user_by_id(user_id)
            u = auth_resp.user if hasattr(auth_resp, "user") else (auth_resp.data or {}).get("user")
            auth_info = _auth_user_to_dict(u)
        except Exception:
            pass

    _log_admin_action(admin_user.get("sub"), "view_user", target_user_id=user_id)
    return {
        "id": user_id,
        "profile": profile,
        "role": role,
        "email": auth_info.get("email"),
        "created_at": auth_info.get("created_at") or profile.get("created_at"),
        "last_sign_in_at": auth_info.get("last_sign_in_at"),
        "email_confirmed": bool(auth_info.get("email_confirmed_at")),
    }


# ---------------------------------------------------------------------------
# User Management — Ban / Unban
# ---------------------------------------------------------------------------

@router.post("/users/{user_id}/ban")
async def toggle_user_ban(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Toggle is_active on a user's profile (soft ban / unban)."""
    client = get_supabase_client()

    profile_resp = client.table("profiles").select("is_active").eq("id", user_id).single().execute()
    profile = profile_resp.data or {}
    current = profile.get("is_active", True)
    new_state = not current

    client.table("profiles").update({"is_active": new_state}).eq("id", user_id).execute()

    action = "unban_user" if new_state else "ban_user"
    _log_admin_action(admin_user.get("sub"), action, target_user_id=user_id, details={"is_active": new_state})
    return {"id": user_id, "is_active": new_state, "action": action}


# ---------------------------------------------------------------------------
# User Management — Change Role
# ---------------------------------------------------------------------------

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Change a user's role (user / admin / dev). Admins/devs are always premium."""
    new_role = payload.get("role")
    if new_role not in ("user", "admin", "dev"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    client = get_supabase_client()
    client.table("user_roles").update({"role": new_role}).eq("user_id", user_id).execute()

    # Auto-sync plan: admin/dev → premium, user → free
    new_plan = "premium" if new_role in ("admin", "dev") else "free"
    client.table("profiles").update({"plan": new_plan}).eq("id", user_id).execute()

    _log_admin_action(
        admin_user.get("sub"),
        "change_role",
        target_user_id=user_id,
        details={"new_role": new_role, "auto_plan": new_plan},
    )
    return {"id": user_id, "role": new_role, "plan": new_plan}


# ---------------------------------------------------------------------------
# User Management — Change Plan
# ---------------------------------------------------------------------------

@router.put("/users/{user_id}/plan")
async def update_user_plan(
    user_id: str,
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Change a user's plan (free / premium)."""
    new_plan = payload.get("plan")
    if not new_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan is required")

    client = get_supabase_client()
    client.table("profiles").update({"plan": new_plan}).eq("id", user_id).execute()

    _log_admin_action(
        admin_user.get("sub"),
        "change_plan",
        target_user_id=user_id,
        details={"new_plan": new_plan},
    )
    return {"id": user_id, "plan": new_plan}


# ---------------------------------------------------------------------------
# User Management — User's Saved Simulations
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/simulations")
async def get_user_simulations(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return all saved simulations for a user."""
    client = get_supabase_client()
    resp = (
        client.table("saved_simulations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    _log_admin_action(admin_user.get("sub"), "view_user_simulations", target_user_id=user_id)
    return {"simulations": resp.data or []}


# ---------------------------------------------------------------------------
# User Management — Usage Report
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/reports")
async def get_user_report(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return aggregated usage statistics for a single user."""
    client = get_supabase_client()

    sims_resp = (
        client.table("saved_simulations")
        .select("id, municipality_id, name, created_at", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    sims = sims_resp.data or []
    total_simulations = sims_resp.count or len(sims)

    chat_resp = (
        client.table("chat_sessions")
        .select("id, created_at", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    chats = chat_resp.data or []
    total_chat_sessions = chat_resp.count or len(chats)

    # Most-searched municipality
    municipality_counts: dict[str, int] = {}
    for s in sims:
        mid = s.get("municipality_id")
        if mid:
            municipality_counts[str(mid)] = municipality_counts.get(str(mid), 0) + 1
    peak_municipality_id = max(municipality_counts, key=municipality_counts.get) if municipality_counts else None

    # Last activity
    all_dates = [s.get("created_at") for s in sims] + [c.get("created_at") for c in chats]
    valid_dates = [d for d in all_dates if d]
    last_active = max(valid_dates) if valid_dates else None

    _log_admin_action(admin_user.get("sub"), "view_user_report", target_user_id=user_id)
    return {
        "user_id": user_id,
        "total_simulations": total_simulations,
        "total_chat_sessions": total_chat_sessions,
        "peak_municipality_id": peak_municipality_id,
        "last_active": last_active,
        "recent_simulations": sims[:5],
    }


# ---------------------------------------------------------------------------
# User Management — Soft Delete
# ---------------------------------------------------------------------------

@router.delete("/users/{user_id}")
async def soft_delete_user(
    user_id: str,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Soft-delete a user: ban + anonymise profile + log action.
    Hard-delete from auth.users is optional and requires the Auth Admin API."""
    client = get_supabase_client()

    # 1. Ban
    client.table("profiles").update({"is_active": False}).eq("id", user_id).execute()

    # 2. Anonymise
    client.table("profiles").update({
        "full_name": "Deleted User",
        "avatar_url": None,
        "organization": None,
        "location": None,
    }).eq("id", user_id).execute()

    _log_admin_action(admin_user.get("sub"), "soft_delete_user", target_user_id=user_id)
    return {"id": user_id, "status": "soft_deleted", "message": "User banned and anonymised. Data retained for audit."}


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get("/analytics")
async def get_analytics(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return system-level analytics."""
    client = get_supabase_client()

    users_resp = client.table("profiles").select("id, plan, is_active", count="exact").execute()
    all_profiles = users_resp.data or []
    total_users = users_resp.count or len(all_profiles)
    active_users = sum(1 for u in all_profiles if u.get("is_active", True))
    banned_users = total_users - active_users

    sims_resp = client.table("saved_simulations").select("id", count="exact").execute()
    total_simulations = sims_resp.count or 0

    chat_resp = client.table("chat_sessions").select("id", count="exact").execute()
    total_chat_sessions = chat_resp.count or 0

    free_users = sum(1 for u in all_profiles if u.get("plan") == "free")
    premium_users = sum(1 for u in all_profiles if u.get("plan") != "free")

    _log_admin_action(user.get("sub"), "view_analytics")
    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "total_simulations": total_simulations,
        "total_chat_sessions": total_chat_sessions,
        "free_users": free_users,
        "premium_users": premium_users,
    }


# ---------------------------------------------------------------------------
# System Config
# ---------------------------------------------------------------------------

@router.post("/config")
async def update_config(
    payload: dict,
    admin_user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Update system configuration toggles."""
    client = get_supabase_client()
    try:
        client.table("system_config").upsert({
            "key": "global",
            "value": payload,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass

    _log_admin_action(admin_user.get("sub"), "update_config", details=payload)
    return {"status": "ok", "config": payload}


@router.get("/config")
async def get_config(user: dict = Depends(require_admin)) -> dict[str, Any]:
    """Return current system configuration."""
    client = get_supabase_client()
    try:
        resp = client.table("system_config").select("value").eq("key", "global").single().execute()
        return resp.data.get("value", {}) if resp.data else {}
    except Exception:
        return {
            "chatbot_enabled": True,
            "maintenance_mode": False,
            "free_chat_limit": 5,
            "free_sim_limit": 3,
        }


# ---------------------------------------------------------------------------
# Moderation: Chat Sessions
# ---------------------------------------------------------------------------

@router.get("/chat-sessions")
async def list_chat_sessions(
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Return recent chat sessions for moderation review."""
    client = get_supabase_client()
    resp = (
        client.table("chat_sessions")
        .select("*, chat_messages(*)")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    _log_admin_action(user.get("sub"), "view_chat_sessions")
    return {"sessions": resp.data or []}


@router.post("/chat-sessions/{session_id}/flag")
async def flag_chat_session(
    session_id: str,
    payload: dict,
    user: dict = Depends(require_admin),
) -> dict[str, Any]:
    """Flag or unflag a chat session."""
    is_flagged = payload.get("is_flagged", True)
    client = get_supabase_client()
    client.table("chat_sessions").update({"is_flagged": is_flagged}).eq("id", session_id).execute()
    _log_admin_action(user.get("sub"), "flag_chat_session", details={"session_id": session_id, "is_flagged": is_flagged})
    return {"session_id": session_id, "is_flagged": is_flagged}
