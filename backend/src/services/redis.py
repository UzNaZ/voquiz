import json
import os
from typing import Any

import redis.asyncio as redis
from fastapi import Depends, Request, Response

from backend.values import RedisData

_redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
)


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
        self._cookie_set = False

        if self._is_new:
            self._set_cookie()

    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value
        # No auto-save! Call save() explicitly after all modifications.

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default=None) -> Any:
        return self._data.get(key, default)

    def _set_cookie(self):
        if not self._cookie_set:
            self._response.set_cookie(
                key=RedisData.SESSION_COOKIE_NAME,
                value=self._session_id,
                max_age=RedisData.SESSION_EXPIRE_IN_2_HOURS,
                httponly=True,
                samesite="lax",
            )
            self._cookie_set = True

    async def save(self):
        try:
            await self._redis.set(
                self._session_id,
                json.dumps(self._data),
                ex=RedisData.SESSION_EXPIRE_IN_2_HOURS,
            )
            # Only set cookie if session is new or explicitly requested
            if self._is_new:
                self._set_cookie()
        except Exception as e:
            print(f"[SessionData] Redis save error: {e}")

    async def clear(self):
        try:
            await self._redis.delete(self._session_id)
            self._response.delete_cookie(RedisData.SESSION_COOKIE_NAME)
            self._data.clear()
        except Exception as e:
            print(f"[SessionData] Redis clear error: {e}")

    def set_cookie_on(self, response: Response):
        response.set_cookie(
            key=RedisData.SESSION_COOKIE_NAME,
            value=self._session_id,
            max_age=RedisData.SESSION_EXPIRE_IN_2_HOURS,
            httponly=True,
            samesite="lax",
        )


def get_redis():
    return _redis_client


async def get_session_data(
    request: Request, response: Response, redis=Depends(get_redis)
) -> SessionData:
    session_id = request.cookies.get(RedisData.SESSION_COOKIE_NAME)
    if not session_id:
        import uuid

        session_id = str(uuid.uuid4())
        try:
            await redis.set(
                session_id, json.dumps({}), ex=RedisData.SESSION_EXPIRE_IN_2_HOURS
            )
        except Exception as e:
            print(f"[get_session_data] Redis set error: {e}")
        data = {}
        is_new = True
    else:
        try:
            raw = await redis.get(session_id)
            data = json.loads(raw) if raw else {}
        except Exception as e:
            print(f"[get_session_data] Redis get error: {e}")
            data = {}
        is_new = False

    request.state.session_id = session_id
    return SessionData(redis, session_id, data, response, is_new=is_new)
