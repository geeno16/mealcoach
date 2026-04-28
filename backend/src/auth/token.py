import os
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

_SECRET_KEY = os.getenv("SECRET_KEY")
_ALGORITHM = os.getenv("ALGORITHM")
_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if not all([_SECRET_KEY, _ALGORITHM, _ACCESS_TOKEN_EXPIRE_MINUTES]):
    raise RuntimeError(
        "Missing required environment variables: SECRET_KEY, ALGORITHM, "
        "ACCESS_TOKEN_EXPIRE_MINUTES"
    )

_TOKEN_TTL = timedelta(minutes=int(_ACCESS_TOKEN_EXPIRE_MINUTES))  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]


def create_access_token(data: dict[str, Any]) -> str:
    payload = {**data, "exp": datetime.now(UTC) + _TOKEN_TTL}
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
