"""Upload an approved daily batch to YouTube.

Usage: python3 upload.py <batch_dir> [--skip id1,id2] [--privacy public|unlisted|private] [--publish-at 17:00] [--dry-run]
--publish-at HH:MM (Europe/Berlin): public videos are uploaded as scheduled and go public at that time today
(immediately if that time has passed). English captions (<video>.srt) are added when the token allows it.
Reads <batch_dir>/batch.json (written by daily.js) and uploads each video as Made-for-Kids, Education.

Credentials (env): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN  (create once with get_token.py)
"""
import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

p = argparse.ArgumentParser()
p.add_argument('batch_dir')
p.add_argument('--skip', default='')
p.add_argument('--privacy', default='public', choices=['public', 'unlisted', 'private'])
p.add_argument('--publish-at', default='', help='HH:MM Europe/Berlin: schedule public videos for this time today')
p.add_argument('--dry-run', action='store_true')
p.add_argument('--only-playlists', action='store_true', help='just file already-uploaded videos into playlists')
p.add_argument('--only-thumbnails', action='store_true', help='just set custom thumbnails on already-uploaded videos')
p.add_argument('--thumb-dir', default='', help='extra folder with <batch id>.jpg thumbnails (backfill)')
args = p.parse_args()

batch = json.load(open(os.path.join(args.batch_dir, 'batch.json')))
skip = {s.strip() for s in args.skip.split(',') if s.strip()}
# videos already uploaded by an earlier (partial) publish run are never uploaded twice
up_file = os.path.join(args.batch_dir, 'uploaded.json')
done = json.load(open(up_file)) if os.path.exists(up_file) else []
skip |= {d['id'] for d in done}
# long episodes first: if YouTube's daily upload limit is hit, the most valuable video is already up
videos = sorted((v for v in batch['videos'] if v['id'] not in skip), key=lambda v: not v.get('long'))
if args.only_playlists or args.only_thumbnails:
    videos = []
# scheduled release: upload as private with publishAt (YouTube flips it to public at that time)
publish_at = None
if args.publish_at and args.privacy == 'public':
    hh, mm = map(int, args.publish_at.split(':'))
    now = dt.datetime.now(dt.timezone.utc)
    when = dt.datetime.now(ZoneInfo('Europe/Berlin')).replace(hour=hh, minute=mm, second=0, microsecond=0)
    if when - now > dt.timedelta(minutes=15):
        publish_at = when.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f'scheduled: videos go public at {args.publish_at} Berlin ({publish_at})')
print(f"{batch['date']}: uploading {len(videos)} video(s), skipping {sorted(skip) or 'none'}")

if args.dry_run:
    for v in videos:
        print('  would upload', v['file'], '-', v['title'])
    sys.exit(0)

from google.oauth2.credentials import Credentials  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.errors import HttpError, ResumableUploadError  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402

creds = Credentials(
    token=None,
    refresh_token=os.environ['YT_REFRESH_TOKEN'],
    client_id=os.environ['YT_CLIENT_ID'],
    client_secret=os.environ['YT_CLIENT_SECRET'],
    token_uri='https://oauth2.googleapis.com/token',
)
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playlists import Playlists  # noqa: E402
pl = Playlists(yt)
pl_ok = True


def file_in_playlists(batch_id, youtube_id):
    global pl_ok
    if not pl_ok:
        return
    try:
        added = pl.file(batch_id, youtube_id)
        if added:
            print(f'    + playlists: {", ".join(added)}')
    except HttpError as e:
        if e.resp.status in (401, 403):
            pl_ok = False
            print('  (playlists skipped: the YouTube token has no playlist permission yet; re-run get_token.py)')
        else:
            print(f'  (playlist error for {batch_id}: {e})')

cap_ok = True


