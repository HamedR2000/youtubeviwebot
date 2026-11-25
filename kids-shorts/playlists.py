"""YouTube playlists for Doodle Pals: every video goes into its category playlist (and episodes into their series).

Needs the full 'youtube' OAuth scope (playlist management). With an upload-only token the API answers 403
and the caller just skips playlists, so uploads keep working until the token is refreshed with get_token.py.
"""
import json
import os
import time

from googleapiclient.errors import HttpError

HERE = os.path.dirname(os.path.abspath(__file__))

CATEGORY = {
    'abc': ('ABC Alphabet for Toddlers 🔤', 'Learn the English alphabet one letter at a time with Penny the Pencil: big letter, little letter and a first word.'),
    'count': ('Numbers & Counting 🔢', 'Count from 1 to 10 with Penny the Pencil. Simple counting songs and number words for kids aged 2–6.'),
    'animal': ('Animal Sounds 🐮', 'Guess the animal by its sound with Ellie the Eraser! Animal names and sounds in English for toddlers.'),
    'color': ('Colors with Coco 🎨', 'Coco the Crayon colours the world! Learn colours in English for kids aged 2–6.'),
    'shape': ('Shapes for Toddlers ✏️', 'Draw a shape with Penny the Pencil and watch it become something new! Learn shapes in English.'),
    'drawalong': ("Let's Draw! Easy Drawing for Kids 🖍️", 'Step-by-step easy drawing for toddlers: draw animals and things with Penny the Pencil, then Coco colours them in!'),
    'shadow': ('Guess the Shadow! 🔦 Who Is Hiding?', 'A guessing game for toddlers: look at the shadow, count 3-2-1 and guess who is hiding! First English words with Penny the Pencil.'),
    'vehicle': ('Vehicle Sounds 🚒', 'Beep beep! Choo choo! Learn vehicle names and sounds with the Doodle Pals: cars, trucks, trains, planes and more.'),
    'colormix': ('Color Mixing with Coco 🎨', 'Red and yellow make orange! Mix colors with Coco the Crayon: color mixing in simple English for toddlers.'),
    'bedtime': ('Bedtime Lullabies 🌙', 'Calm bedtime videos for babies and toddlers: say good night with the Doodle Pals, then drift off to a gentle music-box lullaby.'),
    'mix': ('Doodle Pals Compilations 📺', 'Longer Doodle Pals videos for the big screen: ABC, numbers, animal sounds, colors, drawing and guessing games, many in a row.'),
    'episode': ('Doodle Pals Stories 🎬', 'Longer Doodle Pals cartoons with Penny, Ellie and Coco: stories, songs and learning for kids aged 2–6.'),
}


def playlists_for(video_id):
    """Playlist (title, description) list for one batch video id, e.g. 'abc-a' or 'episode-12-fruit-shop'."""
    if video_id.startswith('mega-'):  # long learning video: compilations + stories playlists
        return [CATEGORY['mix'], CATEGORY['episode']]
    if video_id.startswith('mix-'):  # compilation: its category playlist + all compilations
        return [CATEGORY.get(video_id.split('-')[1], CATEGORY['episode']), CATEGORY['mix']]
    if video_id.startswith('episode-'):
        out = [CATEGORY['episode']]
        f = os.path.join(HERE, 'episodes', video_id[len('episode-'):] + '.json')
        if os.path.exists(f):
            series = json.load(open(f)).get('series')
            if series:
                out.append((f'{series} — Doodle Pals', f'The "{series}" series from Doodle Pals: watch every part in order.'))
        return out
    prefix = video_id.split('-')[0]
    return [CATEGORY.get(prefix, CATEGORY['shape'])]


class Playlists:
    def __init__(self, yt):
        self.yt = yt
        self.cache = None

    def _load(self):
        self.cache = {}
        req = self.yt.playlists().list(part='snippet', mine=True, maxResults=50)
        while req is not None:
            resp = req.execute()
            for p in resp.get('items', []):
                self.cache[p['snippet']['title']] = p['id']
            req = self.yt.playlists().list_next(req, resp)

    def ensure(self, title, description):
        if self.cache is None:
            self._load()
        if title not in self.cache:
            p = self.yt.playlists().insert(part='snippet,status', body={
                'snippet': {'title': title, 'description': description, 'defaultLanguage': 'en'},
                'status': {'privacyStatus': 'public'}}).execute()
            self.cache[title] = p['id']
            print(f'  created playlist "{title}"')
        return self.cache[title]

    def add(self, playlist_id, video_id):
        try:
            have = self.yt.playlistItems().list(part='id', playlistId=playlist_id, videoId=video_id).execute()
            if have.get('items'):
                return False
        except HttpError as e:
            if e.resp.status != 404:  # a playlist created seconds ago can still answer 404: it is empty anyway
                raise
        for attempt in range(5):  # and its first insert may need a few seconds to see it
            try:
                self.yt.playlistItems().insert(part='snippet', body={'snippet': {'playlistId': playlist_id,
                                               'resourceId': {'kind': 'youtube#video', 'videoId': video_id}}}).execute()
                return True
            except HttpError as e:
                if e.resp.status != 404 or attempt == 4:
                    raise
                time.sleep(3 * (attempt + 1))

    def file(self, batch_id, youtube_id):
        added = []
        for title, desc in playlists_for(batch_id):
            if self.add(self.ensure(title, desc), youtube_id):
                added.append(title)
        return added
