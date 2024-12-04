import os
import json
from functools import lru_cache

class Settings:
    default_language : str = "Spanish"
    default_max_tokens = os.getenv("DEFAULT_MAX_TOKENS")
    default_open_ai_model = os.getenv("DEFAULT_OPEN_AI_MODEL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    default_temperature = os.getenv("DEFAULT_TEMPERATURE")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    google_delegated_user = os.getenv("GOOGLE_DELEGATED_USER")
    
@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
        

