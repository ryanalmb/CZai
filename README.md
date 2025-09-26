# CZ.AI Telegram Bot

CZ.AI is a fan-made parody Telegram bot that provides cryptocurrency market insights in the style of CZ (Changpeng Zhao). The bot uses Google's Gemini AI with web search capabilities to provide up-to-date information.

## ⚠️ Disclaimer

CZ.AI is a fan-made parody. Not affiliated with CZ or Binance.
⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀

## Features

- **AI-Powered Responses**: Uses Gemini AI to generate CZ-style responses
- **Web Search Integration**: Automatically searches the web for current information when needed
- **Rate Limiting**: Prevents spam with per-user cooldowns
- **Admin Commands**: Admin-only announcement feature
- **Real-time Information**: Queries about news, prices, and market updates

## ⚠️ Model Name Note

The default configuration uses `gemini-1.5-flash` as the primary model. You can also use `gemini-1.5-pro`. Verify model availability with the official Google AI documentation as availability may change.
- **Web Search Integration**: Automatically searches the web for current information when needed
- **Rate Limiting**: Prevents spam with per-user cooldowns
- **Admin Commands**: Admin-only announcement feature
- **Real-time Information**: Queries about news, prices, and market updates

## Requirements

- Python 3.8+
- Telegram Bot Token
- Gemini API Key

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd czai-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
TELEGRAM_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash  # Suggested: gemini-1.5-flash or gemini-1.5-pro
USE_GEMINI_SEARCH=true  # Set to false to disable google_search tool usage
ADMIN_ID=your_telegram_user_id_here  # Telegram user ID for admin commands
RATE_LIMIT_SECONDS=30  # Per-user cooldown for /CZ command in seconds
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
CONTEXT7_MCP_DISABLED_AT_RUNTIME=true
```

### 4. Run the Bot (Local)

```bash
python run_bot.py
```

### Deploy to Render (Free Web Service)

1) Fork this repo and connect it to Render: https://render.com
2) Create a new Web Service, select your repo and branch.
3) Environment
   - Runtime: Docker (uses provided Dockerfile)
   - Start command: python run_bot.py
   - Environment Variables: TELEGRAM_TOKEN, GEMINI_API_KEY, ADMIN_ID, USE_WEBHOOK=true, WEBHOOK_BASE_URL=https://<your-service>.onrender.com, GEMINI_MODEL=gemini-1.5-flash
4) After first deploy, Render gives you the service URL; ensure WEBHOOK_BASE_URL matches it.
5) Redeploy if you update env vars.

Notes:
- The bot runs in webhook mode on path /webhook. Telegram will POST updates to WEBHOOK_BASE_URL/webhook.
- Optionally set WEBHOOK_SECRET for extra verification.
- Render may sleep on inactivity; Telegram retries deliveries so it usually still works.


## Docker Deployment (Local)

To run with Docker:

```bash
# Build the image
docker build -t czai-bot .

# Run the container
docker run -d --env-file .env czai-bot
```

## Commands

- `/start` - Start the bot and get welcome message
- `/CZ <question>` - Ask CZ-style questions about crypto markets (bilingual, optimistic)
- `/announce <message>` - Admin-only command to send announcements (requires ADMIN_ID)

## Example Usage

- `/CZ Should I move all to BNB?` → Get authoritative advice with BNB ecosystem insights
- `/CZ What's new with Binance regulation today?` → Get latest news with web search results
- `/CZ How to manage risk?` → Get risk management principles

## Architecture

- Webhook mode ready for serverless (Render). The bot sets its Telegram webhook to WEBHOOK_BASE_URL/WEBHOOK_PATH and listens on PORT.


- `bot.py` - Main entry point
- `config/settings.py` - Configuration management
- `services/ai_service.py` - Gemini AI integration with web search (google-genai SDK)
- `handlers/` - Command handlers
  - `start_handler.py` - /start command
  - `cz_handler.py` - /CZ command
  - `announce_handler.py` - /announce command
- `utils/rate_limiter.py` - Rate limiting functionality

## Grounding Behavior

The bot automatically uses Gemini's google_search tool for queries containing:
- "news", "price", "BNB news", "hack", "regulation"
- "today", "yesterday", "latest", "update", "recent"
- "announcement", "market", "change", "now", "current"

Search results are cited in the response with up to 2 URLs.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| TELEGRAM_TOKEN | Telegram Bot token | required |
| GEMINI_API_KEY | Gemini API key | required |
| GEMINI_MODEL | Gemini model to use | gemini-2.5-flash |
| USE_GEMINI_SEARCH | Enable/disable google_search tool | true |
| ADMIN_ID | Admin user ID for /announce command | required |
| RATE_LIMIT_SECONDS | Rate limit for /CZ command (seconds) | 30 |
| LOG_LEVEL | Logging level | INFO |

## Development

### Running Tests

```bash
# Coming soon - basic interaction tests
```

### Code Structure

The bot follows a modular architecture:
1. Configuration is handled in `config/settings.py`
2. AI logic is encapsulated in `services/ai_service.py`
3. Telegram handlers are in the `handlers/` directory
4. Utilities are in the `utils/` directory

## License

This project is for educational and entertainment purposes only. It is a parody and not affiliated with CZ or Binance.

⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