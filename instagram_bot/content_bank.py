"""Content bank for the gold/forex trading niche (English only).

Everything here is plain data: hooks, tips, hashtags, CTAs. main.py and
caption_builder.py pick from these lists so every post is a fresh
combination instead of a repeated template. Edit these lists freely to
match your voice -- no code changes needed elsewhere.
"""

# Search terms used against the Pexels API. Keep these visual and generic;
# Pexels has no literal "gold trading" footage, so we mix finance-adjacent
# and gold-adjacent scenes that read well with a text overlay.
STOCK_SEARCH_TERMS = [
    "gold bars",
    "stock market chart",
    "trading desk",
    "forex chart screen",
    "candlestick chart",
    "financial graph",
    "business chart growth",
    "money currency",
    "stock exchange",
    "investment finance",
]

# Short, punchy hooks -- the first line of the caption / on-video text.
# This is what stops the scroll, so keep each under ~60 characters.
HOOKS = [
    "Gold doesn't lie. Your strategy might.",
    "3 seconds to check gold before you trade it.",
    "The one gold setup most traders miss.",
    "Why XAU/USD keeps humbling traders this week.",
    "Gold is telling a story. Are you reading it?",
    "This is the level gold traders are watching.",
    "Stop guessing gold's next move.",
    "Every pip on gold has a reason. Here's one.",
    "The market moved. Did your plan?",
    "Read this before your next gold trade.",
    "Most gold traders lose to their own hesitation, not the market.",
    "Here's what separates a plan from a hope.",
    "Gold rewards patience more than it rewards speed.",
    "The chart already told you. Did you listen?",
    "A clean setup doesn't need a loud caption.",
    "What's your biggest lesson from a losing trade?",
]

# Educational / value-add tips. These are intentionally generic market
# education, not personalized financial advice or return promises.
TIPS = [
    "Gold tends to react sharply around US CPI and NFP releases -- mark your calendar.",
    "A strong US Dollar Index (DXY) usually pressures gold lower, and vice versa.",
    "Round numbers like $2,000 or $2,300 often act as psychological support/resistance on XAU/USD.",
    "Risk management beats prediction: define your stop-loss before you enter, not after.",
    "Gold often moves inversely to real yields -- worth watching alongside the price chart.",
    "Overtrading during low-volume Asian sessions is a common gold-trading mistake.",
    "A trading journal turns random trades into a repeatable process.",
    "Volatility spikes around FOMC meetings -- position size accordingly.",
    "Support and resistance are zones, not exact lines. Give trades room to breathe.",
    "The best setup is worthless without the discipline to follow your own rules.",
    "Gold's daily range compresses before major news -- a quiet chart isn't a dead chart.",
    "Correlation isn't causation, but DXY, yields, and gold rarely move in isolation.",
    "A missed trade costs you nothing. A bad trade can cost you weeks.",
    "Backtesting a setup once isn't validation -- consistency over time is.",
]

# Calls-to-action promoting the trading bot (sold as a 6-month or 1-year
# subscription via the Telegram channel linked in bio, or by DM). Kept
# factual (no "guaranteed profit" / "get rich" language) to stay within
# Instagram's ad policy norms and basic advertising-honesty practice.
CTAS = [
    "Want your gold trades executed with zero emotion? Join the Telegram channel in my bio -- 6-month & 1-year access available.",
    "I trade with my own automated expert on gold. Get it via the Telegram in bio, or just DM me.",
    "Tired of watching charts all day? My bot does it for you. Telegram channel in bio for subscription options.",
    "Automate your gold strategy the way I do -- Telegram link in bio, or DM me for details.",
    "Consistency beats emotion. That's why I trade with my own bot -- 6-month & 1-year plans open, link in bio.",
    "Every signal I post, my own bot executes -- no manual clicks, no hesitation. Link in bio.",
    "Works with your broker or prop firm, you just set the lot size. Message us to get started.",
    "A ready XAUUSD preset, tested and optimized -- 6-month or 1-year license, full support included.",
    "Stop watching charts all day. Let the bot trade the plan while you live your life. Link in bio.",
    "Same signals, zero delay, zero emotion -- that's what automation buys you. DM for details.",
    "No fear, no greed -- just logic. Every entry and exit calculated before the trade, not during it. Link in bio.",
    "Precise entry, precise exit, zero emotion -- that's the whole edge. Telegram in bio for access.",
]

