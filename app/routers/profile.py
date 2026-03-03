import fitz
from fastapi import APIRouter, HTTPException, UploadFile

from app.db.models import StudentProfile, StudentProfileResponse
from app.db.supabase_client import (
    get_profile,
    save_profile,
    update_profile_resume,
    upload_resume,
)

router = APIRouter(prefix="/api", tags=["profile"])


@router.post("/profile", response_model=StudentProfileResponse)
async def create_profile(profile: StudentProfile):
    try:
        row = save_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return _row_to_response(row)


@router.get("/profile/{profile_id}", response_model=StudentProfileResponse)
async def read_profile(profile_id: str):
    row = get_profile(profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _row_to_response(row)


MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/profile/{profile_id}/resume", response_model=StudentProfileResponse)
async def upload_profile_resume(profile_id: str, file: UploadFile):
    row = get_profile(profile_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    # Extract text with pymupdf
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        resume_text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF")

    # Upload to Supabase Storage
    resume_path = upload_resume(profile_id, file_bytes)

    # Update profile row
    updated = update_profile_resume(profile_id, resume_text, resume_path)
    return _row_to_response(updated)


def _row_to_response(row: dict) -> StudentProfileResponse:
    return StudentProfileResponse(
        id=row["id"],
        alevel=row["alevel"],
        ccas=row["ccas"],
        course=row["course"],
        citizenship=row["citizenship"],
        additional_comments=row.get("additional_comments", ""),
        resume_text=row.get("resume_text", ""),
        resume_path=row.get("resume_path", ""),
    )
