from .base import SlackBaseTool
from typing import Dict
from slack_sdk.errors import SlackApiError
from pydantic import BaseModel, Field
import logging

class SlackGetUsers(SlackBaseTool):
    """
    Class to get the users from the slack workspace
    """
    users_cache: Dict[str, dict] = Field(default_factory=dict, exclude=True)
    name: str = "get_users"
    description: str = "Tool that gets information about Slack users in the workspace"
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SlackGetUsers, cls).__new__(cls)
            cls.instance.fetch_all_users()
        return cls.instance
    
    @classmethod
    def fetch_all_users(cls) -> None:
        """Get and cache all the users from the workspace"""
        try:
            response = cls.client.users_list()
            for user in response["members"]:
                cls.users_cache[user["id"]] = {
                    "full_name": user.get("real_name", ""),
                    "display_name": user.get("profile", {}).get("display_name", "")
                }
        except SlackApiError as e:
            print(f"Error getting users information: {e}")

    def get_user_info(self, user_id: str) -> dict:
        """Get the information of a specific user"""
        return self.users_cache.get(user_id, {
            "full_name": "Unknown User",
            "display_name": "unknown"
        })
   
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

    def _enrich_single_message(self, message: dict) -> dict:
        """Enrich a single message with user information"""
        if "user" in message:
            user_info = self.get_user_info(message["user"])
            message["user_full_name"] = user_info["full_name"]
            message["user_display_name"] = user_info["display_name"]
        return message

    def _run(self):
        pass