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
]

# Calls-to-action promoting the trading bot. Kept factual (no "guaranteed
# profit" / "get rich" language) to stay within Instagram's ad policy norms
# and basic advertising-honesty practice.
CTAS = [
    "Want your gold trades executed with zero emotion? My trading bot is live -- link in bio.",
    "I built a trading bot to automate this exact process. DM \"BOT\" to learn more.",
    "Tired of watching charts all day? My bot does it for you. Details in bio.",
    "Automate your gold strategy the way I do -- check the link in bio for my trading bot.",
    "Consistency beats emotion. That's why I trade with my own bot -- DM me for access.",
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
# of rotation, e.g. rename to your own handle/brand tag.
BRAND_HASHTAGS = ["#goldtradingbot"]
