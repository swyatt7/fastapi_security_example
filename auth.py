
from fastapi import Request, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)
import os
from typing import Optional
import jwt
import requests  # type: ignore


class JWTBearer(HTTPBearer):
    token_endpoint: str
    jwks_uri: str

    def __init__(self, **kwargs):
        # Configure URL from IdP
        user_pool_id = os.environ.get("COGNITO_USER_POOL_ID")
        if user_pool_id is not None:
            provider_url = f"https://cognito-idp.{user_pool_id.split('_')[0]}.amazonaws.com/{user_pool_id}/"
        elif os.environ.get("ARC_ENV") == "testing":
            provider_url = f"http://localhost:{os.environ.get('ARC_OIDC_IDP_PORT')}/"
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Environment variable COGNITO_USER_POOL_ID must be defined in production.",
            )

        # Fetch the well-known config from the IdP
        resp = requests.get(provider_url + ".well-known/openid-configuration")
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            HTTPException(status_code=500, detail=str(e))

        # Find the token endpoint and jwks_uri from the well-known config
        well_known = resp.json()
        self.token_endpoint = well_known["token_endpoint"]
        self.jwks_uri = well_known["jwks_uri"]
        self.token_alg = well_known["id_token_signing_alg_values_supported"]

        super().__init__(**kwargs)

    async def __call__(self, request: Request, security_scopes: SecurityScopes) -> None:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )

        valid = False

        """Validate credentials if passed"""
        if credentials:
            # Fetch signing key from Cognito
            jwks_client = jwt.PyJWKClient(self.jwks_uri)
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(
                    credentials.credentials
                )
            except Exception as e:
                raise HTTPException(
                    status_code=401, detail=f"Authentication error: {e}"
                )

            # Validate the credentials
            try:
                access_token = jwt.api_jwt.decode_complete(
                    credentials.credentials,
                    key=signing_key.key,
                    algorithms=self.token_alg,
                )
                scopes = access_token["payload"]["scope"]
            except jwt.InvalidSignatureError as e:
                raise HTTPException(
                    status_code=401, detail=f"Authentication error: {e}."
                )

            #assuming the jwt scopes will be comma separated
            token_scopes = scopes.split(",")
            
            # check if user scopes is in endpoint scope
            if len(security_scopes.scopes):
                for role in token_scopes:
                    if role in security_scopes.scopes:
                        valid = True    
            else: #endpoint has no scopes
                valid = True

            # raise exception if user.role not in endpoint scope
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Bearer token scope(s) not in endpoint scope",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token not found",
                headers={"WWW-Authenticate": "Bearer"},
            )


jwt_security = JWTBearer(
    scheme_name="ACROSS API Authorization",
    description="Enter your JWT authentication token obtained from /auth/token using GCN client_id and client_key.",
)