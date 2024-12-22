from slack_sdk.errors import SlackApiError
from .base_slack_service import SlackBaseClient
from core.settings import settings
from typing import Dict, Any
import logging
import json


class SlackChannelsService(SlackBaseClient):
    """Service for manage channels from a Slack workspace"""
    
    #Antes llamado send_notification, cambiar a send_channel_message
    def send_channel_message(self, message: str, **kwargs: Dict[str, Any]) -> bool:
        """
        Send a message to a specific channel
        """
        channel = kwargs.get('channel', '#daily-bot')
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message
            )
            
            logging.info(f"################## Slack Notification was sent to channel: {channel}")
            
            return True
        except SlackApiError as e:
            logging.error(f"Error sending message to Slack: {str(e)}")
            return False

    def get_channels_info(self, **kwargs: Dict[str, Any]) -> Dict:
        """
        Get channels information
        Returns: List of channel dictionaries with id, name, created, and num_members
        """
        try:
            result = self.client.conversations_list()
            channels = result["channels"]
            filtered_result = [
                {key: channel[key] for key in ("id", "name", "created", "num_members")}
                for channel in channels
                if "id" in channel
                and "name" in channel
                and "created" in channel
                and "num_members" in channel
            ]
            return json.dumps(filtered_result, ensure_ascii=False)

        except Exception as e:
            return "Error creating conversation: {}".format(e)
    
    def get_channel_messages(self, channel_id: str, **kwargs: Dict[str, Any]) -> Dict:
        """
        Get messages from a specific channel
        Args: channel_id: The ID of the channel to fetch messages from
        Returns: List of message dictionaries
        """
        try:
            result = self.client.conversations_history(channel=channel_id)
            messages = result["messages"]
            filtered_messages = [
                {key: message[key] for key in ("user", "text", "ts")}
                for message in messages
                if "user" in message and "text" in message and "ts" in message
            ]
            return json.dumps(filtered_messages, ensure_ascii=False)
        except Exception as e:
            return "Error creating conversation: {}".format(e)