from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from slack_sdk.errors import SlackApiError
import logging
from .slack_client import SlackSingletonClient
import traceback

class BaseSlackService(ABC):
    """
    Abstract base class for Slack services
    """
    _slack_client_instance = SlackSingletonClient()
    _slack_client : SlackSingletonClient = _slack_client_instance.get_cached_client()

    def _handle_slack_error(self, e: SlackApiError, context: str):
        """
        Centralized error handling for Slack errors
        Args:
            e: SlackApiError
            context: str
        """
        logging.error(f"{context}: {str(e)}")
        logging.error(traceback.format_exc())
        raise