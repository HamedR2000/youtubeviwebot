"""نقطه‌ی ورود برای ویدیوهای آماده (مثلاً خروجی HeyGen) که خودت از قبل
ساختی و فقط می‌خوای نوار سابسکرایب/لایک روش بیاد و بره روی یوتیوب --
برخلاف main.py که از صفر (لینک اینستاگرام + آواتار) می‌سازه.

    python publish_ready.py --video path/to/finished.mp4 --approve --upload --privacy unlisted

بدون --approve فقط اطلاعات ویدیو (مدت، ابعاد) رو چاپ می‌کنه و متوقف
می‌شه. بدون --upload فایل نهایی (با نوار) توی workdir/outputs/ می‌مونه.
--title اختیاریه -- بدون اون، موقع آپلود یه عنوان عمومی از titles.py
انتخاب می‌شه (به‌ترتیب، بدون تکرار تا ته لیست).
"""
import argparse
import os

from moviepy import VideoFileClip

from branding import add_subscribe_banner
from config import config
from titles import pick_title
from youtube_upload import upload_video

SHORTS_MAX_SECONDS = 180


def main() -> None:
    parser = argparse.ArgumentParser(description="آپلود مستقیم یه ویدیوی آماده (مثلاً خروجی HeyGen) به یوتیوب شورتز")
    parser.add_argument("--video", required=True, help="مسیر فایل ویدیوی نهایی و آماده")
    parser.add_argument("--title", help="عنوان ویدیوی یوتیوب (اختیاری -- بدون این، از titles.py یه عنوان عمومی انتخاب می‌شه)")
    parser.add_argument("--description", default="", help="توضیحات ویدیوی یوتیوب")
    parser.add_argument("--tags", default="", help="تگ‌های یوتیوب، با کاما جدا شده")
    parser.add_argument("--no-banner", action="store_true", help="نوار سابسکرایب/لایک اضافه نشه")
    parser.add_argument("--approve", action="store_true", help="تأیید نهایی؛ بدون این فلگ فقط اطلاعات ویدیو رو چاپ می‌کنه")
    parser.add_argument("--upload", action="store_true", help="آپلود به یوتیوب")
    parser.add_argument("--dry-run", action="store_true", help="همراه --upload: فقط payload رو چاپ می‌کنه")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], help="وضعیت انتشار یوتیوب")
    args = parser.parse_args()

    with VideoFileClip(args.video) as clip:
        w, h, duration = clip.w, clip.h, clip.duration

    print(f"ویدیو: {args.video}")
    print(f"ابعاد: {w}x{h}  |  مدت: {duration:.1f} ثانیه")
    if args.title:
        print(f"عنوان: {args.title}")
    else:
        print("عنوان: داده نشده -- موقع آپلود از titles.py یه عنوان عمومی انتخاب می‌شه")
    if h <= w:
        print("⚠️  این ویدیو افقیه یا مربعه، نه عمودی -- برای Shorts معمولاً باید عمودی (9:16) باشه.")
    if duration > SHORTS_MAX_SECONDS:
        print(f"⚠️  مدت ویدیو بیشتر از {SHORTS_MAX_SECONDS} ثانیه‌ست -- یوتیوب ممکنه به‌عنوان Shorts در نظرش نگیره.")

    if not args.approve:
        print("\nهنوز تأیید نشده -- بعد از این‌که مطمئن شدی، همین دستور رو با --approve دوباره بزن.")
        return

    output_path = os.path.join(config.outputs_dir, os.path.basename(args.video))
    if args.no_banner:
        final_path = args.video
    else:
        print(f"در حال اضافه‌کردن نوار سابسکرایب/لایک -> {output_path}")
        final_path = add_subscribe_banner(args.video, output_path)
        print(f"آماده شد: {final_path}")

    if not args.upload:
        print("\nآپلود انجام نشد (برای انتشار در یوتیوب --upload بده).")
        return

    title = args.title or pick_title()
    print(f"عنوان نهایی: {title}")

    description = args.description
    if "#shorts" not in description.lower():
        description = (description + "\n\n#Shorts").strip()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    upload_video(
        file_path=final_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
