
import token

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.token_service import verify_access_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Verify JWT and identify the authenticated user."""

    token = credentials.credentials
    print("Received token length:", len(token))
    print("Received token segments:", len(token.split(".")))    

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or role not in ("student", "instructor"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token information."
        )

    return {
        "user_id": int(user_id),
        "role": role
    }


def require_student(current_user=Depends(get_current_user)):
    """Allow access only to students."""

    if current_user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access only."
        )

    return current_user


def require_instructor(current_user=Depends(get_current_user)):
    """Allow access only to instructors."""

    if current_user["role"] != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor access only."
        )

    return current_user
