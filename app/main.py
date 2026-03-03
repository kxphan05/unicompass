import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import debate, profile, scholarships

app = FastAPI(title="UniAdvisor API", version="0.2.0")

_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(debate.router)
app.include_router(scholarships.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}
