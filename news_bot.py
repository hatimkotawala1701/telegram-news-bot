"""
Telegram News Bot
-----------------
Commands:
  /start        - Welcome message
  /setcategory  - Set your preferred news category
  /news         - Get latest news based on your category
  /help         - Show available commands

Sources:
  - Google News RSS (no API key required)
  - NewsAPI (requires free API key from newsapi.org)

Setup:
  pip install python-telegram-bot requests feedparser
  Set BOT_TOKEN and NEWSAPI_KEY in the config section below.
"""

import feedparser
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

BOT_TOKEN = "8700051027:AAEOWrK0rLZwdnIcBehiX15ehiqjk4epI4E"
NEWSAPI_KEY = "ab823ad21f264509a90b3ed55911feae"
RESULTS_PER_SOURCE = 3        


SELECTING_CATEGORY = 1 

CATEGORIES = ["technology", "sports", "business", "entertainment", "health", "science", "general"]

GOOGLE_NEWS_TOPICS = {
    "technology":    "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "sports":        "CAAqJggKIiBDQkFTRWdvSUwyMHZNR1pwY3pNU0FtVnVHZ0pWVXlnQVAB",
    "business":      "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "entertainment": "CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYVhNU0FtVnVHZ0pWVXlnQVAB",
    "health":        "CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ",
    "science":       "CAAqJggKIiBDQkFTRWdvSUwyMHZNR1p0Y1hNU0FtVnVHZ0pWVXlnQVAB",
    "general":       "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB",
}

user_categories: dict[int, str] = {}

def fetch_google_news(category: str) -> list[dict]:
    """Fetch articles from Google News RSS for the given category."""
    topic_id = GOOGLE_NEWS_TOPICS.get(category, GOOGLE_NEWS_TOPICS["general"])
    url = f"https://news.google.com/rss/topics/{topic_id}?hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:RESULTS_PER_SOURCE]:
        articles.append({
            "title": entry.get("title", "No title"),
            "url": entry.get("link", ""),
            "source": "Google News",
        })
    return articles


def fetch_newsapi(category: str) -> list[dict]:
    """Fetch articles from NewsAPI for the given category."""
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": category if category != "general" else None,
        "language": "en",
        "pageSize": RESULTS_PER_SOURCE,
        "apiKey": NEWSAPI_KEY,
    }

    params = {k: v for k, v in params.items() if v is not None}
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        articles = []
        for item in data.get("articles", [])[:RESULTS_PER_SOURCE]:
            articles.append({
                "title": item.get("title", "No title"),
                "url": item.get("url", ""),
                "source": item.get("source", {}).get("name", "NewsAPI"),
            })
        return articles
    except Exception:
        return []


def format_articles(articles: list[dict]) -> str:
    """Format a list of article dicts into a readable message string."""
    if not articles:
        return "No articles found."
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. *{a['title']}*\n   [{a['source']}]({a['url']})")
    return "\n\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the News Bot.\n\n"
        "Use /setcategory to choose your topic.\n"
        "Use /news to get the latest headlines.\n"
        "Use /help to see all commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — Welcome message\n"
        "/setcategory — Set your preferred news category\n"
        "/news — Get latest news\n"
        "/help — Show this message"
    )


async def setcategory_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category keyboard."""
    keyboard = [[cat.capitalize() for cat in CATEGORIES[i:i+3]] for i in range(0, len(CATEGORIES), 3)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Select a category:", reply_markup=reply_markup)
    return SELECTING_CATEGORY


async def setcategory_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the selected category."""
    choice = update.message.text.strip().lower()
    if choice not in CATEGORIES:
        await update.message.reply_text(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
        return SELECTING_CATEGORY
    user_categories[update.effective_user.id] = choice
    await update.message.reply_text(f"Category set to: {choice.capitalize()}\nUse /news to get headlines.")
    return ConversationHandler.END


async def setcategory_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send news based on the user's saved category."""
    user_id = update.effective_user.id
    category = user_categories.get(user_id, "general")

    await update.message.reply_text(f"Fetching *{category.capitalize()}* news...", parse_mode="Markdown")

    google_articles = fetch_google_news(category)
    newsapi_articles = fetch_newsapi(category)

    all_articles = google_articles + newsapi_articles

    if not all_articles:
        await update.message.reply_text("Could not fetch news. Try again later.")
        return

    # Send Google News results
    if google_articles:
        await update.message.reply_text(
            f"*Google News — {category.capitalize()}*\n\n{format_articles(google_articles)}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

    # Send NewsAPI results
    if newsapi_articles:
        await update.message.reply_text(
            f"*NewsAPI — {category.capitalize()}*\n\n{format_articles(newsapi_articles)}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )



def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for /setcategory
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setcategory", setcategory_start)],
        states={
            SELECTING_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, setcategory_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", setcategory_cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
