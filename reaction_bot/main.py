"""نقطه‌ی ورود خط فرمان پایپ‌لاین ری‌اکشن (فقط عکس آواتار کنار ویدیو، بدون
هیچ متنی روی صفحه، بدون لب‌سینک صوتی فعلاً):

    python main.py --source <لینک-اینستاگرام-یا-فایل-محلی> --approve --upload

بدون --approve، فقط کلیپ منبع دانلود می‌شه و اجرا متوقف می‌شه تا خودت
تأیید کنی. بدون --upload، فایل نهایی توی workdir/outputs/ می‌مونه تا
خودت قبل از پابلیک‌شدن نگاهش کنی.
"""
import argparse
import os

from config import config
from composer import compose_reaction_video
from downloader import fetch_source_video
from youtube_upload import upload_video


def _read_script(args: argparse.Namespace) -> str:
    """اختیاریه -- ویدیو دیگه هیچ متنی روی صفحه نشون نمی‌ده، ولی اگه بدی
    برای پیش‌نمایش/عنوان پیش‌فرض یوتیوب و کارهای بعدی (مثلاً TTS) نگه
    داشته می‌شه."""
    if args.script_file:
        with open(args.script_file, encoding="utf-8") as f:
            return f.read().strip()
    if args.script:
        return args.script.strip()
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="پایپ‌لاین کلیپ اینستاگرام -> ری‌اکشن Shorts (فاز ۱)")
    parser.add_argument("--source", required=True, help="لینک اینستاگرام یا مسیر فایل ویدیوی محلی")
    parser.add_argument("--script", help="متن اسکریپت ری‌اکشن (اختیاری -- روی ویدیو نمایش داده نمی‌شه، فقط برای عنوان/یادداشت)")
    parser.add_argument("--script-file", help="مسیر فایل متنی حاوی اسکریپت ری‌اکشن (اختیاری)")
    parser.add_argument("--voice", help="فایل صوتی ری‌اکشن (ضبط‌شده یا TTS) -- اختیاری")
    parser.add_argument("--avatar", help="مسیر عکس آواتار (PNG، پس‌زمینه‌ی شفاف)؛ پیش‌فرض: reaction_bot/assets/avatar.png اگه وجود داشته باشه")
    parser.add_argument("--approve", action="store_true",
                         help="تأیید نهایی‌بودن اسکریپت؛ بدون این فلگ فقط دانلود و پیش‌نمایش انجام می‌شه")
    parser.add_argument("--upload", action="store_true", help="آپلود ویدیوی ترکیب‌شده به یوتیوب")
    parser.add_argument("--dry-run", action="store_true", help="همراه --upload: فقط payload آپلود رو چاپ می‌کنه، چیزی ارسال نمی‌شه")
    parser.add_argument("--title", help="عنوان ویدیوی یوتیوب (پیش‌فرض: خط اول اسکریپت)")
    parser.add_argument("--description", default="", help="توضیحات ویدیوی یوتیوب")
    parser.add_argument("--tags", default="", help="تگ‌های یوتیوب، با کاما جدا شده")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], help="وضعیت انتشار یوتیوب")
    args = parser.parse_args()

    script_text = _read_script(args)

    print(f"در حال دانلود ویدیوی منبع از: {args.source}")
    source_path = fetch_source_video(args.source)
    print(f"ویدیوی منبع: {source_path}")
    if script_text:
        print("--- اسکریپت ری‌اکشن (فقط برای عنوان/یادداشت، روی ویدیو نمایش داده نمی‌شه) ---")
        print(script_text)
        print("-----------------------")

    if not args.approve:
        print("\nهنوز تأیید نشده -- بعد از این‌که مطمئن شدی، همین دستور رو با --approve دوباره بزن.")
        return

    avatar_path = args.avatar or (config.DEFAULT_AVATAR_PATH if os.path.isfile(config.DEFAULT_AVATAR_PATH) else None)

    output_name = os.path.splitext(os.path.basename(source_path))[0] + "_reaction.mp4"
    output_path = os.path.join(config.outputs_dir, output_name)
    print(f"در حال ساخت ویدیوی ری‌اکشن -> {output_path}")
    compose_reaction_video(
        source_path=source_path,
        output_path=output_path,
        voice_path=args.voice,
        avatar_path=avatar_path,
    )
    print(f"ساخته شد: {output_path}")

    if not args.upload:
        print("\nآپلود انجام نشد (برای انتشار در یوتیوب --upload بده). "
              "اول فایل بالا رو خودت ببین.")
        return

    title = args.title or (script_text.splitlines()[0][:100] if script_text else os.path.basename(source_path))
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
