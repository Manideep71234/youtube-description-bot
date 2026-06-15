import os
import base64
import json
import requests
from dotenv import dotenv_values
from nacl import encoding, public

# Replace with your details
GITHUB_TOKEN = "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"
REPO_OWNER = "Manideep71234"
REPO_NAME = "youtube-description-bot"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def encrypt(public_key: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def get_public_key():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def upload_secret(secret_name, secret_value, key_id, public_key):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    encrypted_value = encrypt(public_key, secret_value)
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Secret {secret_name} successfully set.")

def main():
    print("Fetching repository public key...")
    try:
        key_data = get_public_key()
    except Exception as e:
        print(f"Failed to fetch public key. Ensure the repo exists and PAT has 'repo' scope. Error: {e}")
        return

    key_id = key_data["key_id"]
    public_key = key_data["key"]

    print("Loading local secrets...")
    env_vars = dotenv_values(".env")
    
    # Base64 encode the token.pickle file
    with open("token.pickle", "rb") as f:
        token_b64 = base64.b64encode(f.read()).decode('utf-8')
        
    with open("client_secret.json", "r") as f:
        client_secret = f.read()

    secrets_to_upload = {
        "GEMINI_API_KEY": env_vars.get("GEMINI_API_KEY", ""),
        "YOUTUBE_CHANNEL_ID": env_vars.get("YOUTUBE_CHANNEL_ID", ""),
        "EMAIL_SENDER": env_vars.get("EMAIL_SENDER", ""),
        "EMAIL_PASSWORD": env_vars.get("EMAIL_PASSWORD", ""),
        "EMAIL_RECIPIENT": env_vars.get("EMAIL_RECIPIENT", ""),
        "YOUTUBE_TOKEN_PICKLE_B64": token_b64,
        "CLIENT_SECRET_JSON": client_secret
    }

    print("Uploading secrets to GitHub Actions...")
    for name, value in secrets_to_upload.items():
        if value:
            upload_secret(name, value, key_id, public_key)
        else:
            print(f"Warning: {name} is empty, skipping.")

    print("\nAll secrets uploaded successfully!")

if __name__ == "__main__":
    main()
