"""One-off: query the Instagram Graph API's online_followers insight to see
what hours the account's actual followers are online, instead of guessing
a posting time. Prints the result -- not part of the ongoing pipeline,
delete after use.
"""
import os

import requests

IG_USER_ID = os.environ["IG_USER_ID"]
IG_ACCESS_TOKEN = os.environ["IG_ACCESS_TOKEN"]
GRAPH_API_VERSION = "v21.0"


def main() -> None:
    resp = requests.get(
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/insights",
        params={
            "metric": "online_followers",
            "period": "lifetime",
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=30,
    )
    print("status:", resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()