# Mandatory risk disclaimer appended to every caption. Do not remove --
# trading content without a risk disclosure is misleading and can violate
# advertising standards in many jurisdictions.
DISCLAIMER = (
    "⚠️ Educational content only, not financial advice. "
    "Trading gold/forex carries a high level of risk and may not be suitable for everyone. "
    "Past performance does not guarantee future results."
)

# Evergreen hashtag pool for the niche. main.py rotates a subset of these
# each day (Instagram caps usable hashtags and repeating the exact same 30
# every day looks spammy / can suppress reach).
HASHTAGS = [
    "#gold", "#goldtrading", "#xauusd", "#forex", "#forextrading",
    "#trading", "#tradingbot", "#daytrading", "#swingtrading",
    "#stockmarket", "#investing", "#financialfreedom", "#priceaction",
    "#technicalanalysis", "#tradingsignals", "#forexsignals",
    "#goldprice", "#preciousmetals", "#wallstreet", "#tradertips",
    "#tradingstrategy", "#algotrading", "#fintech", "#tradinglife",
    "#forexmarket", "#goldinvestment", "#tradereducation", "#usdollar",
    "#marketanalysis", "#automatedtrading",
]

# Branded/always-on tags -- identity hashtags kept in every post regardless
# of rotation.
BRAND_HASHTAGS = ["#goldhamedsignals"]

# Auto-reply templates for comments on our own posts (reply_comments.py).
# "{name}" is filled with the commenter's Instagram username. Language is
# picked per-comment by detecting Persian/Arabic script in their comment
# text (see comment_autoresponder.py) -- these invite them to the free
# Telegram channel, not the paid bot, so they stay a soft, honest CTA.
COMMENT_REPLIES_EN = [
    "Hey {name}, thanks for stopping by! \U0001F64C We share free XAUUSD signals & daily analysis in our Telegram channel -- link in bio, come join us!",
    "Appreciate you, {name}! \U0001F64F Free gold signals + daily breakdowns are waiting for you in our Telegram -- link in bio.",
    "Thanks for the love, {name}! Join our free Telegram channel (link in bio) for daily XAUUSD signals and analysis.",
]

COMMENT_REPLIES_FA = [
    "سلام {name} عزیز، ممنون که وقت گذاشتی \U0001F64C سیگنال‌های رایگان طلا و تحلیل روزانه رو تو کانال تلگرام‌مون داریم -- لینک تو بایو، بیا عضو شو!",
    "دستت درد نکنه {name}! \U0001F64F سیگنال رایگان طلا + تحلیل هر روز منتظرته تو تلگرام -- لینک تو بایو.",
    "ممنون از همراهیت {name}! کانال تلگرام رایگان‌مون رو از لینک تو بایو ببین، هر روز سیگنال XAUUSD می‌ذاریم.",
]

# The channel's actual Telegram invite link. Comments (like captions) never
# render links as tappable on Instagram -- only the bio link does -- but
# spelling it out here still lets people copy it straight from the post,
# which is what FIRST_COMMENT_EN/FA below are for.
TELEGRAM_CHANNEL_URL = "https://t.me/+L8xT0WpBnJtjZjA0"

# Auto-posted as the very first comment on every new Reel/feed post/carousel
# (main.py run_publish(), via instagram_publish.create_comment) -- an
# evergreen CTA with the channel link spelled out for easy copy-paste, not
# rotated since there's nothing to keep fresh about a fixed link.
FIRST_COMMENT_EN = f"\U0001F517 Free daily XAUUSD signals in our Telegram channel: {TELEGRAM_CHANNEL_URL}"
FIRST_COMMENT_FA = f"\U0001F517 سیگنال‌های رایگان روزانه‌ی طلا تو کانال تلگرام‌مون: {TELEGRAM_CHANNEL_URL}"

