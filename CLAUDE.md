# Notes for Claude

- Always write to the user in Persian (Farsi), in every message, including scheduled-task updates. Code, commit messages and PRs stay in English.
- Doodle Pals kids channel lives in `kids-shorts/` (see its README). Code changes: open a PR and merge it yourself after testing. Uploading to YouTube always needs the user's explicit approval.
- Never upload a topic twice: `daily.js` only picks topics not yet in `state/used.json`. When a category runs low (see `topicsLeft` in batch.json), tell the user and add 10 new topics for it (PR + merge).
