"""Instagram Graph API (Meta Content Publishing) client: turn a public
media URL into a live Reel, feed post, or Story on the connected
Business/Creator account.

Flow (per Meta's docs), the same three steps for every content type:
  1. POST /{ig-user-id}/media                -> creates a container, returns creation_id
  2. GET  /{creation-id}?fields=status_code   -> poll until FINISHED
  3. POST /{ig-user-id}/media_publish         -> publishes the container

Note: Stories do not support captions or interactive stickers (polls,
links, etc.) through the Graph API -- only a plain image or video.
"""
import time

import requests


class PublishError(Exception):
    pass


def _graph_url(version: str, path: str) -> str:
    return f"https://graph.facebook.com/{version}/{path}"


def create_media_container(version: str, ig_user_id: str, access_token: str, *,
                            media_type: str = None, image_url: str = None,
                            video_url: str = None, caption: str = None) -> str:
    if not image_url and not video_url:
        raise ValueError("create_media_container requires image_url or video_url")

    data = {"access_token": access_token}
    if media_type:
        data["media_type"] = media_type
    if image_url:
        data["image_url"] = image_url
    if video_url:
        data["video_url"] = video_url
    if caption:
        data["caption"] = caption

    resp = requests.post(_graph_url(version, f"{ig_user_id}/media"), data=data, timeout=60)
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


def _create_wait_publish(version, ig_user_id, access_token, **container_kwargs) -> str:
    creation_id = create_media_container(version, ig_user_id, access_token, **container_kwargs)
    wait_until_ready(version, creation_id, access_token)
    return publish_container(version, ig_user_id, access_token, creation_id)


def publish_reel(version: str, ig_user_id: str, access_token: str,
                  video_url: str, caption: str) -> str:
    return _create_wait_publish(version, ig_user_id, access_token,
                                 media_type="REELS", video_url=video_url, caption=caption)


def publish_feed_image(version: str, ig_user_id: str, access_token: str,
                        image_url: str, caption: str) -> str:
    return _create_wait_publish(version, ig_user_id, access_token,
                                 image_url=image_url, caption=caption)


def publish_story(version: str, ig_user_id: str, access_token: str, *,
                   image_url: str = None, video_url: str = None) -> str:
    return _create_wait_publish(version, ig_user_id, access_token,
                                 media_type="STORIES", image_url=image_url, video_url=video_url)


def publish_carousel(version: str, ig_user_id: str, access_token: str,
                      image_urls: list, caption: str) -> str:
    """Publish a multi-image swipeable carousel (album) post: each image
    becomes an `is_carousel_item` child container, then a parent CAROUSEL
    container ties them together and carries the single shared caption."""
    child_ids = []
    for image_url in image_urls:
        resp = requests.post(
            _graph_url(version, f"{ig_user_id}/media"),
            data={"image_url": image_url, "is_carousel_item": "true", "access_token": access_token},
            timeout=60,
        )
        _raise_for_graph_error(resp)
        child_id = resp.json()["id"]
        wait_until_ready(version, child_id, access_token)
        child_ids.append(child_id)

    resp = requests.post(
        _graph_url(version, f"{ig_user_id}/media"),
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": access_token,
        },
        timeout=60,
    )
    _raise_for_graph_error(resp)
    parent_id = resp.json()["id"]
    wait_until_ready(version, parent_id, access_token)
    return publish_container(version, ig_user_id, access_token, parent_id)


def list_comments(version: str, media_id: str, access_token: str) -> list:
    """Top-level comments on one of our own media items -- our own replies
    live under each comment's `replies` edge, not here, so this never
    returns anything we posted ourselves."""
    resp = requests.get(
        _graph_url(version, f"{media_id}/comments"),
        params={"fields": "id,username,text,timestamp", "access_token": access_token},
        timeout=30,
    )
    _raise_for_graph_error(resp)
    return resp.json().get("data", [])


def reply_to_comment(version: str, comment_id: str, access_token: str, message: str) -> str:
    resp = requests.post(
        _graph_url(version, f"{comment_id}/replies"),
        data={"message": message, "access_token": access_token},
        timeout=30,
    )
    _raise_for_graph_error(resp)
    return resp.json()["id"]


def _raise_for_graph_error(resp: requests.Response) -> None:
    if resp.status_code >= 400:
        raise PublishError(f"Graph API error {resp.status_code}: {resp.text}")
