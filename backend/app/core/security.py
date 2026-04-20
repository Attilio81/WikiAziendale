from fastapi import Header, HTTPException, status
from app.config import get_settings


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != get_settings().API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key non valida",
        )
