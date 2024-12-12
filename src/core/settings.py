import os
import json
from functools import lru_cache
import logging
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # General configuration
    DEFAULT_LANGUAGE: str = "Spanish"

    # OpenAI configuration
    DEFAULT_MAX_TOKENS = os.getenv("DEFAULT_MAX_TOKENS")
    DEFAULT_OPEN_AI_MODEL = os.getenv("DEFAULT_OPEN_AI_MODEL")
    DEFAULT_TEMPERATURE = os.getenv("DEFAULT_TEMPERATURE")
    DEFAULT_OPENAI_EMBEDDING_MODEL = os.getenv("DEFAULT_OPENAI_EMBEDDING_MODEL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # External APIs configuration
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    BASE_PINECONE_INDEX_NAME = os.getenv("BASE_PINECONE_INDEX_NAME")

    # Authentication configuration
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
    GOOGLE_DELEGATED_USER = os.getenv("GOOGLE_DELEGATED_USER")
    SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
    SLACK_USER_DISPLAY_NAME = os.getenv("SLACK_USER_DISPLAY_NAME")
    SLACK_MEMBER_ID = os.getenv("SLACK_MEMBER_ID")

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL")

    # DynamoDB configuration
    DYNAMODB_REGION_NAME = os.getenv("DYNAMODB_REGION_NAME")
    TAGS_TABLE = os.getenv("TAGS_TABLE")

    def __init__(self):
        logging.basicConfig(level=self.LOG_LEVEL)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
        

