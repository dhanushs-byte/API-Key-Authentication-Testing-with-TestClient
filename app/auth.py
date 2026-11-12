
import secrets
from fastapi import Header, HTTPException, Depends

from app.database import hash_api_key, increment_request
from app.dependencies import get_user_by_hash


def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="x-api-key")
):
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing"
        )

    received_hash = hash_api_key(x_api_key)

    user = get_user_by_hash(received_hash)

    if not user or not secrets.compare_digest(
        received_hash,
        user["key_hash"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    increment_request(user["id"])

    return user
