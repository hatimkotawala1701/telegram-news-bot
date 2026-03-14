# Telegram News Bot

A Python-based Telegram bot that fetches the latest news headlines based on your preferred category. Pulls from two sources — Google News RSS and NewsAPI — and delivers results on demand.

---

## Features

- Set a preferred news category (technology, sports, business, etc.)
- Fetch live headlines on demand with a single command
- Results from two independent sources for broader coverage
- Per-user preference storage

---

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and instructions |
| `/setcategory` | Choose your preferred news category |
| `/news` | Fetch latest headlines for your category |
| `/help` | List all available commands |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/telegram-news-bot.git
cd telegram-news-bot
```

### 2. Install dependencies

```bash
pip install python-telegram-bot requests feedparser
```

### 3. Add your credentials

Open `news_bot.py` and replace the placeholders at the top:

```python
BOT_TOKEN = "your-telegram-bot-token"
NEWSAPI_KEY = "your-newsapi-key"
```

### 4. Run the bot

```bash
python news_bot.py
```

---

## Getting Credentials

**Telegram Bot Token**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the token provided

**NewsAPI Key**
1. Go to [https://newsapi.org](https://newsapi.org)
2. Register for a free account
3. Copy your API key from the dashboard

---

## Available Categories

`technology` · `sports` · `business` · `entertainment` · `health` · `science` · `general`

---

## Screenshot

*Add screenshot here after running the bot*

---

## Tech Stack

- Python 3.x
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [NewsAPI](https://newsapi.org)
- Google News RSS
