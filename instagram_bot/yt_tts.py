"""Voiceover providers for the YouTube-to-Reel pipeline (yt_reel.py).

The free default, Microsoft Edge's neural TTS (edge-tts), reads Persian
with an audible accent and a robotic cadence -- the account owner's
feedback on the first Reel. Two paid providers sound far more natural and
are used automatically once their key is set as a repo secret:

  ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID  (preferred: pick a native
      Persian voice in ElevenLabs' Voice Library; model eleven_v3 by
      default, override with ELEVENLABS_MODEL)
  OPENAI_API_KEY  (gpt-4o-mini-tts, steered toward natural Tehrani
      conversational Persian; voice via OPENAI_TTS_VOICE)

content.json can force one with "tts": "elevenlabs" | "openai" | "edge";
the default "auto" takes the first one whose key is configured.
"""
import asyncio
import os

import requests

EDGE_VOICES = {"fa": "fa-IR-FaridNeural", "en": "en-US-AndrewNeural"}

OPENAI_INSTRUCTIONS = {
    "fa": ("You are a native Persian speaker from Tehran recording a short Instagram "
           "Reel about trading. Speak natural, colloquial Tehrani Persian with no "
           "foreign accent, warm and confident like a friendly teacher, with natural "
           "intonation and pauses -- not like a news anchor or a robot."),
    "en": "Speak like a friendly, confident trading educator recording a short Instagram Reel.",
}


def pick_provider(content: dict) -> str:
    choice = content.get("tts", "auto")
    if choice != "auto":
        return choice
    if os.environ.get("ELEVENLABS_API_KEY") and os.environ.get("ELEVENLABS_VOICE_ID"):
        return "elevenlabs"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "edge"


def synthesize(provider: str, text: str, out_path: str, content: dict) -> None:
    """Write `text` spoken as an mp3 to out_path. Raises on failure."""
    lang = content.get("lang", "fa")
    if provider == "elevenlabs":
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['ELEVENLABS_VOICE_ID']}",
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
            json={"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_v3")},
            timeout=120,
        )
    elif provider == "openai":
        resp = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            json={"model": os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
                  "voice": os.environ.get("OPENAI_TTS_VOICE", "ash"),
                  "input": text,
                  "instructions": OPENAI_INSTRUCTIONS.get(lang, OPENAI_INSTRUCTIONS["en"]),
                  "response_format": "mp3"},
            timeout=120,
        )
    elif provider == "edge":
        import edge_tts

        voice = content.get("voice", EDGE_VOICES.get(lang, EDGE_VOICES["en"]))
        rate = content.get("voice_rate", "+0%")

        async def run():
            await edge_tts.Communicate(text, voice, rate=rate).save(out_path)

        asyncio.run(run())
        return
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")

    if resp.status_code != 200:
        raise RuntimeError(f"{provider} TTS error {resp.status_code}: {resp.text[:300]}")
    with open(out_path, "wb") as f:
        f.write(resp.content)
