"""One-time helper — run on YOUR computer (needs a browser) to get a YouTube refresh token.

1. Google Cloud Console → new project → enable "YouTube Data API v3".
2. OAuth consent screen: External, add your Google account as a test user, then "Publish app"
   (in Testing mode refresh tokens expire after 7 days).
3. Credentials → Create OAuth client ID → "Desktop app" → download as client_secret.json next to this file.
4. pip install google-auth-oauthlib && python3 get_token.py
5. Save the three printed values as GitHub repo secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', scopes=['https://www.googleapis.com/auth/youtube.upload'])
creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
print('YT_CLIENT_ID     =', creds.client_id)
print('YT_CLIENT_SECRET =', creds.client_secret)
print('YT_REFRESH_TOKEN =', creds.refresh_token)
