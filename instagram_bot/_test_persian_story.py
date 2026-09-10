"""One-off: verify Persian RTL story rendering works in the real CI
environment (not just the dev sandbox) before relying on it for the
weekly Persian story. Uploads one rendered story as a Release asset.
Not part of the ongoing pipeline -- delete after use.
"""
import datetime
import os

from carousel_backgrounds import next_background
from github_host import upload_release_asset
from image_composer import build_story_card
import state as state_mod
from content_bank import STORY_LINES_FA

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

st = state_mod.load()
photo_path = next_background(st)
out_path = "/tmp/persian_story_ci_test.jpg"
build_story_card(photo_path, STORY_LINES_FA[0], "@Goldhamedsignals", out_path, rtl=True)

tag = "persian-story-test-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
url = upload_release_asset(GITHUB_REPOSITORY, GITHUB_TOKEN, tag, out_path)
print("URL:", url)
