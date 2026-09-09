# ربات پست خودکار روزانه اینستاگرام (نیچ ترید طلا)

این پوشه یه پایپ‌لاین کامله که هر روز خودکار:
1. یه کلیپ استوک رایگان و عمودی (متناسب با موضوع ترید/طلا) از Pexels می‌گیره.
2. روش متن (هوک + نکته آموزشی + برندینگ) می‌ذاره و موزیک بدون کپی‌رایت زیرش میکس می‌کنه.
3. ویدیوی نهایی رو (چون Instagram API فقط از روی URL عمومی می‌خونه) به‌عنوان Release در همین گیت‌هاب آپلود می‌کنه.
4. با Instagram Graph API پستش می‌کنه (به‌صورت Reel) همراه با کپشن + هشتگ‌های چرخشی + دیسکلایمر ریسک.
5. وضعیت (چه کلیپ‌ها/هوک‌ها/هشتگ‌هایی استفاده شده) رو توی `state.json` ذخیره می‌کنه تا تکراری نشه.

زمان‌بندی روزانه‌ش با GitHub Actions انجام می‌شه (`.github/workflows/daily_post.yml`) — نیاز به سرور شخصی نداری.

---

## قبل از هر چیز: تبدیل اکانت به Business/Creator

اکانت شخصی الان قابل اتصال به API نیست. این کار رو داخل اپ اینستاگرام انجام بده:

1. `Settings → Account type and tools → Switch to professional account`
2. نوع رو `Creator` یا `Business` انتخاب کن (برای فروش محصول، `Business` مناسب‌تره).
3. توی مراحلش بهت پیشنهاد می‌ده به یه **صفحه فیسبوک** وصلش کنی — این اجباریه، چون Graph API از طریق صفحه فیسبوک به اینستاگرام وصل می‌شه. اگه صفحه فیسبوک نداری، همون‌جا یکی بساز (رایگانه، نیازی نیست فالوور داشته باشه).

## ساخت اپ متا و گرفتن توکن

1. برو به [developers.facebook.com](https://developers.facebook.com/) و یه اپ جدید بساز (نوع: **Business**).
2. توی داشبورد اپ، محصول **Instagram Graph API** رو اضافه کن.
3. از ابزار [Graph API Explorer](https://developers.facebook.com/tools/explorer/) استفاده کن:
   - اپت رو انتخاب کن، خودت رو با فیسبوک لاگین کن.
   - پرمیژن‌های `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement` رو اضافه کن و یه **User Access Token** بگیر.
4. با همون توکن، `GET /me/accounts` رو بزن تا `id` صفحه فیسبوکت رو پیدا کنی.
5. با `page id`، بزن `GET /{page-id}?fields=instagram_business_account` تا **IG Business Account ID** رو پیدا کنی — این می‌شه `IG_USER_ID`.
6. توکن کوتاه‌مدتیه که گرفتی رو به یه **Long-Lived Token** (۶۰ روزه) تبدیل کن:
   ```
   GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
   ```
   این می‌شه `IG_ACCESS_TOKEN`.

⚠️ **نکته مهم:** این توکن حداکثر ۶۰ روز اعتبار داره و باید دستی یا با یه اسکریپت جدا رفرش بشه، وگرنه ربات بعد از ۶۰ روز متوقف می‌شه. یه یادآور توی تقویم خودت بذار.

در حالت Development اپ، فقط اکانت‌هایی که به‌عنوان Tester/Admin به اپ اضافه کردی (یعنی خودت) کار می‌کنن — برای استفاده شخصی نیازی به App Review کامل متا نیست.

## گرفتن کلید Pexels

برو [pexels.com/api](https://www.pexels.com/api/) و رایگان یه API key بگیر → `PEXELS_API_KEY`.

## اضافه کردن موزیک

فایل‌های mp3 بدون کپی‌رایت رو بریز توی `instagram_bot/music/` (توضیح منابع رایگان توی `music/README.md` هست). بدون حداقل یه فایل، ربات ارور می‌ده و پست نمی‌کنه — عمداً همینه که یادت نره.

## تنظیم Secrets توی گیت‌هاب

برو `Settings → Secrets and variables → Actions → New repository secret` و این‌ها رو اضافه کن:

| Secret | مقدار |
|---|---|
| `IG_USER_ID` | همون Instagram Business Account ID |
| `IG_ACCESS_TOKEN` | Long-Lived Token |
| `PEXELS_API_KEY` | کلید Pexels |

(`GITHUB_TOKEN` نیازی به ست کردن دستی نداره — GitHub Actions خودکار می‌سازتش.)

## قبل از فعال کردن، این‌ها رو دستی عوض کن

- توی `instagram_bot/main.py` مقدار `BRAND_HANDLE = "@your_handle"` رو با آیدی واقعی پیجت جایگزین کن.
- توی `instagram_bot/content_bank.py` هوک‌ها/نکته‌ها/CTAها/هشتگ‌ها رو بخون و با لحن و محصول واقعی خودت (اسم ربات معامله‌گر، لینک بیو) هماهنگ کن.
- زمان‌بندی cron توی `.github/workflows/daily_post.yml` (الان `15:00 UTC`) رو با بهترین ساعت فعالیت مخاطب‌هات تنظیم کن.

## اجرای محلی (برای تست قبل از فعال کردن cron)

```bash
cd instagram_bot
pip install -r requirements.txt
export IG_USER_ID=...
export IG_ACCESS_TOKEN=...
export PEXELS_API_KEY=...
export GITHUB_TOKEN=...            # یه Personal Access Token با scope مخزن
export GITHUB_REPOSITORY=owner/repo
python main.py
```

## محدودیت‌ها و نکات مهم

- **موزیک رسمی اینستاگرام (Reels audio library) از طریق API قابل انتخاب نیست** — به همین خاطر موزیک از قبل داخل خود فایل ویدیو میکس می‌شه (روش قانونی و پایدارتر).
- Content Publishing API محدودیت نرخ داره (حدود ۲۵ پست در روز برای هر اکانت) — یه پست در روز خیلی زیر این سقفه.
- چون Actions فقط روی برنچ پیش‌فرض (`main`) طبق زمان‌بندی cron اجرا می‌شه، بعد از مرج این تغییرات به `main`، زمان‌بندی خودکار فعال می‌شه؛ تا قبلش فقط با دکمه‌ی «Run workflow» (workflow_dispatch) توی تب Actions قابل تست دستیه.
- محتوای مرتبط با ترید/فروش ربات معامله‌گر ممکنه هدف بازبینی‌های سیاست تبلیغات مالی متا قرار بگیره؛ به همین دلیل دیسکلایمر ریسک توی هر کپشن اجباریه — لطفاً حذفش نکن و از ادعای «سود تضمینی» پرهیز کن.
