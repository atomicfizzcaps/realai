from fastapi import Depends, Header, HTTPException, status

from .config import get_valid_api_keys

_valid_keys = get_valid_api_keys()


def require_api_key(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise _unauthorized("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized("Authorization header must use Bearer scheme")

    if token not in _valid_keys:
        raise _unauthorized("Invalid API key")

    return token


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