def add_captions(entry):
    """Upload the English .srt for one uploaded video (once). Needs the youtube.force-ssl scope."""
    global cap_ok
    v = next((x for x in batch['videos'] if x['id'] == entry['id']), None)
    srt = v and v.get('captions') and os.path.join(args.batch_dir, v['captions'])
    if not cap_ok or entry.get('captions') or not srt or not os.path.exists(srt):
        return
    try:
        yt.captions().insert(part='snippet', body={'snippet': {'videoId': entry['youtube_id'], 'language': 'en', 'name': 'English', 'isDraft': False}},
                             media_body=MediaFileUpload(srt, mimetype='application/octet-stream')).execute()
        entry['captions'] = True
        print(f"    + English captions")
    except HttpError as e:
        if e.resp.status in (401, 403):
            cap_ok = False
            print(f'  (captions skipped: {"quota used up for today" if "quota" in str(e) else "token has no caption permission yet; re-run get_token.py"})')
        else:
            print(f"  (caption error for {entry['id']}: {e})")


thumb_ok = True


def set_thumbnail(entry):
    """Custom thumbnail for one uploaded video (needs a phone-verified channel)."""
    global thumb_ok
    v = next((x for x in batch['videos'] if x['id'] == entry['id']), {})
    cands = [os.path.join(args.batch_dir, v['thumbnail'])] if v.get('thumbnail') else []
    if args.thumb_dir:
        cands.append(os.path.join(args.thumb_dir, entry['id'] + '.jpg'))
    jpg = next((c for c in cands if os.path.exists(c)), None)
    if not thumb_ok or entry.get('thumbnail') or not jpg:
        return
    try:
        yt.thumbnails().set(videoId=entry['youtube_id'], media_body=MediaFileUpload(jpg, mimetype='image/jpeg')).execute()
        entry['thumbnail'] = True
        print(f"    + thumbnail for {entry['id']}")
    except HttpError as e:
        if e.resp.status in (401, 403):
            thumb_ok = False
            print(f'  (thumbnails skipped: {e})')
        else:
            print(f"  (thumbnail error for {entry['id']}: {e})")


results = list(done)
pending = []
for n, v in enumerate(videos):
    body = {
        'snippet': {
            'title': v['title'][:100],
            'description': v['description'],
            'tags': v['tags'],
            'categoryId': v.get('categoryId', '27'),
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en',
        },
        'status': {
            'privacyStatus': 'private' if publish_at else args.privacy,
            **({'publishAt': publish_at} if publish_at else {}),
            'selfDeclaredMadeForKids': bool(v.get('madeForKids', True)),
            'containsSyntheticMedia': False,
        },
    }
    media = MediaFileUpload(os.path.join(args.batch_dir, v['file']), mimetype='video/mp4', resumable=True)
    req = yt.videos().insert(part='snippet,status', body=body, media_body=media)
    resp = None
    try:
        while resp is None:
            _, resp = req.next_chunk()
    except (HttpError, ResumableUploadError) as e:
        if 'uploadLimitExceeded' not in str(e):
            json.dump(results, open(up_file, 'w'), indent=2)
            raise
        pending = [x['id'] for x in videos[n:]]
        print(f"  YouTube daily upload limit reached — not uploaded yet: {', '.join(pending)}")
        print('  Run publish again for the same date later (about 24 h after the earlier uploads); uploaded videos are skipped.')
        break
    url = f"https://youtube.com/watch?v={resp['id']}" if v.get('long') else f"https://youtube.com/shorts/{resp['id']}"
    print('  uploaded', v['id'], '->', url)
    results.append({'id': v['id'], 'youtube_id': resp['id'], 'url': url, **({'publishAt': publish_at} if publish_at else {})})
    file_in_playlists(v['id'], resp['id'])

if args.only_thumbnails:
    for d in results:
        set_thumbnail(d)
elif args.only_playlists:
    for d in done:
        file_in_playlists(d['id'], d['youtube_id'])
else:
    for r in results:
        set_thumbnail(r)
    # a run without a schedule makes earlier scheduled uploads of this batch public right away
    if args.privacy == 'public' and not publish_at:
        for r in results:
            if r.get('publishAt'):
                yt.videos().update(part='status', body={'id': r['youtube_id'], 'status': {
                    'privacyStatus': 'public', 'selfDeclaredMadeForKids': True, 'containsSyntheticMedia': False}}).execute()
                r.pop('publishAt')
                print(f"  made public now: {r['id']}")
    # captions last (and retried on later runs), so the videos themselves never wait for them
    for r in results:
        add_captions(r)

json.dump(results, open(up_file, 'w'), indent=2)
open(os.path.join(args.batch_dir, 'pending.txt'), 'w').write('\n'.join(pending))