# Story cards are read in ~2 seconds each, so lines stay short -- but a
# whole day's STORIES_PER_DAY slides come from ONE set here, not random
# picks off a flat list, so the sequence reads as one connected thread
# (a shared "topic" kicker + a build-up) instead of disconnected one-liners.
# Each set must have exactly STORIES_PER_DAY (see main.py) lines.
STORY_SETS = [
    {
        "topic": "RISK FIRST",
        "lines": [
            "Before you enter, know your exit.",
            "Risk 1%, not your whole week.",
            "Your stop-loss is not optional.",
            "Protect your capital first. Grow it second.",
            "A small profit beats a big loss.",
        ],
    },
    {
        "topic": "AFTER A LOSS",
        "lines": [
            "You just took a loss. Don't rush back in.",
            "Close the chart. Breathe. Reset.",
            "One loss is data, not a verdict.",
            "Review the trade, not your worth.",
            "Come back only when your plan is clear again.",
        ],
    },
    {
        "topic": "WHY WE AUTOMATE",
        "lines": [
            "Every signal we post, our bot executes.",
            "No manual clicks. No hesitation.",
            "Runs on MT5, on your PC -- not your phone.",
            "Works with any broker, any prop firm.",
            "6-month or 1-year license. Telegram in bio.",
        ],
    },
    {
        "topic": "PATIENCE PAYS",
        "lines": [
            "Gold rewards patience more than speed.",
            "The best trade is sometimes no trade.",
            "One good setup beats ten random trades.",
            "Boredom is not a reason to enter.",
            "Discipline works from anywhere -- a desk or a beach.",
        ],
    },
    {
        "topic": "READ THE CHART",
        "lines": [
            "Price action is the only truth.",
            "Support and resistance are zones, not lines.",
            "A quiet chart isn't a dead chart.",
            "Volatility spikes around big news -- size down.",
            "The chart already told you. Did you listen?",
        ],
    },
    {
        "topic": "EMOTIONS COST MONEY",
        "lines": [
            "Fear closes winners early.",
            "Greed holds losers too long.",
            "Emotions are the real spread cost.",
            "No emotion. Just logic and precision.",
            "That's why our bot trades it, not us.",
        ],
    },
    {
        "topic": "KNOW THE LEVELS",
        "lines": [
            "Round numbers like $2,000 act like magnets.",
            "DXY up, gold down. Usually.",
            "CPI and NFP days move gold hard.",
            "Real yields and gold rarely move alone.",
            "Know the calendar before you know the entry.",
        ],
    },
    {
        "topic": "PRECISE ENTRY, PRECISE EXIT",
        "lines": [
            "Every entry, every exit -- calculated, not guessed.",
            "No fear, no greed -- just logic.",
            "Pre-calculated levels. Zero manual clicks.",
            "Signal in. Trade out. Same process, every time.",
            "That's what automation buys you. Link in bio.",
        ],
    },
    {
        # Five real, sourced facts (account owner reviewed and picked
        # these from a larger researched list) instead of the usual
        # aphorisms -- BIS Triennial FX Survey 2025, ESMA 2025 retail-loss
        # data across 20 EU brokers, and gold's Jan 2026 record close
        # (sources clustered $5,405-5,602; using the rounded, safely
        # understated $5,600 rather than any single exact figure).
        "topic": "TRADE FACTS",
        "lines": [
            "$9.5 trillion moves through forex -- every single day.",
            "And yet 74-89% of retail traders still lose money in it.",
            "After 5 years, only 5-7% of traders are still profitable.",
            "Lose half your account, and the rest is usually gone within 90 days.",
            "Jan 2026: gold broke $5,600 for the first time in history.",
        ],
    },
    # Ten trading-principles/methodology topics, added at the account
    # owner's request after the original 9 sets started feeling repetitive.
    # Rotate once each before new topics get added again (see
    # story_set_cursor / story_set_fa_cursor in state.json).
    {
        "topic": "RISK:REWARD RATIO",
        "lines": [
            "Win rate doesn't matter as much as you think.",
            "A 40% win rate can still be profitable.",
            "What matters is your risk-to-reward ratio.",
            "Risk $1 to make $2 or more, every time.",
            "Do the math before the trade, not after.",
        ],
    },
    {
        "topic": "POSITION SIZING",
        "lines": [
            "Lot size isn't a feeling. It's a calculation.",
            "Risk a fixed % of your account, not a fixed lot.",
            "A $10k account and a $1k account need different sizes.",
            "Your stop-loss distance decides your position size.",
            "Same risk, every trade -- that's the goal.",
        ],
    },
    {
        "topic": "MULTI-TIMEFRAME ANALYSIS",
        "lines": [
            "The daily chart shows the story. The hourly shows the sentence.",
            "Trade with the higher timeframe trend.",
            "Use the lower timeframe only for your entry.",
            "Fighting the bigger trend is fighting the tide.",
            "Zoom out before you zoom in.",
        ],
    },
    {
        "topic": "TRADING AS A BUSINESS",
        "lines": [
            "A business has a plan. So should your trading.",
            "Track your numbers like a business tracks revenue.",
            "Rules first. Instincts second.",
            "No business survives without managing its losses.",
            "Treat it like a business, not a lottery ticket.",
        ],
    },
    {
        "topic": "DRAWDOWN MANAGEMENT",
        "lines": [
            "Every trader has losing streaks. Even the good ones.",
            "Cut your size when the losses pile up.",
            "A drawdown is a signal to slow down, not speed up.",
            "Protect what's left before you chase what's lost.",
            "Recovery starts with smaller risk, not bigger bets.",
        ],
    },
    {
        "topic": "TREND VS RANGE",
        "lines": [
            "Not every strategy works in every market.",
            "Trends reward patience. Ranges reward precision.",
            "Breakout strategies struggle in a sideways market.",
            "Know which one you're in before you enter.",
            "The chart tells you. Read it first.",
        ],
    },
    {
        "topic": "FOMO",
        "lines": [
            "The candle already moved. You didn't miss much.",
            "Chasing price is how late entries turn into early losses.",
            "If you missed the move, there's always another one.",
            "FOMO has no stop-loss.",
            "Wait for your setup, not the crowd's.",
        ],
    },
    {
        "topic": "LEVERAGE",
        "lines": [
            "Leverage doesn't create an edge. It multiplies the one you already have.",
            "The same leverage that doubles your win doubles your loss.",
            "High leverage, low size -- or it adds up fast.",
            "Leverage is a tool, not a shortcut.",
            "Respect it, or it won't respect you.",
        ],
    },
    {
        "topic": "SESSIONS & LIQUIDITY",
        "lines": [
            "Not all hours are equal for gold.",
            "London and New York overlap brings the real volume.",
            "Asian session often just drifts sideways.",
            "Thin liquidity means wider spreads and fake moves.",
            "Trade when the market is actually trading.",
        ],
    },
    {
        "topic": "BACKTEST FIRST",
        "lines": [
            "Test the idea before you trust it with real money.",
            "History doesn't repeat, but setups often do.",
            "A backtested edge beats a gut feeling.",
            "If it doesn't work on old charts, it won't work tomorrow.",
            "Prove it on paper before you prove it with capital.",
        ],
    },
]

