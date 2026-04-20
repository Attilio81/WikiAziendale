from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import get_settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    if not x_api_key or x_api_key != get_settings().API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key non valida",
        )
