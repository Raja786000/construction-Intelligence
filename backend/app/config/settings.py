import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "construction_intelligence")

    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # "google" or "openai"
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")

    # Dynamic Fallback: if no LLM key is configured, run in Mock LLM consolidation mode
    @property
    def USE_MOCK_LLM(self) -> bool:
        if self.LLM_PROVIDER == "google" and not self.GOOGLE_API_KEY:
            return True
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            return True
        return False

settings = Settings()
