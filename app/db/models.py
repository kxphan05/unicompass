from datetime import datetime

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    alevel: dict[str, str]  # e.g. {"H2 Math": "A", "H2 Physics": "B"}
    ccas: list[str] = []
    course: str  # preferred course e.g. "Computer Science"
    citizenship: str = "Singaporean"
    additional_comments: str = ""  # learning style, preferences, etc.
    resume_text: str = ""
    resume_path: str = ""


class StudentProfileResponse(StudentProfile):
    id: str


class DebateCreate(BaseModel):
    profile_id: str
    agents: list[str] = Field(min_length=2, description="Agent keys, e.g. ['NUS', 'NTU']")


class DebateSession(BaseModel):
    id: str
    profile_id: str
    agents: list[str]
    status: str = "pending"  # pending | running | completed | error
    summary: str | None = None
    created_at: datetime


class Message(BaseModel):
    id: str
    debate_id: str
    agent: str
    content: str
    round: str
    sources: list[str] = []
    created_at: datetime


class QuestionRequest(BaseModel):
    content: str


class Scholarship(BaseModel):
    id: str
    university: str
    name: str
    bond_years: int | None = None
    citizenship: list[str] = []
    url: str = ""
    notes: str = ""
