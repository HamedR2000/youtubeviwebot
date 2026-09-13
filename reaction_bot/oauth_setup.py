"""راه‌اندازی یک‌باره‌ی دسترسی یوتیوب، مخصوص محیطی که مرورگر نداره (این
سرور). فلوی معمول OAuth (`run_local_server`) نیاز به مرورگر روی همون
ماشین داره؛ این اسکریپت به‌جاش خودت لینک رو دستی توی مرورگر خودت باز
می‌کنی و کد برگشتی رو برمی‌گردونی اینجا.

قدم ۱ (روی همین سرور): این رو اجرا کن و لینکی که می‌ده رو باز کن.

    python oauth_setup.py --print-url

قدم ۲: توی مرورگر خودت، لینک رو باز کن، با اکانت یوتیوبت وارد شو، اجازه
بده. صفحه‌ی بعدی یه ارور «نمی‌شه وصل شد» می‌ده -- عادیه، چون سروری پشت
localhost نیست. کل آدرس همون صفحه‌ی ارور رو از نوار آدرس کپی کن.

قدم ۳ (دوباره روی همین سرور): همون آدرس کپی‌شده رو بده به این دستور --
توکن رو می‌سازه و ذخیره می‌کنه، دیگه نیازی به تکرار نیست.

    python oauth_setup.py --exchange "http://localhost:8080/?state=...&code=..."
"""
import argparse

from google_auth_oauthlib.flow import Flow

from config import config

REDIRECT_URI = "http://localhost:8080/"


def _build_flow() -> Flow:
    return Flow.from_client_secrets_file(
        config.YOUTUBE_CLIENT_SECRETS_FILE,
        scopes=[config.YOUTUBE_UPLOAD_SCOPE],
        redirect_uri=REDIRECT_URI,
    )


def print_url() -> None:
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    print("این لینک رو توی مرورگر خودت باز کن:\n")
    print(auth_url)
    print("\nبعد از تأیید، آدرس کامل صفحه‌ی بعدی (حتی اگه ارور داد) رو کپی کن و با:")
    print('  python oauth_setup.py --exchange "همون آدرس"')
    print("بفرستش برام تکمیلش کنم.")


def exchange(redirected_url: str) -> None:
    flow = _build_flow()
    flow.fetch_token(authorization_response=redirected_url)
    with open(config.YOUTUBE_TOKEN_FILE, "w") as f:
        f.write(flow.credentials.to_json())
    print(f"دسترسی یوتیوب با موفقیت ذخیره شد: {config.YOUTUBE_TOKEN_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="راه‌اندازی یک‌باره‌ی OAuth یوتیوب بدون مرورگر روی این سرور")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--print-url", action="store_true", help="لینک تأیید رو چاپ می‌کنه (قدم ۱)")
    group.add_argument("--exchange", metavar="REDIRECTED_URL", help="آدرس برگشتی بعد از تأیید رو می‌گیره و توکن می‌سازه (قدم ۳)")
    args = parser.parse_args()

    if args.print_url:
        print_url()
    else:
        exchange(args.exchange)


if __name__ == "__main__":
    main()
