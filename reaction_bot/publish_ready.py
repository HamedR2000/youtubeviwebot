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
from hashtags import CATEGORY_POOLS, ensure_hashtags
from thumbnail import extract_thumbnail
from titles import pick_title
from youtube_upload import set_thumbnail, upload_video

SHORTS_MAX_SECONDS = 180


def main() -> None:
    parser = argparse.ArgumentParser(description="آپلود مستقیم یه ویدیوی آماده (مثلاً خروجی HeyGen) به یوتیوب شورتز")
    parser.add_argument("--video", required=True, help="مسیر فایل ویدیوی نهایی و آماده")
    parser.add_argument("--title", help="عنوان ویدیوی یوتیوب (اختیاری -- بدون این، از titles.py یه عنوان عمومی انتخاب می‌شه)")
    parser.add_argument("--description", default="", help="توضیحات ویدیوی یوتیوب")
    parser.add_argument("--tags", default="", help="تگ‌های یوتیوب، با کاما جدا شده")
    parser.add_argument("--category", choices=list(CATEGORY_POOLS), help="ژانر ویدیو (اختیاری) -- چندتا هشتگ مرتبط‌تر هم به توضیحات اضافه می‌کنه")
    parser.add_argument("--no-banner", action="store_true", help="نوار سابسکرایب/لایک اضافه نشه")
    parser.add_argument("--approve", action="store_true", help="تأیید نهایی؛ بدون این فلگ فقط اطلاعات ویدیو رو چاپ می‌کنه")
    parser.add_argument("--upload", action="store_true", help="آپلود به یوتیوب")
    parser.add_argument("--dry-run", action="store_true", help="همراه --upload: فقط payload رو چاپ می‌کنه")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], help="وضعیت انتشار یوتیوب")
    parser.add_argument("--no-thumbnail", action="store_true", help="تامبنیل سفارشی (فریمی از خود ویدیو) ست نشه")
    parser.add_argument("--intro-seconds", type=float, default=3.0, help="مدت کارت مقدمه در ویدیوی ورودی (برای رد شدن از روش موقع انتخاب فریم تامبنیل)")
    parser.add_argument("--outro-seconds", type=float, default=2.5, help="مدت کارت پایان‌بندی در ویدیوی ورودی (همون منطق تامبنیل)")
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

    description = ensure_hashtags(args.description, category=args.category)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    video_id = upload_video(
        file_path=final_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
    )

    if video_id and not args.no_thumbnail:
        thumb_path = final_path + ".thumb.jpg"
        try:
            extract_thumbnail(
                final_path, thumb_path,
                intro_seconds=args.intro_seconds, outro_seconds=args.outro_seconds,
            )
            set_thumbnail(video_id, thumb_path)
        except Exception as e:
            print(f"⚠️  تامبنیل ست نشد (خود ویدیو مشکلی نداره): {e}")
        finally:
            if os.path.exists(thumb_path):
                os.remove(thumb_path)


if __name__ == "__main__":
    main()
