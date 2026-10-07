"""One-off script: fetch engagement data for every tracked post in
state.json so we can tell the account owner which content type/topic is
performing best. Not part of the daily pipeline -- run once via a temp
workflow, then deleted.
"""
import json
import os

import requests

from config import config

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")

GRAPH_BASE = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"

# Metric sets vary by media_product_type on the Graph API.
INSIGHTS_METRICS = {
    "REELS": "plays,reach,likes,comments,shares,saved,total_interactions",
    "CAROUSEL_ALBUM": "reach,likes,comments,shares,saved,total_interactions",
    "FEED": "reach,likes,comments,shares,saved,total_interactions",
}


def fetch_basic_fields(media_id, token):
    resp = requests.get(
        f"{GRAPH_BASE}/{media_id}",
        params={
            "fields": "media_type,media_product_type,timestamp,permalink,like_count,comments_count,caption",
            "access_token": token,
        },
        timeout=30,
    )
    return resp.status_code, resp.json()


def fetch_insights(media_id, product_type, token):
    metrics = INSIGHTS_METRICS.get(product_type, "reach,likes,comments,shares,saved,total_interactions")
    resp = requests.get(
        f"{GRAPH_BASE}/{media_id}/insights",
        params={"metric": metrics, "access_token": token},
        timeout=30,
    )
    return resp.status_code, resp.json()


def main():
    with open(STATE_PATH) as f:
        state = json.load(f)

    posts = state.get("posts", [])
    token = config.IG_ACCESS_TOKEN

    results = []
    for post in posts:
        media_id = post["ig_media_id"]
        row = {"date": post["date"], "type": post["type"], "ig_media_id": media_id}

        status, basic = fetch_basic_fields(media_id, token)
        if status == 200:
            row["basic"] = basic
        else:
            row["basic_error"] = basic

        product_type = basic.get("media_product_type") if status == 200 else None
        status2, insights = fetch_insights(media_id, product_type, token)
        if status2 == 200:
            row["insights"] = insights.get("data", [])
        else:
            row["insights_error"] = insights

        results.append(row)
        print(json.dumps(row, ensure_ascii=False))

    with open(os.path.join(os.path.dirname(__file__), "_insights_output.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Fetched data for {len(results)} posts.")


if __name__ == "__main__":
    main()
