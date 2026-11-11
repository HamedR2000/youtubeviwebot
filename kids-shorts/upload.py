"""Upload an approved daily batch to YouTube.

Usage: python3 upload.py <batch_dir> [--skip id1,id2] [--privacy public|unlisted|private] [--dry-run]
Reads <batch_dir>/batch.json (written by daily.js) and uploads each video as Made-for-Kids, Education.

Credentials (env): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN  (create once with get_token.py)
"""
import argparse
import json
import os
import sys

p = argparse.ArgumentParser()
p.add_argument('batch_dir')
p.add_argument('--skip', default='')
p.add_argument('--privacy', default='public', choices=['public', 'unlisted', 'private'])
p.add_argument('--dry-run', action='store_true')
args = p.parse_args()

batch = json.load(open(os.path.join(args.batch_dir, 'batch.json')))
skip = {s.strip() for s in args.skip.split(',') if s.strip()}
# videos already uploaded by an earlier (partial) publish run are never uploaded twice
up_file = os.path.join(args.batch_dir, 'uploaded.json')
done = json.load(open(up_file)) if os.path.exists(up_file) else []
skip |= {d['id'] for d in done}
# long episodes first: if YouTube's daily upload limit is hit, the most valuable video is already up
videos = sorted((v for v in batch['videos'] if v['id'] not in skip), key=lambda v: not v.get('long'))
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
    scopes=['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly'],
)
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

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
            'privacyStatus': args.privacy,
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
    results.append({'id': v['id'], 'youtube_id': resp['id'], 'url': url})

json.dump(results, open(up_file, 'w'), indent=2)
open(os.path.join(args.batch_dir, 'pending.txt'), 'w').write('\n'.join(pending))
