"""Environment-driven configuration for the reaction pipeline. Mirrors
instagram_bot/config.py's pattern: secrets/paths come from env vars (or a
local .env) so the same code runs on a laptop or a VPS with no edits.
"""
import os


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


class Config:
    # Where downloaded source clips, composed outputs and OAuth state live.
    WORK_DIR = _env("REACTION_WORK_DIR", os.path.join(os.path.dirname(__file__), "workdir"))

    @property
    def downloads_dir(self) -> str:
        path = os.path.join(self.WORK_DIR, "downloads")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def outputs_dir(self) -> str:
        path = os.path.join(self.WORK_DIR, "outputs")
        os.makedirs(path, exist_ok=True)
        return path

    # YouTube Data API v3 OAuth (installed-app flow). Create both in Google
    # Cloud Console -- see reaction_bot/README.md "راه‌اندازی یوتیوب".
    YOUTUBE_CLIENT_SECRETS_FILE = _env(
        "YOUTUBE_CLIENT_SECRETS_FILE", os.path.join(os.path.dirname(__file__), "client_secret.json")
    )
    YOUTUBE_TOKEN_FILE = _env(
        "YOUTUBE_TOKEN_FILE", os.path.join(os.path.dirname(__file__), "token.json")
    )
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    # "private" by default: a Shorts upload is a public, hard-to-fully-undo
    # action, so the pipeline never defaults to publishing straight to
    # "public" -- pass --privacy explicitly to change it per run.
    DEFAULT_PRIVACY_STATUS = _env("YOUTUBE_DEFAULT_PRIVACY", "private")
    DEFAULT_CATEGORY_ID = _env("YOUTUBE_DEFAULT_CATEGORY_ID", "23")  # "Comedy"

    # Output canvas: vertical 9:16 for Shorts.
    TARGET_W = 1080
    TARGET_H = 1920
    # Source clip only fills the top portion of the frame (not full-screen)
    # and the bottom "reaction" panel is reserved for the commentary/caption
    # (and, in phase 2, the avatar) -- see README.md "نکات حقوقی/ریسک".
    SOURCE_HEIGHT_RATIO = float(_env("REACTION_SOURCE_HEIGHT_RATIO", "0.6"))
    MAX_CLIP_SECONDS = float(_env("REACTION_MAX_CLIP_SECONDS", "58"))


config = Config()
