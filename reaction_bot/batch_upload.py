"""نقطه‌ی ورود استاندارد برای آپلود یه بچ ویدیوی آماده (بعد از compose/edit) --
طبق خواسته‌ی کاربر: از هر بچی که می‌فرسته، ۵ تای اول همون لحظه public
می‌شن، و باقی (بیشتر از ۵) private آپلود و به صف زمان‌بندی‌شده
(queue_process.py, هر ۴ ساعت یک بار) اضافه می‌شن.

    python batch_upload.py --dir path/to/edited --files a.mp4 b.mp4 ...
"""
import argparse
import os
import subprocess
import sys

IMMEDIATE_COUNT = 5


def main() -> None:
    parser = argparse.ArgumentParser(description="آپلود یه بچ: ۵ تای اول فوری public، باقی private+queue")
    parser.add_argument("--dir", required=True, help="پوشه‌ی فایل‌های نهایی (بعد از compose/edit)")
    parser.add_argument("--files", nargs="+", required=True, help="اسم فایل‌ها (نسبت به --dir)، به‌ترتیب")
    parser.add_argument("--category", help="ژانر (اختیاری) -- پاس داده می‌شه به publish_ready.py")
    args = parser.parse_args()

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
        if immediate:
            cmd += ["--privacy", "public"]
        else:
            cmd += ["--queue"]
        if args.category:
            cmd += ["--category", args.category]

        proc = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
        results.append({"file": fname, "immediate": immediate, "rc": proc.returncode, "stdout": proc.stdout})

    print("ALL DONE")


if __name__ == "__main__":
    main()
