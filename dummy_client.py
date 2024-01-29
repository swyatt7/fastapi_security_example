import requests
import os

HOST = "http://localhost:8000"

class dummy_client:
    def __init__(self, client_id=None, client_secret=None, access_token=None):
        self.client_id = client_id,
        self.client_secret = client_secret
        self.access_token = access_token

        #client credential flow - grab token from api
        if (self.client_id and self.client_secret):
            request_json = {
                "client_id":self.client_id,
                "client_secret":self.client_secret
            }

            token_url = f"{HOST}/auth/token/"
            token_response = requests.post(
                token_url, 
                params = request_json
            )
            token_response.raise_for_status()
            token_response_json = token_response.json()
            self._access_token = token_response_json["access_token"]

        #access token already provided
        elif self.access_token:
            self._access_token = self.access_token

        #set auth headers
        self.headers = {
            f"accept": "application/json",
            f"Authorization": f"Bearer {self._access_token}"
        }

        #verify the bearer token, and raise if not
        verification_url = f"{HOST}/auth/verify/"
        verification_response = requests.get(
            verification_url,
            headers = self.headers
        )
        verification_response.raise_for_status()
        

    def read_foo(self):
        url = f"{HOST}/read_foo/"
        response = requests.get(
            url,
            headers = self.headers
        )
        print(response.text)


if __name__ == "__main__":
    dc = dummy_client(
        client_id=os.environ.get("TEST_CLIENT_ID"),
        client_secret=os.environ.get("TEST_CLIENT_SECRET")
    )

    dc.read_foo()