# Persian equivalents of HOOKS -- used on Persian-language days (see
# ENGLISH_WEEKDAYS in main.py), same order/meaning as the English list.
HOOKS_FA = [
    "طلا دروغ نمی‌گه. شاید استراتژیت دروغ بگه.",
    "۳ ثانیه وقت بذار و طلا رو چک کن، قبل از معامله.",
    "ستاپی از طلا که بیشتر معامله‌گرها ازش رد می‌شن.",
    "چرا XAU/USD این هفته معامله‌گرها رو غافلگیر می‌کنه.",
    "طلا داره یک داستان رو تعریف می‌کنه. داری می‌خونیش؟",
    "این همون سطحیه که معامله‌گرهای طلا بهش زل زدن.",
    "دیگه حدس نزن طلا کجا می‌ره.",
    "هر پیپ طلا یک دلیل داره. اینم یکیش.",
    "بازار حرکت کرد. برنامه‌ت هم حرکت کرد؟",
    "قبل از معامله‌ی بعدی طلات، این رو بخون.",
    "بیشتر معامله‌گرهای طلا از تردید خودشون می‌بازن، نه از بازار.",
    "این چیزیه که یک برنامه رو از یک آرزو جدا می‌کنه.",
    "طلا به صبر بیشتر از سرعت پاداش می‌ده.",
    "چارت از قبل بهت گفته بود. گوش دادی؟",
    "یک ستاپ تمیز، به یک کپشن پرسروصدا نیاز نداره.",
    "بزرگ‌ترین درسِ تو از یک معامله‌ی ضررده چی بوده؟",
]

