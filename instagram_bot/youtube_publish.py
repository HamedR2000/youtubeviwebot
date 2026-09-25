"""YouTube Data API v3 client: upload an already-rendered local video file
as a Short on the dedicated YouTube channel.

Unlike Instagram's Graph API (which fetches media from a public URL),
YouTube's upload endpoint needs the raw video bytes, so this always takes
a local file path -- main.py downloads the already-hosted reel from its
GitHub Release URL first (see stock_media.download_video), then hands the
local copy here.

Auth is OAuth 2.0 with a long-lived refresh token (minted once, locally,
via youtube_auth_setup.py) rather than Meta-style long-lived access
tokens -- YouTube access tokens are short-lived, so every run exchanges
the refresh token for a fresh one first.
"""
import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


class YouTubePublishError(Exception):
    pass


def _raise_for_error(resp: requests.Response) -> None:
    if resp.status_code >= 400:
        raise YouTubePublishError(f"YouTube API error {resp.status_code}: {resp.text}")


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    resp = requests.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }, timeout=30)
    _raise_for_error(resp)
    return resp.json()["access_token"]


def upload_short(access_token: str, video_path: str, title: str, description: str,
                  category_id: str = "22", privacy_status: str = "public") -> str:
    """Uploads video_path as a public video via the resumable-upload
    protocol (a single PUT, since Shorts are small enough not to need
    chunking) and returns the new video's id. YouTube auto-detects the
    Shorts shelf from aspect ratio (<=1:1... actually vertical) + duration
    (<=60s) -- our Reels are already 1080x1920 and <=15s, so no
    re-encoding is needed, just the upload."""
    metadata = {
        "snippet": {"title": title[:100], "description": description, "categoryId": category_id},
        "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False},
    }
    init_resp = requests.post(
        UPLOAD_URL,
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"},
        json=metadata,
        timeout=30,
    )
    _raise_for_error(init_resp)
    upload_session_url = init_resp.headers["Location"]

    with open(video_path, "rb") as f:
        video_bytes = f.read()
    put_resp = requests.put(
        upload_session_url,
        headers={"Content-Type": "video/mp4"},
        data=video_bytes,
        timeout=300,
    )
    _raise_for_error(put_resp)
    return put_resp.json()["id"]
