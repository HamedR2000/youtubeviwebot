"""Hourly view tracker for the Doodle Pals channel (YouTube Data API: public view counts only).

  python3 stats.py snapshot stats.jsonl   # append one line: {"ts": ..., "views": {videoId: count}}
  python3 stats.py report stats.jsonl     # views gained per hour of day (Berlin / New York / London)

The hourly GitHub workflow keeps stats.jsonl as an asset of the 'stats' release.
Credentials (env): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
"""
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo


def snapshot(path):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(token=None, refresh_token=os.environ['YT_REFRESH_TOKEN'], client_id=os.environ['YT_CLIENT_ID'],
                        client_secret=os.environ['YT_CLIENT_SECRET'], token_uri='https://oauth2.googleapis.com/token')
    yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)
    ch = yt.channels().list(part='contentDetails,statistics', mine=True).execute()['items'][0]
    uploads = ch['contentDetails']['relatedPlaylists']['uploads']
    ids, req = [], yt.playlistItems().list(part='contentDetails', playlistId=uploads, maxResults=50)
    while req is not None:
        resp = req.execute()
        ids += [i['contentDetails']['videoId'] for i in resp.get('items', [])]
        req = yt.playlistItems().list_next(req, resp)
    views = {}
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part='statistics', id=','.join(ids[i:i + 50])).execute().get('items', []):
            views[v['id']] = int(v['statistics'].get('viewCount', 0))
    row = {'ts': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'subs': int(ch['statistics'].get('subscriberCount', 0)),
           'total': sum(views.values()), 'views': views}
    with open(path, 'a') as f:
        f.write(json.dumps(row) + '\n')
    print(f"{row['ts']}: {len(views)} videos, {row['total']} views, {row['subs']} subscribers")


def report(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows.sort(key=lambda r: r['ts'])
    gain = defaultdict(float)  # views gained, by UTC hour
    days = set()
    for a, b in zip(rows, rows[1:]):
        ta, tb = (dt.datetime.fromisoformat(r['ts'].replace('Z', '+00:00')) for r in (a, b))
        hours = (tb - ta).total_seconds() / 3600
        if hours <= 0 or hours > 3:  # skip gaps (missed runs)
            continue
        # only videos present in both snapshots, so new uploads do not count as a jump
        d = sum(max(0, b['views'][k] - a['views'][k]) for k in b['views'] if k in a['views'])
        mid = ta + (tb - ta) / 2
        gain[mid.hour] += d
        days.add(mid.date())
    total = sum(gain.values()) or 1
    print(f'{len(rows)} snapshots over {len(days)} day(s), {int(total)} views counted\n')
    print('UTC  Berlin  London  New York   share')
    for h in range(24):
        t = dt.datetime(2026, 1, 15, h, 30, tzinfo=dt.timezone.utc)  # winter offsets
        loc = [t.astimezone(ZoneInfo(z)).strftime('%H:00') for z in ('Europe/Berlin', 'Europe/London', 'America/New_York')]
        share = gain[h] / total
        print(f'{h:02d}   {loc[0]}   {loc[1]}   {loc[2]}   {share:6.1%} {"#" * round(share * 100)}')
    best = sorted(gain, key=gain.get, reverse=True)[:3]
    print('\nbusiest hours (UTC):', ', '.join(f'{h:02d}:00' for h in best))


if __name__ == '__main__':
    {'snapshot': snapshot, 'report': report}[sys.argv[1]](sys.argv[2])
