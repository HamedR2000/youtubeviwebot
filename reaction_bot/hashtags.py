"""هشتگ‌های description هر آپلود. یوتیوب حداکثر ۱۵ تا هشتگ رو قبول
می‌کنه -- بیشتر از اون بشه، همه‌شون (نه فقط اضافه‌ها) نادیده گرفته
می‌شن، پس عمداً همینجا زیر اون سقف نگهش داشتیم.

برای این‌که هر ویدیو یه ترکیب یکسان و تکراری نگیره، از یه استخر بزرگ
و متنوع، هر بار یه زیرمجموعه‌ی تصادفی انتخاب می‌شه. اگه ژانر ویدیو رو
از قبل می‌دونی (مثلاً prank یا family)، با پارامتر category بده تا
چندتا هشتگ مرتبط‌تر هم اضافه بشه."""

import random

CORE_HASHTAGS = ["#Shorts", "#ری_اکشن"]

GENERAL_POOL = [
    "#خنده", "#خنده_دار", "#طنز", "#طنز_ایرانی", "#کلیپ_طنز", "#کمدی",
    "#ایرانی", "#فارسی", "#فان", "#سرگرمی", "#شوخی", "#خنده_واقعی",
    "#کلیپ_باحال", "#کلیپ_خنده_دار", "#طنز_واقعی", "#خنده_تضمینی",
    "#ویدیوی_خنده_دار", "#موقعیت_خنده_دار", "#کلیپ_ایرانی", "#خنده_از_ته_دل",
    "#طنز_خنده_دار", "#لحظه_خنده_دار", "#کلیپ_فان", "#خنده_دار_ترین",
    "#reaction", "#comedy", "#funny", "#funnyvideos", "#viral", "#fyp",
    "#laugh", "#lol", "#trending", "#shortsfeed", "#ytshorts", "#comedyvideos",
    "#funnymoments", "#instafunny", "#persian", "#iranian",
]

CATEGORY_POOLS = {
    "family": ["#خانوادگی", "#طنز_خانوادگی", "#مادر_و_دختر", "#خواهر_برادر", "#family", "#familyfunny"],
    "couple": ["#زوج_خنده_دار", "#ازدواج", "#طنز_زناشویی", "#couplegoals", "#relationship"],
    "prank": ["#پرانک", "#پرانک_ایرانی", "#شوخی_باحال", "#prank", "#pranks"],
    "kids": ["#بچه_ها", "#کودک", "#طنز_کودکانه", "#kids", "#cutekids"],
    "pets": ["#حیوان_خانگی", "#سگ", "#گربه", "#pets", "#animals"],
    "talk": ["#دل_نوشته", "#واقعیت_زندگی", "#حرف_دل", "#رابطه"],
    "fail": ["#شکست_خنده", "#اتفاق_خنده_دار", "#fail", "#epicfail"],
}


def ensure_hashtags(description: str, category: str | None = None, count: int = 13) -> str:
    """اگه description از قبل هیچ هشتگی نداشت، یه ترکیب تصادفی از
    CORE + (چندتا هشتگ مرتبط با category، اگه داده باشی) + بقیه از
    GENERAL_POOL رو ته‌ش اضافه می‌کنه، جوری که جمعاً از ۱۵ تا رد نشه.
    اگه خودت هشتگ گذاشته باشی، دست‌نخورده می‌مونه."""
    if "#" in description:
        return description

    picked: list[str] = []
    if category and category in CATEGORY_POOLS:
        pool = CATEGORY_POOLS[category]
        picked.extend(random.sample(pool, min(3, len(pool))))

    remaining = count - len(picked)
    general_choices = [t for t in GENERAL_POOL if t not in picked]
    picked.extend(random.sample(general_choices, min(remaining, len(general_choices))))

    tags = CORE_HASHTAGS + picked
    return (description + "\n\n" + " ".join(tags)).strip()
