"""آپلود به یوتیوب با YouTube Data API v3 (OAuth، فلوی Installed App) برای
فایل نهایی Shorts. برای ساخت OAuth client توی Google Cloud Console به
README.md بخش "راه‌اندازی یوتیوب" نگاه کن -- این قدم رو باید یه‌بار خودت
دستی انجام بدی، این ماژول فقط از اون به بعد با API کار می‌کنه.

نکته‌ی quota: quota روزانه‌ی پیش‌فرض یه پروژه‌ی جدید Cloud (۱۰,۰۰۰ واحد)
حدود ۶ آپلود در روز رو پوشش می‌ده (هر آپلود ~۱۶۰۰ واحد) -- توی README.md
توضیح داده شده.
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
                    f"فایل {config.YOUTUBE_CLIENT_SECRETS_FILE} پیدا نشد. "
                    "طبق README.md بخش 'راه‌اندازی یوتیوب' یه OAuth client توی "
                    "Google Cloud Console بساز و دانلودش کن."
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
    """فایل file_path رو به‌عنوان یه YouTube Short آپلود می‌کنه. آی‌دی ویدیوی
    جدید رو برمی‌گردونه، یا در حالت dry_run هیچی به گوگل فرستاده نمی‌شه و
    None برمی‌گرده."""
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
        print("[dry-run] چیزی که به یوتیوب آپلود می‌شد:")
        print(f"  فایل: {file_path}")
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
            print(f"آپلود شده: {int(status.progress() * 100)}٪")

    video_id = response["id"]
    print(f"آپلود کامل شد: https://youtube.com/shorts/{video_id}")
    return video_id
