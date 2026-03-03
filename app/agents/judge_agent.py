import json
import os
import re

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

Be concise but thorough (300-400 words). Use bullet points for clarity.

IMPORTANT: After your prose summary, you MUST append a fenced JSON block with structured pros and cons for each university discussed. Use exactly this format:

```json
{{"pros_cons": {{"UniversityKey": {{"pros": ["pro 1", "pro 2"], "cons": ["con 1", "con 2"]}}, ...}}}}
```

Replace "UniversityKey" with the actual university abbreviation (e.g. NUS, NTU). Include 2-4 pros and 2-4 cons per university based on the debate."""


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


def parse_pros_cons(summary: str) -> dict | None:
    """Extract the JSON pros_cons block from the Judge's response."""
    match = re.search(r"```json\s*(\{.*\})\s*```", summary, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        return data.get("pros_cons")
    except (json.JSONDecodeError, AttributeError):
        return None


def strip_json_block(summary: str) -> str:
    """Remove the fenced JSON block from the Judge's response for display."""
    return re.sub(r"\s*```json\s*\{.*\}\s*```\s*", "", summary, flags=re.DOTALL).strip()
