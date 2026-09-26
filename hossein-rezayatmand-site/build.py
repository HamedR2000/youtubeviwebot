"""نمونه‌ها را از src/ می‌سازد و موتور مشترک را درون هر فایل قرار می‌دهد تا هر صفحه مستقل باز شود."""
from pathlib import Path

root = Path(__file__).parent
shared = (root / "src" / "shared.js").read_text(encoding="utf-8")
out = root / "samples"
out.mkdir(exist_ok=True)
for page in sorted((root / "src").glob("*.html")):
    html = page.read_text(encoding="utf-8").replace("/*@SHARED@*/", shared)
    (out / page.name).write_text(html, encoding="utf-8")
    print("built", page.name)
