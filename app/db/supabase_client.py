import os
import uuid
from datetime import datetime, timezone

from supabase import Client, create_client

from app.db.models import StudentProfile

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


def upload_resume(profile_id: str, file_bytes: bytes) -> str:
    """Upload a PDF to the 'resumes' bucket. Returns the storage path."""
    path = f"{profile_id}.pdf"
    get_client().storage.from_("resumes").upload(
        path,
        file_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )
    return path


def update_profile_resume(profile_id: str, resume_text: str, resume_path: str) -> dict:
    """Update the profile row with extracted resume text and file path."""
    result = (
        get_client()
        .table("profiles")
        .update({"resume_text": resume_text, "resume_path": resume_path})
        .eq("id", profile_id)
        .execute()
    )
    return result.data[0]


def save_profile(profile: StudentProfile) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "alevel": profile.alevel,
        "ccas": profile.ccas,
        "course": profile.course,
        "citizenship": profile.citizenship,
        "additional_comments": profile.additional_comments,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = get_client().table("profiles").insert(row).execute()
    return result.data[0]


def get_profile(profile_id: str) -> dict | None:
    result = get_client().table("profiles").select("*").eq("id", profile_id).execute()
    return result.data[0] if result.data else None


def create_debate(profile_id: str, agents: list[str]) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "profile_id": profile_id,
        "agents": agents,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = get_client().table("debates").insert(row).execute()
    return result.data[0]


def add_message(
    debate_id: str,
    agent: str,
    content: str,
    round: str,
    sources: list[str] | None = None,
) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "debate_id": debate_id,
        "agent": agent,
        "content": content,
        "round": round,
        "sources": sources or [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = get_client().table("messages").insert(row).execute()
    return result.data[0]


def get_messages(debate_id: str) -> list[dict]:
    result = (
        get_client()
        .table("messages")
        .select("*")
        .eq("debate_id", debate_id)
        .order("created_at")
        .execute()
    )
    return result.data


def get_debate(debate_id: str) -> dict | None:
    result = get_client().table("debates").select("*").eq("id", debate_id).execute()
    return result.data[0] if result.data else None


def update_debate_status(
    debate_id: str, status: str, summary: str | None = None
) -> dict:
    update = {"status": status}
    if summary is not None:
        update["summary"] = summary
    result = (
        get_client().table("debates").update(update).eq("id", debate_id).execute()
    )
    return result.data[0]


def get_scholarships(
    university: str | None = None,
    citizenship: str | None = None,
) -> list[dict]:
    """Fetch scholarships, optionally filtered by university and/or citizenship."""
    query = get_client().table("scholarships").select("*")
    if university:
        query = query.eq("university", university)
    if citizenship:
        query = query.contains("citizenship", [citizenship])
    result = query.order("university").execute()
    return result.data
