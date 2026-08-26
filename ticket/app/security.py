import os

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app import schemas

GATEWAY_SHARED_SECRET = os.getenv("GATEWAY_SHARED_SECRET", "change-me-gateway")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ISSUER = os.getenv("JWT_ISSUER", "ticket-service-auth")

security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    id: int
    username: str
    phone_number: str | None = None
    department: str | None = None


def _verify_gateway_auth(
    user_id: str | None = Header(default=None, alias="X-Authenticated-User-Id"),
    username: str | None = Header(default=None, alias="X-Authenticated-Username"),
    phone_number: str | None = Header(default=None, alias="X-Authenticated-Phone-Number"),
    department: str | None = Header(default=None, alias="X-Authenticated-Department"),
    gateway_secret: str | None = Header(default=None, alias="X-Gateway-Secret"),
) -> AuthenticatedUser:
    """Verify gateway-forwarded authentication headers."""
    if gateway_secret != GATEWAY_SHARED_SECRET:
        return None

    try:
        parsed_user_id = int(user_id or "")
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated user",
        )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated user",
        )

    return AuthenticatedUser(
        id=parsed_user_id,
        username=username,
        phone_number=phone_number,
        department=department,
    )


def _verify_jwt_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser | None:
    """Verify JWT token from Authorization header (dev mode)."""
    if not credentials:
        return None

    try:
        import jwt as pyjwt
        from datetime import datetime, timezone

        payload = pyjwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "iss", "sub"]},
        )
        if payload.get("iss") != JWT_ISSUER:
            return None

        return AuthenticatedUser(
            id=int(payload["sub"]),
            username=payload.get("username", ""),
            phone_number=payload.get("phone_number"),
            department=payload.get("department"),
        )
    except Exception:
        return None


def get_current_user(
    user_id: str | None = Header(default=None, alias="X-Authenticated-User-Id"),
    username: str | None = Header(default=None, alias="X-Authenticated-Username"),
    phone_number: str | None = Header(default=None, alias="X-Authenticated-Phone-Number"),
    department: str | None = Header(default=None, alias="X-Authenticated-Department"),
    gateway_secret: str | None = Header(default=None, alias="X-Gateway-Secret"),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> schemas.AuthenticatedUser:
    """Get current user from either gateway headers or JWT token."""
    # Try gateway auth first
    gw_user = _verify_gateway_auth(
        user_id=user_id,
        username=username,
        phone_number=phone_number,
        department=department,
        gateway_secret=gateway_secret,
    )
    if gw_user:
        return schemas.AuthenticatedUser(
            id=gw_user.id,
            username=gw_user.username,
            phone_number=gw_user.phone_number,
            department=gw_user.department,
        )

    # Fall back to JWT token (dev mode)
    jwt_user = _verify_jwt_token(credentials=credentials)
    if jwt_user:
        return schemas.AuthenticatedUser(
            id=jwt_user.id,
            username=jwt_user.username,
            phone_number=jwt_user.phone_number,
            department=jwt_user.department,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing gateway authentication",
    )