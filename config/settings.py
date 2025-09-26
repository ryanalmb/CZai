import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings for the CZ.AI bot."""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_api_keys = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.admin_id = int(os.getenv("ADMIN_ID", 0))
        self.use_gemini_search = os.getenv("USE_GEMINI_SEARCH", "true").lower() == "true"
        self.rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", 30))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.context7_disabled = os.getenv("CONTEXT7_MCP_DISABLED_AT_RUNTIME", "true").lower() == "true"

        # Webhook (Render/Serverless)
        self.use_webhook = os.getenv("USE_WEBHOOK", "true").lower() == "true"
        self.webhook_base_url = os.getenv("WEBHOOK_BASE_URL", "")  # e.g., https://your-service.onrender.com
        self.webhook_path = os.getenv("WEBHOOK_PATH", "webhook")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")
        self.port = int(os.getenv("PORT", 8080))
        
        # Validate required environment variables
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        if not (self.gemini_api_key or self.gemini_api_keys):
            raise ValueError("GEMINI_API_KEY or GEMINI_API_KEYS environment variable is required")
        if not self.admin_id:
            raise ValueError("ADMIN_ID environment variable is required")

# Create a global settings instance
settings = Settings()