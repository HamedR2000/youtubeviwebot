"""Instagram's Graph API needs a publicly reachable URL to fetch the video
from -- it will not accept an uploaded file directly. Rather than standing
up separate cloud storage, we (ab)use GitHub Releases: create a dated
release in this same repo and attach the rendered mp4 as an asset, whose
`browser_download_url` is a stable public URL.
"""
import os

import requests

API_ROOT = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def publish_video_as_release_asset(repo: str, token: str, tag: str, video_path: str) -> str:
    """Create a release tagged `tag` (e.g. daily-post-2026-09-09) in `repo`
    ("owner/name"), upload `video_path` as its asset, and return the
    asset's public download URL.
    """
    create_resp = requests.post(
        f"{API_ROOT}/repos/{repo}/releases",
        headers=_headers(token),
        json={
            "tag_name": tag,
            "name": tag,
            "body": "Automated daily Instagram post asset.",
            "draft": False,
            "prerelease": False,
        },
        timeout=30,
    )
    create_resp.raise_for_status()
    release = create_resp.json()
    upload_url = release["upload_url"].split("{")[0]

    filename = os.path.basename(video_path)
    with open(video_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={**_headers(token), "Content-Type": "video/mp4"},
            params={"name": filename},
            data=f,
            timeout=300,
        )
    upload_resp.raise_for_status()
    return upload_resp.json()["browser_download_url"]
