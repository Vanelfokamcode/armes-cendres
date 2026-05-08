import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_acled_token():
    resp = requests.post(
        "https://acleddata.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username":   os.getenv("ACLED_EMAIL"),
            "password":   os.getenv("ACLED_PASSWORD"),
            "grant_type": "password",
            "client_id":  "acled",
            "scope":      "authenticated"
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

if __name__ == "__main__":
    token = get_acled_token()
    print(f"Token OK : {token[:20]}...")
