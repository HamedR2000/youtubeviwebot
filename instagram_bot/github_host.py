"""Instagram's Graph API needs a publicly reachable URL to fetch media from
-- it will not accept an uploaded file directly. Rather than standing up
separate cloud storage, we (ab)use GitHub Releases: create a dated release
in this same repo and attach the rendered file (video or image) as an
asset, whose `browser_download_url` is a stable public URL.
"""
import mimetypes
import os

import requests

API_ROOT = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def upload_release_asset(repo: str, token: str, tag: str, file_path: str,
                          release_name: str = None) -> str:
    """Create (or reuse) a release tagged `tag` (e.g. daily-post-2026-09-09)
    in `repo` ("owner/name"), upload `file_path` as an asset, and return the
    asset's public download URL. Safe to call multiple times with the same
    tag in one run (e.g. reel + several story images for the same day).
    """
    create_resp = requests.post(
        f"{API_ROOT}/repos/{repo}/releases",
        headers=_headers(token),
        json={
            "tag_name": tag,
            "name": release_name or tag,
            "body": "Automated daily Instagram post assets.",
            "draft": False,
            "prerelease": False,
        },
        timeout=30,
    )
    if create_resp.status_code == 422:
        # Release for this tag already exists (e.g. second asset today) -- fetch it.
        get_resp = requests.get(f"{API_ROOT}/repos/{repo}/releases/tags/{tag}",
                                 headers=_headers(token), timeout=30)
        get_resp.raise_for_status()
        release = get_resp.json()
    else:
        create_resp.raise_for_status()
        release = create_resp.json()

    upload_url = release["upload_url"].split("{")[0]
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={**_headers(token), "Content-Type": content_type},
            params={"name": filename},
            data=f,
            timeout=300,
        )
    upload_resp.raise_for_status()
    return upload_resp.json()["browser_download_url"]
