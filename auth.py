
from fastapi import Request, HTTPException, status
from fastapi.security import (
    SecurityScopes,
)
from jose import JWTError, jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def authenticate(security_scopes: SecurityScopes, request: Request):
    valid = False
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # retrieve the token from the request params
    try:
        if "token" in request.query_params:
            token = request.query_params["token"]
        elif "token" in request.json.keys():
            token = request.json["token"]
        else:
            raise
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="bearer token is a required query/json parameter",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # decode the JWT token, and retrieve user token scopes
    # we can also validate jwt.exp and jwt.sup here as well
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_scopes = payload.get("scopes", [])
    except (JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check if user scopes is in endpoint scope
    for role in token_scopes:
        if role in security_scopes.scopes:
            valid = True

    # raise exception if user.role not in endpoint scope
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token scope(s) not in endpoint scope",
            headers={"WWW-Authenticate": "Bearer"},
        )