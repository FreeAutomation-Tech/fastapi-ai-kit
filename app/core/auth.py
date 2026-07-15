from fastapi import Header, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN

from app.config import settings

security = HTTPBearer(auto_error=False)


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    if not settings.api_key:
        return "anonymous"
    if not credentials:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API key required")
    if credentials.credentials != settings.api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return credentials.credentials
