from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from slack_sdk.errors import SlackApiError
import logging
from .slack_client import SlackSingletonClient

class BaseSlackService(ABC):
    """
    Abstract base class for Slack services
    """
    def __init__(self, slack_client: SlackSingletonClient):
        self._slack_client = slack_client.get_cached_client()

    def _handle_slack_error(self, e: SlackApiError, context: str):
        """
        Centralized error handling for Slack errors
        """
        logging.error(f"{context}: {str(e)}")
        raise