# Persian equivalents of TIPS.
TIPS_FA = [
    "طلا معمولاً دور و بر انتشار CPI و NFP آمریکا واکنش شدید نشون می‌ده -- تو تقویمت علامت بزن.",
    "معمولاً یک دلار قوی (DXY) روی طلا فشار نزولی می‌ذاره، و برعکس.",
    "اعداد رند مثل ۲۰۰۰ یا ۲۳۰۰ دلار معمولاً به‌عنوان حمایت/مقاومت روانی روی XAU/USD عمل می‌کنن.",
    "مدیریت ریسک از پیش‌بینی مهم‌تره: حد ضررت رو قبل از ورود مشخص کن، نه بعدش.",
    "طلا معمولاً برعکس بازده واقعی حرکت می‌کنه -- ارزش داره کنار چارت قیمت دنبالش کنی.",
    "بیش‌ازحد معامله کردن تو سشن کم‌حجم آسیا، یک اشتباه رایج تو معامله‌ی طلاست.",
    "یک ژورنال معاملاتی، معاملات تصادفی رو به یک فرآیند قابل‌تکرار تبدیل می‌کنه.",
    "نوسان دور و بر جلسات FOMC بالا می‌ره -- حجم پوزیشنت رو متناسب باهاش تنظیم کن.",
    "حمایت و مقاومت، ناحیه‌ن نه خط‌های دقیق. به معاملاتت فضای نفس‌کشیدن بده.",
    "بهترین ستاپ هم بدون نظمِ رعایتِ قوانین خودت، بی‌ارزشه.",
    "رنج روزانه‌ی طلا قبل از خبرهای مهم فشرده می‌شه -- چارت ساکت به معنی چارت مرده نیست.",
    "همبستگی به معنی علیت نیست، ولی DXY، بازده، و طلا به‌ندرت جدا از هم حرکت می‌کنن.",
    "یک معامله‌ی ازدست‌رفته هیچی برات هزینه نداره. یک معامله‌ی بد می‌تونه هفته‌ها برات هزینه داشته باشه.",
    "یک بار بک‌تست کردن یک ستاپ، اعتبارسنجی نیست -- ثبات در طول زمانه که اعتبار میاره.",
]

