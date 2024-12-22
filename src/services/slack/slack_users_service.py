from typing import Dict
from slack_sdk.errors import SlackApiError
from pydantic import Field
import logging
from .base_slack_service import BaseSlackService
from .slack_client import SlackSingletonClient

class SlackUsersService(BaseSlackService):
    """Service for managing users from a Slack workspace"""
    
    users_cache: Dict[str, dict] = Field(default_factory=dict, exclude=True)
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SlackUsersService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '__initialized') and self.__initialized:
            return
        super().__init__()
        self.users_cache = {}
        self.fetch_all_users()
        self.__initialized = True
    
    def fetch_all_users(self) -> None:
        """Get and save in memory all the users from the workspace"""
        try:
            response = self._slack_client.users_list()
            for user in response["members"]:
                self.users_cache[user["id"]] = {
                    "full_name": user.get("real_name", ""),
                    "display_name": user.get("profile", {}).get("display_name", "")
                }
        except SlackApiError as e:
            self._handle_slack_error(e, "Error getting users information")
    
    def get_user_info(self, user_id: str) -> dict:
        """Get the information of a specific user"""
        return self.users_cache.get(user_id, {
            "full_name": "Unknown User",
            "display_name": "unknown"
        })

    def _enrich_single_message(self, message: dict) -> dict:
        """Enrich a single message with user information"""
        if "user" in message:
            user_info = self.get_user_info(message["user"])
            message["user_full_name"] = user_info["full_name"]
            message["user_display_name"] = user_info["display_name"]
        return message   
    def enrich_messages(self, channel_data: dict) -> dict:
        """Enrich all the messages with user information"""
        messages = channel_data.get("messages", [])
        enriched_messages = []
        
        for message in messages:
            enriched_message = self._enrich_single_message(message)
            enriched_messages.append(enriched_message)
            
            # Enrich messages in threads if they exist
            if "thread_messages" in message:
                thread_messages = message["thread_messages"]
                enriched_thread_messages = [
                    self._enrich_single_message(thread_msg) 
                    for thread_msg in thread_messages
                ]
                enriched_message["thread_messages"] = enriched_thread_messages
                
        channel_data["messages"] = enriched_messages
        return channel_data
