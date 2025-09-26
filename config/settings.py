import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuration settings for the CZ.AI bot."""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.admin_id = int(os.getenv("ADMIN_ID", 0))
        self.use_gemini_search = os.getenv("USE_GEMINI_SEARCH", "true").lower() == "true"
        self.rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", 30))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.context7_disabled = os.getenv("CONTEXT7_MCP_DISABLED_AT_RUNTIME", "true").lower() == "true"
        
        # Validate required environment variables
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if not self.admin_id:
            raise ValueError("ADMIN_ID environment variable is required")

# Create a global settings instance
settings = Settings()