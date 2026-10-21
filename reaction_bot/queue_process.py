"""زمان‌بندی انتشار -- طبق درخواست کاربر، از هر بچ ویدیو: ۵ تای اول همون
لحظه‌ی آپلود public می‌شن (توی batch_upload.py)، و بقیه (overflow) با
privacyStatus=private آپلود می‌شن و همون لحظه‌ی آپلود (نه بعداً) یه زمان
دقیق انتشار (scheduled_at) می‌گیرن: دسته‌های ۵تایی، هر دسته ۴ ساعت بعد از
دسته‌ی قبلی توی صف.

این اسکریپت (هر ۴ ساعت یک‌بار، از طریق یه cron job -- و هم به‌عنوان شبکه‌ی
ایمنی هر بار که batch_upload.py صدا زده می‌شه) هر آیتمی از صف که
scheduled_at‌ش گذشته رو از private به public تغییر می‌ده. اگه چیزی due
نباشه، کاری نمی‌کنه (idempotent -- هر وقت صدا زده بشه امنه).

عمداً فایل‌های ویدیویی هیچ‌وقت توی گیت ذخیره نمی‌شن -- فقط آی‌دی/عنوان/زمان
(متادیتای سبک و بی‌خطر) توی publish_queue.json که توی گیت کامیت/پوش می‌شه
تا صف بین اجراها (با فاصله‌ی چند ساعته، و حتی اگه خودِ سشن/cron از بین
برود) از بین نره.

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
INTERVAL_SECONDS = 4 * 3600


def load_queue() -> dict:
    with open(QUEUE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("last_run", 0)
    return data


def save_queue(data: dict) -> None:
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def enqueue_batch(items: list[dict]) -> list[dict]:
    """یه دسته از ویدیوهای overflow (private آپلود شده) رو به صف اضافه
    می‌کنه و همون لحظه برای هرکدوم scheduled_at (زمان دقیق unix) تعیین
    می‌کنه -- دسته‌های BATCH_SIZE تایی، هر دسته INTERVAL_SECONDS بعد از
    دسته‌ی قبلی توی صف (یا بعد از الان، اگه صف خالی بود). همون لیست رو با
    scheduled_at برمی‌گردونه تا بشه زمان‌ها رو به کاربر گزارش داد."""
    queue = load_queue()
    pending = queue["pending"]
    now = time.time()

    if pending:
        last_slot_time = max(e["scheduled_at"] for e in pending)
        last_slot_count = sum(1 for e in pending if e["scheduled_at"] == last_slot_time)
    else:
        last_slot_time = now
        last_slot_count = BATCH_SIZE  # یعنی صف خالیه -- دسته‌ی جدید شروع بشه

    slot_time = last_slot_time
    slot_count = last_slot_count
    scheduled = []
    for item in items:
        if slot_count >= BATCH_SIZE:
            slot_time = (slot_time if slot_time > now else now) + INTERVAL_SECONDS
            slot_count = 0
        entry = {**item, "scheduled_at": slot_time}
        pending.append(entry)
        scheduled.append(entry)
        slot_count += 1

    save_queue(queue)
    return scheduled


def process_due() -> list[dict]:
    """هر آیتم از صف که scheduled_at‌ش رسیده (یا گذشته) رو public می‌کنه.
    اگه چیزی due نباشه، هیچ کاری نمی‌کنه -- امن برای صدا زدن در هر لحظه
    (هم از cron، هم به‌عنوان شبکه‌ی ایمنی موقع آپلود بچ بعدی)."""
    queue = load_queue()
    now = time.time()
    due = [e for e in queue["pending"] if e["scheduled_at"] <= now]
    if not due:
        return []

    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    results = []
    for entry in due:
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

    queue["last_run"] = now
    save_queue(queue)
    return results


if __name__ == "__main__":
    results = process_due()
    if not results:
        print("چیزی due نبود -- صف خالیه یا هنوز نوبت هیچ‌کدوم نرسیده.")
    print(json.dumps(results, ensure_ascii=False, indent=2))
