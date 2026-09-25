"""One-time LOCAL script -- run this yourself, once, on your own machine
(NOT in GitHub Actions, it needs a real browser). Mints the long-lived
refresh token that main.py's YouTube Shorts upload uses every day, so you
only ever have to do this once per channel.

Before running:
  1. Sign in to https://console.cloud.google.com with the Google account
     that owns the new dedicated YouTube channel.
  2. Create a project, enable the "YouTube Data API v3".
  3. OAuth consent screen: External, add that same Google account as a
     test user (fine to leave the app in "Testing" mode).
  4. Credentials -> Create Credentials -> OAuth client ID -> type
     "Desktop app". Copy the Client ID and Client secret it gives you.
  (Full walkthrough: README.md "YouTube Shorts setup".)

Then:
    pip install google-auth-oauthlib
    python youtube_auth_setup.py

A browser tab opens for you to log in (as the channel's account) and
approve access. Paste the resulting Client ID / secret / refresh token
into the repo's GitHub secrets as YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET
/ YOUTUBE_REFRESH_TOKEN.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    client_id = input("OAuth Client ID: ").strip()
    client_secret = input("OAuth Client secret: ").strip()

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        scopes=SCOPES,
    )
    credentials = flow.run_local_server(port=0)

    print("\nSave these as GitHub repo secrets:\n")
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")


if __name__ == "__main__":
    main()
