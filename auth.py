import os

from dotenv import load_dotenv
from supabase import create_client
from fastapi import Header, HTTPException

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_current_user(authentication: str | None = Header(default=None)):
    if authentication is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )
    if not authentication.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )
    token = authentication.removeprefix("Bearer ").strip()
    
    if token == "":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )
    
    try:
        response = supabase.auth.get_user(token)
        return response.user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

