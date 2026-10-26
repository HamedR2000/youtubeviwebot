"""نقطه‌ی ورود استاندارد برای آپلود یه بچ ویدیوی آماده (بعد از compose/edit) --
طبق خواسته‌ی کاربر: هر ویدیویی که فرستاده می‌شه، همون لحظه public منتشر
می‌شه (بدون صف/تأخیر).

    python batch_upload.py --dir path/to/edited --files a.mp4 b.mp4 ...
"""
import argparse
import os
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="آپلود یه بچ: همه فوری public")
    parser.add_argument("--dir", required=True, help="پوشه‌ی فایل‌های نهایی (بعد از compose/edit)")
    parser.add_argument("--files", nargs="+", required=True, help="اسم فایل‌ها (نسبت به --dir)، به‌ترتیب")
    parser.add_argument("--category", help="ژانر (اختیاری) -- پاس داده می‌شه به publish_ready.py")
    args = parser.parse_args()

    for i, fname in enumerate(args.files):
        path = os.path.join(args.dir, fname)
        print(f"[{i + 1}/{len(args.files)}] {fname} -> public (فوری)", flush=True)

        cmd = [
            "python3", "publish_ready.py",
            "--video", path,
            "--approve", "--upload", "--no-banner",
            "--privacy", "public",
        ]
        if args.category:
            cmd += ["--category", args.category]

        proc = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)

    print("ALL DONE")


if __name__ == "__main__":
    main()
