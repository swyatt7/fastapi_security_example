from fastapi import FastAPI
from datetime import datetime, timedelta, timezone

from fastapi import Security, FastAPI
from fastapi.security import (
    SecurityScopes,
)
from jose import jwt

from app_scopes import API_SCOPE_DICT
from auth import authenticate

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

#quick and easy way to get a valid jwt with custom scope
@app.get("/generate_jwt/")
async def generate_dummy_jwt(scope_example: str = "read:/"):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    data={
        "sub": "sunglass_coolguy", 
        "scopes": [scope_example],
        "exp": expire
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


#decoroate our endpoint with our authenticate function as a security dependency
@app.get("/read_foo/", dependencies=[Security(authenticate, scopes=API_SCOPE_DICT["/read_foo/"])])
async def read_foo():
    return [{"item": "Foo"}, {"item": "Bar"}]