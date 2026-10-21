"""نقطه‌ی ورود استاندارد برای آپلود یه بچ ویدیوی آماده (بعد از compose/edit) --
طبق خواسته‌ی کاربر: از هر بچی که می‌فرسته، ۵ تای اول همون لحظه public
می‌شن، و باقی (بیشتر از ۵) private آپلود می‌شن و **همون لحظه‌ی آپلود**
(نه بعداً) یه زمان دقیق انتشار می‌گیرن -- دسته‌های ۵تایی، هر دسته ۴ ساعت
بعد از دسته‌ی قبلی توی صف (queue_process.py صف رو هر ۴ ساعت پردازش می‌کنه).

    python batch_upload.py --dir path/to/edited --files a.mp4 b.mp4 ...
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

from queue_process import enqueue_batch

IMMEDIATE_COUNT = 5

ID_RE = re.compile(r"آپلود کامل شد: https://youtube\.com/shorts/(\S+)")
TITLE_RE = re.compile(r"عنوان نهایی: (.+)")


def main() -> None:
    parser = argparse.ArgumentParser(description="آپلود یه بچ: ۵ تای اول فوری public، باقی private + زمان‌بندی فوری")
    parser.add_argument("--dir", required=True, help="پوشه‌ی فایل‌های نهایی (بعد از compose/edit)")
    parser.add_argument("--files", nargs="+", required=True, help="اسم فایل‌ها (نسبت به --dir)، به‌ترتیب")
    parser.add_argument("--category", help="ژانر (اختیاری) -- پاس داده می‌شه به publish_ready.py")
    args = parser.parse_args()

    overflow_items = []
    results = []
    for i, fname in enumerate(args.files):
        path = os.path.join(args.dir, fname)
        immediate = i < IMMEDIATE_COUNT
        mode = "public (فوری)" if immediate else "private (صف)"
        print(f"[{i + 1}/{len(args.files)}] {fname} -> {mode}", flush=True)

        cmd = [
            "python3", "publish_ready.py",
            "--video", path,
            "--approve", "--upload", "--no-banner",
        ]
        cmd += ["--privacy", "public"] if immediate else ["--queue"]
        if args.category:
            cmd += ["--category", args.category]

        proc = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)

        id_match = ID_RE.search(proc.stdout)
        title_match = TITLE_RE.search(proc.stdout)
        video_id = id_match.group(1) if id_match else None
        title = title_match.group(1) if title_match else ""
        results.append({"file": fname, "immediate": immediate, "video_id": video_id, "title": title, "rc": proc.returncode})

        if not immediate and video_id:
            overflow_items.append({"video_id": video_id, "title": title})

    scheduled = enqueue_batch(overflow_items) if overflow_items else []
    for entry, item in zip(scheduled, overflow_items):
        when = datetime.datetime.fromtimestamp(entry["scheduled_at"]).strftime("%Y-%m-%d %H:%M")
        print(f"زمان‌بندی شد: {item['video_id']} -> پابلیش در {when}")

    print("ALL DONE")


if __name__ == "__main__":
    main()
