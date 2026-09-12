"""CLI entry point for the phase-1 reaction pipeline (no avatar yet):

    python main.py --source <instagram-url-or-local-file> \\
        --script-file script.txt --approve --upload

Without --approve, the source clip is downloaded and the script is printed
back for review, then the run stops -- matching the project's requirement
that the reaction script is confirmed/edited by hand before final
production (see ../README project notes). Without --upload, the composed
file is left in workdir/outputs/ for a manual look before it goes public.
"""
import argparse
import os

from config import config
from composer import compose_reaction_video
from downloader import fetch_source_video
from youtube_upload import upload_video


def _read_script(args: argparse.Namespace) -> str:
    if args.script_file:
        with open(args.script_file, encoding="utf-8") as f:
            return f.read().strip()
    if args.script:
        return args.script.strip()
    raise SystemExit("Provide the reaction script with --script or --script-file.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Instagram clip -> reaction Short pipeline (phase 1)")
    parser.add_argument("--source", required=True, help="Instagram URL or local video file")
    parser.add_argument("--script", help="Reaction script text")
    parser.add_argument("--script-file", help="Path to a text file with the reaction script")
    parser.add_argument("--lang", choices=["fa", "en"], default="fa", help="Script language (controls RTL layout)")
    parser.add_argument("--voice", help="Optional recorded/TTS reaction voiceover audio file")
    parser.add_argument("--approve", action="store_true",
                         help="Confirms the script is final; without this, only downloads and previews it")
    parser.add_argument("--upload", action="store_true", help="Upload the composed video to YouTube")
    parser.add_argument("--dry-run", action="store_true", help="With --upload: print the upload payload, send nothing")
    parser.add_argument("--title", help="YouTube video title (defaults to the first line of the script)")
    parser.add_argument("--description", default="", help="YouTube video description")
    parser.add_argument("--tags", default="", help="Comma-separated YouTube tags")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], help="YouTube privacy status")
    args = parser.parse_args()

    script_text = _read_script(args)

    print(f"Fetching source video from: {args.source}")
    source_path = fetch_source_video(args.source)
    print(f"Source video: {source_path}")
    print("--- Reaction script ---")
    print(script_text)
    print("-----------------------")

    if not args.approve:
        print("\nScript not approved yet -- rerun with --approve once you're happy with it "
              "(edit the script file or pass a different --script first).")
        return

    output_name = os.path.splitext(os.path.basename(source_path))[0] + "_reaction.mp4"
    output_path = os.path.join(config.outputs_dir, output_name)
    print(f"Composing reaction video -> {output_path}")
    compose_reaction_video(
        source_path=source_path,
        script_text=script_text,
        output_path=output_path,
        rtl=(args.lang == "fa"),
        voice_path=args.voice,
    )
    print(f"Composed: {output_path}")

    if not args.upload:
        print("\nNot uploading (pass --upload to publish to YouTube). "
              "Review the file above first.")
        return

    title = args.title or script_text.splitlines()[0][:100]
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    upload_video(
        file_path=output_path,
        title=title,
        description=args.description,
        tags=tags,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