# Persian equivalents of CTAS.
CTAS_FA = [
    "می‌خوای معاملات طلات بدون هیچ احساسی اجرا بشه؟ به کانال تلگرام تو بایوم بپیوند -- دسترسی ۶ ماهه و ۱ ساله موجوده.",
    "من با ربات خودم روی طلا معامله می‌کنم. از تلگرام تو بایو بگیرش، یا مستقیم دایرکت بده.",
    "خسته شدی از دید زدن چارت تمام روز؟ رباتم این کار رو برات می‌کنه. برای گزینه‌های اشتراک، تلگرام تو بایو.",
    "استراتژی طلات رو دقیقاً مثل من خودکار کن -- لینک تلگرام تو بایو، یا برای جزئیات دایرکت بده.",
    "ثبات از احساسات مهم‌تره. برای همینه با ربات خودم معامله می‌کنم -- پلن‌های ۶ ماهه و ۱ ساله باز، لینک تو بایو.",
    "هر سیگنالی که پست می‌کنم، ربات خودم اجراش می‌کنه -- بدون کلیک دستی، بدون تردید. لینک تو بایو.",
    "با بروکر یا پراپ‌فرم تو کار می‌کنه، فقط حجم معامله رو تو مشخص کن. برای شروع پیام بده.",
    "یک پریست آماده‌ی XAUUSD، تست‌شده و بهینه -- لایسنس ۶ ماهه یا ۱ ساله، با پشتیبانی کامل.",
    "دیگه تمام روز چارت نگاه نکن. بذار ربات برنامه رو معامله کنه، تو زندگیت رو بکن. لینک تو بایو.",
    "همون سیگنال‌ها، بدون تأخیر، بدون احساس -- این چیزیه که خودکارسازی بهت می‌ده. برای جزئیات دایرکت بده.",
    "بدون ترس، بدون طمع -- فقط منطق. نقطه‌ی ورود و خروج هر معامله از قبل محاسبه می‌شه، نه وسط معامله. لینک تو بایو.",
    "ورود دقیق، خروج دقیق، بدون هیچ احساسی -- کل مزیتش همینه. برای دسترسی، تلگرام تو بایو.",
]

# Persian equivalent of DISCLAIMER -- appended to every Persian-day caption
# instead of the English one. Same legal/ethical content, not a paraphrase.
DISCLAIMER_FA = (
    "⚠️ این محتوا فقط آموزشیه و مشاوره‌ی مالی نیست. "
    "معامله‌ی طلا/فارکس ریسک بالایی داره و ممکنه برای همه مناسب نباشه. "
    "عملکرد گذشته تضمینی برای نتایج آینده نیست."
)

