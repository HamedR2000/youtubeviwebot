"""YouTube Data API v3 upload (OAuth, installed-app flow) for the composed
Shorts file. See README.md "راه‌اندازی یوتیوب" for how to create the OAuth
client in Google Cloud Console -- that step has to be done by hand once,
this module just drives the API afterwards.

Quota note: a new Cloud project's default daily quota (10,000 units) covers
about 6 uploads/day (each insert costs 1600 units) -- see README.md.
"""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import config


def _get_credentials() -> Credentials:
    creds = None
    if os.path.exists(config.YOUTUBE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            config.YOUTUBE_TOKEN_FILE, [config.YOUTUBE_UPLOAD_SCOPE]
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(config.YOUTUBE_CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"{config.YOUTUBE_CLIENT_SECRETS_FILE} not found. "
                    "See reaction_bot/README.md -> 'راه‌اندازی یوتیوب' to create "
                    "an OAuth client in Google Cloud Console and download it."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRETS_FILE, [config.YOUTUBE_UPLOAD_SCOPE]
            )
            creds = flow.run_local_server(port=0)
        with open(config.YOUTUBE_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags: list[str] | None = None,
    category_id: str | None = None,
    privacy_status: str | None = None,
    made_for_kids: bool = False,
    dry_run: bool = False,
) -> str | None:
    """Uploads file_path as a YouTube Short. Returns the new video id, or
    None in dry_run mode (nothing is sent to Google)."""
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id or config.DEFAULT_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": privacy_status or config.DEFAULT_PRIVACY_STATUS,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    if dry_run:
        print("[dry-run] Would upload to YouTube with:")
        print(f"  file: {file_path}")
        print(f"  body: {body}")
        return None

    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded: https://youtube.com/shorts/{video_id}")
    return video_id
