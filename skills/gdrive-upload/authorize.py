#!/usr/bin/env python3
"""
One-time Google Drive / Docs OAuth authorizer.

Run this once to turn your downloaded credentials.json into a token.json that
the upload scripts use. It opens a browser, you log in, and the token is saved.

Setup before running:
  1. Create a project at https://console.cloud.google.com/
  2. Enable the "Google Drive API" and "Google Docs API"
  3. APIs & Services -> Credentials -> Create OAuth client ID -> type "Desktop app"
  4. Download the JSON and save it as credentials.json in your config dir
     (default: ~/.claude/.gdrive/credentials.json)

Then run:
    python3 ~/.claude/skills/gdrive-upload/authorize.py

Override locations with env vars GDRIVE_CONFIG_DIR / GDRIVE_TOKEN_PATH /
GDRIVE_CREDENTIALS_PATH if you keep the files elsewhere.
"""

import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

CONFIG_DIR = os.environ.get(
    "GDRIVE_CONFIG_DIR", os.path.expanduser("~/.claude/.gdrive")
)
TOKEN_PATH = os.environ.get("GDRIVE_TOKEN_PATH", os.path.join(CONFIG_DIR, "token.json"))
CREDENTIALS_PATH = os.environ.get(
    "GDRIVE_CREDENTIALS_PATH", os.path.join(CONFIG_DIR, "credentials.json")
)


def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CREDENTIALS_PATH):
        sys.exit(
            f"No credentials file found at {CREDENTIALS_PATH}.\n"
            "Download an OAuth client ID (Desktop app) JSON from Google Cloud "
            "Console and save it there, then run this again. See the header of "
            "this file for the full steps."
        )

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    print(f"Authorized. Token saved to {TOKEN_PATH}")
    print("You can now use /gdrive-upload and /script-to-teleprompter.")


if __name__ == "__main__":
    main()
