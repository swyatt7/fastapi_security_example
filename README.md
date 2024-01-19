# fastapi_security_example

Quick demo to generate a jwt with scopes that are validated by a simple API endpoint using the `FastAPI.security` library.

To run:

```bash
#new python3.10 environment
python -m pip install -r requirements.txt
uvicorn api:app --reload
```

This will launch an api example on local environment: http://127.0.0.1:8000

It serves two endpoints:

*   `http://127.0.0.1:8000/generate_jwt` -> returns a simple jwt bearer token
*   `http://127.0.0.1:8000/read_foo` -> accepts a query parameter "token". Thus appending the jwt from the first endpoint as: `http://127.0.0.1:8000/read_foo?token=<jwt>`.

The `/read_foo/` endpoint is decorated by the FastAPI Security dependency enjection and is validated with the custom `auth.authenticate()` function, and the endpoint accepted scopes defined in `app_scopes.API_SCOPE_DICT`.
