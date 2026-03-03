from fastapi import APIRouter, Query

from app.db.supabase_client import get_scholarships

router = APIRouter(prefix="/api/scholarships", tags=["scholarships"])


@router.get("/")
async def list_scholarships(
    university: str | None = Query(None, description="Filter by university key (e.g. NUS)"),
    citizenship: str | None = Query(None, description="Filter by eligible citizenship"),
):
    """List scholarships, optionally filtered by university and citizenship."""
    data = get_scholarships(university=university, citizenship=citizenship)
    return {"data": data}
