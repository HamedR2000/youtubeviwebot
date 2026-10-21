"""زمان‌بندی انتشار -- طبق درخواست کاربر، ویدیوها بلافاصله بعد از آپلود
به‌صورت عمومی منتشر نمی‌شن؛ اول با privacyStatus=private آپلود می‌شن (خودِ
یوتیوب نگهشون می‌داره، نه این سرور) و آی‌دی‌شون به queue/publish_queue.json
اضافه می‌شه. این اسکریپت (هر ۴ ساعت یک‌بار، از طریق یه cron job) حداکثر
BATCH_SIZE تای اول صف رو از private به public تغییر می‌ده.

عمداً فایل‌های ویدیویی هیچ‌وقت توی گیت ذخیره نمی‌شن -- فقط آی‌دی/عنوان
(متادیتای سبک و بی‌خطر) توی publish_queue.json که توی گیت کامیت/پوش
می‌شه تا صف بین اجراها (با فاصله‌ی چند ساعته) از بین نره.

    python queue_process.py
"""
import json
import os
import time

from googleapiclient.discovery import build
from youtube_upload import _get_credentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_PATH = os.path.join(BASE_DIR, "queue", "publish_queue.json")
BATCH_SIZE = 5
MIN_GAP_SECONDS = 4 * 3600


def load_queue() -> dict:
    with open(QUEUE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("last_run", 0)
    return data


def save_queue(data: dict) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def enqueue(video_id: str, title: str) -> None:
    """بعد از آپلود یه ویدیوی private جدید، آی‌دیش رو به صف انتشار اضافه
    می‌کنه -- وقتی batch size پر بشه، queue_process.py (زمان‌بندی‌شده)
    به‌ترتیب public‌شون می‌کنه."""
    queue = load_queue()
    queue["pending"].append({"video_id": video_id, "title": title})
    save_queue(queue)


def process_batch() -> list[dict]:
    queue = load_queue()
    batch = queue["pending"][:BATCH_SIZE]
    if not batch:
        print("صف خالیه -- ویدیوی در انتظار انتشار نیست.")
        return []

    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    results = []
    for entry in batch:
        vid = entry["video_id"]
        print(f"در حال پابلیک‌کردن {vid} ({entry.get('title', '')}) ...", flush=True)
        try:
            youtube.videos().update(
                part="status", body={"id": vid, "status": {"privacyStatus": "public"}}
            ).execute()
            results.append({**entry, "ok": True})
            queue["pending"] = [e for e in queue["pending"] if e["video_id"] != vid]
            queue["history"].append(entry)
        except Exception as e:
            print(f"❌ خطا در پابلیک‌کردن {vid}: {e}")
            results.append({**entry, "ok": False, "error": str(e)})
            # توی pending می‌مونه تا دفعه‌ی بعد دوباره امتحان بشه

    queue["last_run"] = time.time()
    save_queue(queue)
    return results


def process_if_due(min_gap_seconds: int = MIN_GAP_SECONDS) -> list[dict]:
    """شبکه‌ی ایمنی: اگه cron به هر دلیلی (مثلاً از بین رفتن سشن) اجرا نشه،
    هر بار که این فایل صدا زده می‌شه (مثلاً موقع آپلود بچ بعدی) چک می‌کنه
    اگه حداقل ۴ ساعت از آخرین اجرا گذشته و صف خالی نیست، یه بچ رو پابلیک کنه."""
    queue = load_queue()
    if not queue["pending"]:
        return []
    if time.time() - queue.get("last_run", 0) < min_gap_seconds:
        return []
    return process_batch()


if __name__ == "__main__":
    results = process_batch()
    print(json.dumps(results, ensure_ascii=False, indent=2))
