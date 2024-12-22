from functools import lru_cache
from slack_sdk import WebClient
from core.settings import settings

class SlackSingletonClient:
    """
    Singleton for Slack client
    Benefits:
    - Guarantees a single instance of the client
    - Method cache for memory optimization
    - Thread-safe
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = WebClient(token=settings.SLACK_USER_TOKEN)
        return cls._instance

    @property
    def client(self):
        return self._client

    @lru_cache(maxsize=1)
    def get_cached_client(self):
        """Method with cache to get client"""
        return self.client
