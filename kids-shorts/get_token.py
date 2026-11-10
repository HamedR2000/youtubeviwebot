"""One-time helper — run on YOUR computer (needs a browser) to get a permanent YouTube refresh token.

Prerequisites (see the step-by-step guide in the chat / README):
  - Google Cloud project with "YouTube Data API v3" enabled
  - OAuth app published to "In production" (in Testing mode tokens expire after 7 days)
  - OAuth client of type "Desktop app", downloaded as client_secret.json next to this file

Run:
  pip install google-auth-oauthlib google-api-python-client
  python3 get_token.py

In the browser: pick your Google account, then pick the NEW channel (not your old one),
then "Advanced" -> "Go to ... (unsafe)" -> Continue. Copy the three printed values into GitHub secrets.
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',  # only to confirm which channel was authorized
]

flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=SCOPES)
creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')

me = build('youtube', 'v3', credentials=creds, cache_discovery=False).channels().list(part='snippet', mine=True).execute()
for ch in me.get('items', []):
    print(f"\nAuthorized channel: {ch['snippet']['title']}  (id {ch['id']})")
print('\nIf that is NOT your new kids channel, run this script again and pick the right channel.\n')

print('YT_CLIENT_ID     =', creds.client_id)
print('YT_CLIENT_SECRET =', creds.client_secret)
print('YT_REFRESH_TOKEN =', creds.refresh_token)
