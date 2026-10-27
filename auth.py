
import os

import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Verify the Supabase access token and return the authenticated user.

    The token is verified by Supabase Auth rather than trusted directly.
    """

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in to access this resource.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase authentication is not configured.",
        )

    try:
        response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_PUBLISHABLE_KEY,
                "Authorization": f"Bearer {credentials.credentials}",
            },
            timeout=15,
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Supabase Auth.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Your session is invalid or expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = response.json()
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Supabase returned an invalid user response.",
        )

    if not user.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Could not verify the authenticated user.",
        )

    return user
