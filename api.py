from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from authlib.integrations.httpx_client import AsyncOAuth2Client  # type: ignore
from authlib.integrations.base_client.errors import OAuthError

from fastapi import Security, Depends, HTTPException, Request, status
from fastapi.security import (
    SecurityScopes,
)
from pydantic import BaseModel

from app_scopes import API_SCOPE_DICT
from auth import jwt_security


class AuthToken(BaseModel):
    """Pydantic Model for OIDC Auth Token"""

    access_token: str
    expires_in: int
    token_type: str
    expires_at: int


class VerifyAuth(BaseModel):
    status: str = "success"

app = FastAPI()


@app.post("/auth/token/")
async def get_authentication_token(client_id: str, client_secret: str) -> AuthToken:
    """Obtain an authorization token using GCN credentials."""
    session = AsyncOAuth2Client(client_id, client_secret, scope={})
    try:
        token = await session.fetch_token(jwt_security.token_endpoint)
    except OAuthError:
        raise HTTPException(
            status_code=401, detail="Invalid client_id or client_secret."
        )
    return AuthToken(**token)


#decorate our endpoint with our jwt_security function as a security dependency
@app.get("/auth/verify/", dependencies=[Security(jwt_security, scopes=[])])
async def verify_authentication() -> VerifyAuth:
    """Verify that the user is authenticated."""
    return VerifyAuth()


#decorate our endpoint with our jwt_security function as a security dependency
@app.get("/read_foo/", dependencies=[Security(jwt_security, scopes=API_SCOPE_DICT["/read_foo/"])])
async def read_foo():
    return [{"item": "Foo"}, {"item": "Bar"}]