# Persian equivalents of STORY_SETS -- same 8 topics, same order, faithful
# translation (not word-for-word) so each day's 5 Persian stories form one
# connected thread too, not disconnected one-liners.
STORY_SETS_FA = [
    {
        "topic": "اول ریسک",
        "lines": [
            "قبل از ورود، خروجت رو بدون.",
            "۱٪ ریسک کن، نه کل هفته‌ت رو.",
            "حد ضررت اختیاری نیست.",
            "اول سرمایه‌ت رو حفظ کن، بعد رشدش بده.",
            "یک سود کوچیک، از یک ضرر بزرگ بهتره.",
        ],
    },
    {
        "topic": "بعد از یک ضرر",
        "lines": [
            "تازه ضرر کردی. سریع برنگرد تو معامله.",
            "چارت رو ببند. نفس بکش. ریست کن.",
            "یک ضرر فقط یک داده‌ست، نه یک حکم.",
            "معامله رو بررسی کن، خودت رو سرزنش نکن.",
            "فقط وقتی ذهنت آرومه، برگرد.",
        ],
    },
    {
        "topic": "چرا خودکارش کردیم",
        "lines": [
            "هر سیگنالی که پست می‌کنیم، رباتمون اجراش می‌کنه.",
            "بدون کلیک دستی. بدون تردید.",
            "روی MT5، روی کامپیوترت اجرا می‌شه -- نه گوشیت.",
            "با هر بروکر و هر پراپ‌فرمی کار می‌کنه.",
            "لایسنس ۶ ماهه یا ۱ ساله. لینک تو بایو.",
        ],
    },
    {
        "topic": "صبر جواب می‌ده",
        "lines": [
            "طلا به صبر بیشتر از سرعت پاداش می‌ده.",
            "گاهی بهترین معامله، معامله نکردنه.",
            "یک ستاپ خوب، از ده تا معامله‌ی تصادفی بهتره.",
            "حوصله سر رفتن دلیل ورود نیست.",
            "نظم از هر جایی جواب می‌ده -- پشت میز یا لب ساحل.",
        ],
    },
    {
        "topic": "چارت رو بخون",
        "lines": [
            "پرایس اکشن تنها حقیقته.",
            "حمایت و مقاومت، ناحیه‌ن نه خط‌های دقیق.",
            "چارت ساکت به معنی چارت مرده نیست.",
            "نوسان دور و بر خبرهای مهم بالا می‌ره -- حجمت رو کم کن.",
            "چارت از قبل بهت گفته بود. گوش دادی؟",
        ],
    },
    {
        "topic": "احساسات هزینه داره",
        "lines": [
            "ترس، سود رو زود می‌بنده.",
            "طمع، ضرر رو طولانی نگه می‌داره.",
            "احساسات، هزینه‌ی واقعیِ اسپردن.",
            "بدون احساس. فقط منطق و دقت.",
            "برای همینه که رباتمون معامله می‌گیره، نه ما.",
        ],
    },
    {
        "topic": "سطح‌ها رو بشناس",
        "lines": [
            "اعداد رند مثل ۲۰۰۰ دلار مثل آهن‌ربان.",
            "DXY بالا، طلا پایین. معمولاً.",
            "روزهای CPI و NFP طلا رو شدید حرکت می‌دن.",
            "بازده واقعی و طلا به‌ندرت تنها حرکت می‌کنن.",
            "قبل از نقطه‌ی ورود، تقویم رو بشناس.",
        ],
    },
    {
        "topic": "ورود دقیق، خروج دقیق",
        "lines": [
            "هر ورود، هر خروج -- محاسبه‌شده، نه حدسی.",
            "بدون ترس، بدون طمع -- فقط منطق.",
            "سطح‌های از پیش محاسبه‌شده. بدون کلیک دستی.",
            "سیگنال میاد. معامله میره. هر بار همون فرآیند.",
            "این چیزیه که خودکارسازی بهت می‌ده. لینک تو بایو.",
        ],
    },
    {
        "topic": "فکت‌های ترید",
        "lines": [
            "هر روز ۹.۵ تریلیون دلار توی بازار فارکس جابه‌جا می‌شه.",
            "با این‌حال ۷۴ تا ۸۹ درصد معامله‌گرهای خرد ضرر می‌کنن.",
            "بعد از ۵ سال، فقط ۵ تا ۷ درصد معامله‌گرها هنوز سودده‌ن.",
            "وقتی نصف حساب از دست بره، معمولاً ظرف ۹۰ روز بقیه‌ش هم می‌ره.",
            "ژانویه ۲۰۲۶: طلا برای اولین‌بار در تاریخ از ۵٬۶۰۰ دلار رد شد.",
        ],
    },
    # Persian equivalents of the 10 new trading-principles sets above --
    # same order/meaning, faithful translation not word-for-word.
    {
        "topic": "نسبت ریسک به ریوارد",
        "lines": [
            "نرخ برد اون‌قدری که فکر می‌کنی مهم نیست.",
            "با ۴۰٪ برد هم می‌شه سودده بود.",
            "چیزی که مهمه، نسبت ریسک به ریورده.",
            "هر بار ۱ دلار ریسک کن برای ۲ دلار یا بیشتر سود.",
            "قبل از معامله حساب کن، نه بعدش.",
        ],
    },
    {
        "topic": "اندازه‌ی پوزیشن",
        "lines": [
            "حجم معامله حس نیست، محاسبه‌ست.",
            "درصد ثابتی از حساب رو ریسک کن، نه یک حجم ثابت.",
            "یک حساب ۱۰هزار دلاری با یک حساب ۱هزار دلاری حجم یکسان نمی‌خوان.",
            "فاصله‌ی حد ضررت، حجم معامله‌ت رو تعیین می‌کنه.",
            "ریسک یکسان توی هر معامله -- همینه هدف.",
        ],
    },
    {
        "topic": "تحلیل چند تایم‌فریم",
        "lines": [
            "چارت روزانه داستان رو نشون می‌ده. چارت ساعتی جمله رو.",
            "همراه با روند تایم‌فریم بالا معامله کن.",
            "تایم‌فریم پایین رو فقط برای ورودت استفاده کن.",
            "مقابل روند بزرگ‌تر رفتن، مثل مقابل جزر و مده.",
            "اول دور شو، بعد نزدیک.",
        ],
    },
    {
        "topic": "ترید به‌عنوان کسب‌وکار",
        "lines": [
            "یک کسب‌وکار برنامه داره. تریدینگ تو هم باید داشته باشه.",
            "آمارت رو مثل یک کسب‌وکار دنبال کن.",
            "اول قانون، بعد غریزه.",
            "هیچ کسب‌وکاری بدون مدیریت ضرر دوام نمیاره.",
            "باهاش مثل یک کسب‌وکار رفتار کن، نه یک بلیط بخت‌آزمایی.",
        ],
    },
    {
        "topic": "مدیریت دوره‌ی ضرر",
        "lines": [
            "هر معامله‌گری دوره‌ی ضرر داره. حتی خوب‌هاش.",
            "وقتی ضررها جمع شد، حجمت رو کم کن.",
            "دوره‌ی ضرر یعنی آروم‌تر برو، نه تندتر.",
            "اول چیزی که مونده رو حفظ کن، بعد دنبال جبران باش.",
            "جبران با ریسک کمتر شروع می‌شه، نه شرط بزرگ‌تر.",
        ],
    },
    {
        "topic": "روند در مقابل رنج",
        "lines": [
            "هر استراتژی تو هر بازاری جواب نمی‌ده.",
            "روند به صبر پاداش می‌ده. رنج به دقت.",
            "استراتژی‌های breakout تو بازار رنج ضعیف عمل می‌کنن.",
            "قبل از ورود بدون تو کدومشی.",
            "چارت بهت می‌گه. اول بخونش.",
        ],
    },
    {
        "topic": "ترس از دست دادن فرصت",
        "lines": [
            "کندل حرکت کرده. چیز زیادی از دست ندادی.",
            "دنبال قیمت دواندن، ورود دیر رو به ضرر زود تبدیل می‌کنه.",
            "اگه یک حرکت رو از دست دادی، همیشه یکی دیگه هست.",
            "FOMO حد ضرر نداره.",
            "برای ستاپ خودت صبر کن، نه برای جمعیت.",
        ],
    },
    {
        "topic": "اهرم",
        "lines": [
            "اهرم مزیت نمی‌سازه، مزیتِ موجودت رو چند برابر می‌کنه.",
            "همون اهرمی که سودت رو دوبرابر می‌کنه، ضررت رو هم دوبرابر می‌کنه.",
            "اهرم بالا، حجم پایین -- وگرنه سریع جمع می‌شه.",
            "اهرم یک ابزاره، نه یک میان‌بر.",
            "بهش احترام بذار، وگرنه بهت احترام نمی‌ذاره.",
        ],
    },
    {
        "topic": "نشست‌های معاملاتی و نقدینگی",
        "lines": [
            "همه‌ی ساعت‌ها برای طلا یکسان نیستن.",
            "overlap لندن و نیویورک حجم واقعی رو میاره.",
            "سشن آسیا معمولاً فقط رنج می‌زنه.",
            "نقدینگی کم یعنی اسپرد بازتر و حرکت‌های الکی.",
            "وقتی بازار واقعاً در حال معامله‌ست معامله کن.",
        ],
    },
    {
        "topic": "بک‌تست قبل از ریسک واقعی",
        "lines": [
            "قبل از اینکه با پول واقعی بهش اعتماد کنی، ایده رو تست کن.",
            "تاریخ تکرار نمی‌شه، ولی ستاپ‌ها اغلب تکرار می‌شن.",
            "یک مزیتِ بک‌تست‌شده از یک حس دلی بهتره.",
            "اگه رو چارت‌های قدیمی جواب نده، فردا هم جواب نمی‌ده.",
            "اول رو کاغذ ثابتش کن، بعد با سرمایه.",
        ],
    },
]
