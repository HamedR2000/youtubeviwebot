"""صفحه‌ها را از src/ می‌سازد و موتور مشترک را درون هر فایل قرار می‌دهد تا هر صفحه مستقل باز شود.

src/*.html       → samples/  (نمونه‌های طراحی)
src/site/*.html  → site/     (سایت اصلی دو زبانه)
"""
from pathlib import Path

root = Path(__file__).parent
shared = (root / "src" / "shared.js").read_text(encoding="utf-8")
for src, out in ((root / "src", root / "samples"), (root / "src" / "site", root / "site")):
    out.mkdir(exist_ok=True)
    for page in sorted(src.glob("*.html")):
        html = page.read_text(encoding="utf-8").replace("/*@SHARED@*/", shared)
        (out / page.name).write_text(html, encoding="utf-8")
        print("built", out.name + "/" + page.name)
