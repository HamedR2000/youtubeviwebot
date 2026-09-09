"""Instagram Graph API (Meta Content Publishing) client: turn a public
video URL + caption into a live Reel on the connected Business/Creator
account.

Flow (per Meta's docs):
  1. POST /{ig-user-id}/media           -> creates a container, returns creation_id
  2. GET  /{creation-id}?fields=status_code  -> poll until FINISHED
  3. POST /{ig-user-id}/media_publish   -> publishes the container
"""
import time

import requests


class PublishError(Exception):
    pass


def _graph_url(version: str, path: str) -> str:
    return f"https://graph.facebook.com/{version}/{path}"


def create_media_container(version: str, ig_user_id: str, access_token: str,
                            video_url: str, caption: str) -> str:
    resp = requests.post(
        _graph_url(version, f"{ig_user_id}/media"),
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=60,
    )
    _raise_for_graph_error(resp)
    return resp.json()["id"]


def wait_until_ready(version: str, creation_id: str, access_token: str,
                      timeout_s: int = 300, poll_interval_s: int = 10) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = requests.get(
            _graph_url(version, creation_id),
            params={"fields": "status_code,status", "access_token": access_token},
            timeout=30,
        )
        _raise_for_graph_error(resp)
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise PublishError(f"Media container {creation_id} failed processing: {resp.json()}")
        time.sleep(poll_interval_s)
    raise PublishError(f"Media container {creation_id} did not finish within {timeout_s}s")


def publish_container(version: str, ig_user_id: str, access_token: str, creation_id: str) -> str:
    resp = requests.post(
        _graph_url(version, f"{ig_user_id}/media_publish"),
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=60,
    )
    _raise_for_graph_error(resp)
    return resp.json()["id"]


def publish_reel(version: str, ig_user_id: str, access_token: str,
                  video_url: str, caption: str) -> str:
    creation_id = create_media_container(version, ig_user_id, access_token, video_url, caption)
    wait_until_ready(version, creation_id, access_token)
    return publish_container(version, ig_user_id, access_token, creation_id)


def _raise_for_graph_error(resp: requests.Response) -> None:
    if resp.status_code >= 400:
        raise PublishError(f"Graph API error {resp.status_code}: {resp.text}")
