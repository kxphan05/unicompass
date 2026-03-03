import os

import httpx

from app.db.models import StudentProfile

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
JUDGE_MODEL = "openrouter/free"


def _build_system_prompt(profile: StudentProfile) -> str:
    grades = ", ".join(f"{k}: {v}" for k, v in profile.alevel.items())
    return f"""You are a neutral university admissions advisor summarizing a debate between
Singapore university ambassadors. You are fair, objective, and student-focused.

Student profile:
- A-Level grades: {grades}
- CCAs: {', '.join(profile.ccas) if profile.ccas else 'None listed'}
- Preferred course: {profile.course}
- Citizenship: {profile.citizenship}
- Additional comments: {profile.additional_comments if profile.additional_comments else 'None provided'}
- Resume: {profile.resume_text if profile.resume_text else 'Not provided'}

Your job:
1. Summarize each university's key arguments objectively.
2. Highlight the pros and cons of each university relative to THIS student's profile.
3. Give a personalized recommendation — which university is the best fit and why.
4. Note any claims that seemed unsupported or exaggerated.

Be concise but thorough (300-400 words). Use bullet points for clarity."""


async def judge_summarize(profile: StudentProfile, debate_history: str) -> str:
    system_prompt = _build_system_prompt(profile)

    user_message = f"""Here is the full debate transcript:

{debate_history}

Now provide your objective summary and recommendation."""

    api_key = os.getenv("OPENROUTER_API_KEY", "")

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": JUDGE_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 2048,
            },
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]
