import os
import httpx

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {UPSTASH_TOKEN}"}


async def get_cache(key: str) -> str | None:
    if not UPSTASH_URL:
        return None
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UPSTASH_URL}/get/{key}", headers=_headers())
        result = r.json().get("result")
        return result if result else None


async def set_cache(key: str, value: str, ttl: int = 86400) -> None:
    if not UPSTASH_URL:
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{UPSTASH_URL}",
            headers={**_headers(), "Content-Type": "application/json"},
            json=["SET", key, value, "EX", ttl],
        )
