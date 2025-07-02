import json
import os
from typing import Any

import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import Depends, Request, Response

from backend.values import RedisData


class SessionData:
    def __init__(
        self,
        redis,
        session_id: str,
        data: dict,
        response: Response,
        is_new: bool = False,
    ):
        self._redis = redis
        self._session_id = session_id
        self._data = data
        self._response = response
        self._is_new = is_new

        if self._is_new:
            self._set_cookie()

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

    def _set_cookie(self):
        self._response.set_cookie(
            key=RedisData.SESSION_COOKIE_NAME,
            value=self._session_id,
            max_age=RedisData.SESSION_EXPIRE_IN_1_DAY,
            httponly=True,
            samesite="lax",
        )

    async def _save(self):
        await self._redis.set(
            self._session_id,
            json.dumps(self._data),
            ex=RedisData.SESSION_EXPIRE_IN_1_DAY,
        )
        self._set_cookie()

    # Optional explicit save if you want
    async def save(self):
        await self._save()


async def get_redis():
    load_dotenv()
    return redis.from_url(os.environ.get("REDIS_URL"))


async def get_session_data(
    request: Request, response: Response, redis=Depends(get_redis)
) -> SessionData:
    session_id = request.cookies.get(RedisData.SESSION_COOKIE_NAME)
    if not session_id:
        import uuid

        session_id = str(uuid.uuid4())
        await redis.set(
            session_id, json.dumps({}), ex=RedisData.SESSION_EXPIRE_IN_1_DAY
        )
        data = {}
        is_new = True
    else:
        raw = await redis.get(session_id)
        data = json.loads(raw) if raw else {}
        is_new = False

    request.state.session_id = session_id
    return SessionData(redis, session_id, data, response, is_new=is_new)
