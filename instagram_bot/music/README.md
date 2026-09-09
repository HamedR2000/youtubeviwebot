# Background music

Drop royalty-free `.mp3` (or `.m4a`) files in this folder. `video_composer.py`
picks one at random for each post, loops it if it's shorter than the clip,
and mixes it under the video at reduced volume.

**Where to get tracks legally:**

- [YouTube Audio Library](https://www.youtube.com/audiolibrary) — filter by
  "no attribution required" if you don't want to credit the artist in the
  caption; otherwise follow the attribution text it gives you.
- [Pixabay Music](https://pixabay.com/music/) — free, no attribution required.
- [Free Music Archive](https://freemusicarchive.org/) — check each track's
  license (some require attribution or are non-commercial only).

Keep a note of each track's name/license (e.g. in `LICENSES.txt` in this
folder) in case you ever need to prove where the audio came from.

This folder is empty by default — the bot will fail with a clear error
("No .mp3/.m4a files found") until you add at least one track.
