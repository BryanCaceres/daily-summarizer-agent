from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from core.settings import settings
from typing import Dict, Any
import logging


class SlackNotificationService():
    """
    Notifications for Slack channels
    """
    client : WebClient = WebClient(token=settings.SLACK_USER_TOKEN)

    def send_notification(self, message: str, **kwargs: Dict[str, Any]) -> bool:
        channel = kwargs.get('channel', '#daily-bot')
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message
            )
            
            return True
        except SlackApiError as e:
            logging.error(f"Error sending message to Slack: {str(e)}")
            return False