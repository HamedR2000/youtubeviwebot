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

# Short single lines for Story cards -- Stories are read in ~2 seconds, so
# these are intentionally punchier and shorter than HOOKS/TIPS. Mix of
# facts, quotes, and soft CTAs pointing at the bot.
STORY_LINES = [
    "Gold just moved. Do you know why?",
    "Discipline > Prediction.",
    "Your stop-loss is not optional.",
    "DXY up, gold down. Usually.",
    "The trend is your friend -- until it bends.",
    "Automate the boring part. Telegram in bio.",
    "One good setup beats ten random trades.",
    "Risk 1%, not your whole week.",
    "Emotions are the real spread cost.",
    "My bot trades gold while I sleep. Telegram in bio.",
    "Signal in. Trade out. Zero manual clicks.",
    "One bot. Any broker. Any prop firm.",
    "You set the lot size. The bot handles the rest.",
    "A ready XAUUSD preset, pre-optimized and tested.",
    "Runs on MT5, on your PC -- not your phone.",
    "6-month or 1-year license. Full support included.",
    "Patience is a position too.",
    "The best trade is sometimes no trade.",
    "Protect your capital first. Grow it second.",
    "A plan without discipline is just a guess.",
    "There is no easy way. Be disciplined.",
    "No risk, no story. No loss, no profit.",
    "A small profit beats a big loss.",
    "Focus. Patience. Execution.",
    "Every trade starts as risk before it becomes profit.",
    "The market doesn't just move price -- it tests your patience.",
    "Treat every setup like it's real gold in the vault.",
    "Discipline works from anywhere -- a desk or a beach.",
    "Price action is the only truth.",
]

# Once-a-week Persian story line (see PERSIAN_STORY_WEEKDAY in main.py) --
# same bot-focused content as STORY_LINES, for the audience segment that
# reads Persian. Kept short, matching the Story format.
STORY_LINES_FA = [
    "معاملات طلا دیگه دستی نیست.",
    "هر سیگنال کانال تلگرام، خودکار روی MT5 اجرا می‌شه.",
    "با هر بروکر و هر پراپ‌فرم سازگاره -- فقط حجم معامله دست شماست.",
    "یک پریست آماده و بهینه‌شده، مخصوص XAUUSD.",
    "لایسنس ۶ ماهه یا ۱ ساله، با پشتیبانی کامل.",
    "ربات معامله‌گر خودکار طلا -- برای دریافت، پیام بده.",
    "نظم بهتر از پیش‌بینیه.",
    "گاهی بهترین معامله، معامله نکردنه.",
    "اول سرمایه‌ت رو حفظ کن، بعد رشدش بده.",
    "ربات با هر بروکر و پراپ‌فرمی کار می‌کنه -- فقط حجم معامله دست شماست.",
]
