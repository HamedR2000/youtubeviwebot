"""Environment-driven configuration. All secrets come from env vars so the
same code runs locally (via a .env file) and in GitHub Actions (via repo
secrets) with no code changes.
"""
import os


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "See instagram_bot/README.md for setup instructions."
        )
    return value


class Config:
    # Instagram Graph API (Meta) -- see README.md "Meta / Instagram setup".
    IG_USER_ID = property(lambda self: _require("IG_USER_ID"))
    IG_ACCESS_TOKEN = property(lambda self: _require("IG_ACCESS_TOKEN"))

    # Pexels API key -- free at https://www.pexels.com/api/
    PEXELS_API_KEY = property(lambda self: _require("PEXELS_API_KEY"))

    # GitHub repo (owner/name) + token, used to host the rendered video as a
    # public Release asset so Instagram's Graph API can fetch it by URL.
    GITHUB_REPOSITORY = property(lambda self: _require("GITHUB_REPOSITORY"))
    GITHUB_TOKEN = property(lambda self: _require("GITHUB_TOKEN"))

    GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v21.0")


config = Config()
