import json
from typing import Any
from fastapi import Request, Response, Depends
import redis.asyncio as redis

from backend.values import RedisData


class SessionData:
    def __init__(self, redis, session_id: str, data: dict, response: Response):
        self._redis = redis
        self._session_id = session_id
        self._data = data
        self._response = response

    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value
        # Save immediately on set
        import asyncio
        asyncio.create_task(self._save())

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default=None) -> Any:
        return self._data.get(key, default)

    async def _save(self):
        await self._redis.set(
            self._session_id,
            json.dumps(self._data),
            ex=RedisData.SESSION_EXPIRE_IN_1_DAY,
        )

    # Optional explicit save if you want
    async def save(self):
        await self._save()


async def get_redis():
    return redis.from_url("redis://localhost:6379")


async def get_session_data(request: Request, response: Response, redis=Depends(get_redis)) -> SessionData:
    session_id = request.cookies.get(RedisData.SESSION_COOKIE_NAME)
    if not session_id:
        # Create new session
        import uuid
        session_id = str(uuid.uuid4())
        await redis.set(session_id, json.dumps({}), ex=RedisData.SESSION_EXPIRE_IN_1_DAY)
        response.set_cookie(
            key=RedisData.SESSION_COOKIE_NAME,
            value=session_id,
            max_age=RedisData.SESSION_EXPIRE_IN_1_DAY,
            httponly=True,
            samesite="lax",
        )
        data = {}
    else:
        raw = await redis.get(session_id)
        data = json.loads(raw) if raw else {}
    # Attach session_id to request state (optional)
    request.state.session_id = session_id
    return SessionData(redis, session_id, data, response)
