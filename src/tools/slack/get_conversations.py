from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .base import SlackBaseTool
from .utils import UTC_FORMAT
from langchain_core.callbacks import CallbackManagerForToolRun
import json
from slack_sdk.errors import SlackApiError
import logging

class GetConversationsSchema(BaseModel):
    """Input schema for GetConversationsSchema."""
    
    day: str = Field(
        ...,
        description="The day to search for conversations in format YYYY-MM-DD",
    )
    user_id: str = Field(
        ...,
        description="The user ID to search conversations for",
    )

class SlackGetConversations(SlackBaseTool):
    """Tool for getting conversations where user participated in a specific day."""

    name: str = "get_conversations"
    description: str = (
        "Use this tool to get all conversations where the user participated "
        "in a specific day, including context and thread replies."
    )
    args_schema: Type[GetConversationsSchema] = GetConversationsSchema

    def _get_all_messages(self, channel_id: str, start_ts: str, end_ts: str) -> List[Dict[str, Any]]:
        """
        Retrieves all messages from a channel within a time range, handling pagination.
        
        Args:
            channel_id: The ID of the channel to fetch messages from
            start_ts: Starting timestamp for message retrieval
            end_ts: Ending timestamp for message retrieval
            
        Returns:
            List of message dictionaries
            
        Note:
            Uses cursor-based pagination to handle large message sets
        """
        all_messages: List[Dict[str, Any]] = []
        cursor = None
        
        while True:
            try:
                response = self.client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    limit=500,  # Slack's recommended limit
                    oldest=start_ts,
                    latest=end_ts,
                    inclusive=True
                )
                
                if not response["ok"]:
                    logging.error(f"Error in API response: {response.get('error', 'Unknown error')}")
                    break
                
                all_messages.extend(response["messages"])
                
                # Check for more messages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                    
            except SlackApiError as e:
                logging.error(f"Error getting messages: {e.response['error']}")
                break
                
        return all_messages

    def _get_thread_replies(
        self, 
        channel_id: str, 
        thread_ts: str, 
        start_ts: str, 
        end_ts: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all replies in a thread within a time range.
        
        Args:
            channel_id: The ID of the channel containing the thread
            thread_ts: Timestamp of the parent message
            start_ts: Starting timestamp for reply retrieval
            end_ts: Ending timestamp for reply retrieval
            
        Returns:
            List of reply message dictionaries
        """
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                oldest=start_ts,
                latest=end_ts,
                limit=500,
                inclusive=True
            )
            
            if not response["ok"]:
                logging.error(f"Error in API response: {response.get('error', 'Unknown error')}")
                return []
                
            return response.get("messages", [])
            
        except SlackApiError as e:
            logging.error(f"Error getting thread replies: {e.response['error']}")
            return []

    def _run(
        self,
        day: str,
        user_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Main execution method to get all conversations for a user on a specific day.
        
        Args:
            day: The day to search for in YYYY-MM-DD format
            user_id: The Slack user ID to search conversations for
            run_manager: Optional callback manager
            
        Returns:
            JSON string containing all relevant conversations
        """
        try:
            date_obj = datetime.strptime(day, "%Y-%m-%d")
            start_ts = datetime(
                date_obj.year, date_obj.month, date_obj.day
            ).timestamp()
            end_ts = datetime(
                date_obj.year, date_obj.month, date_obj.day, 23, 59, 59
            ).timestamp()

            # Get channels where user is a member
            channels_response = self.client.users_conversations(
                user=user_id,
                types="public_channel,private_channel,mpim,im",
                exclude_archived=True,
                limit=500
            )
            
            if not channels_response["ok"]:
                raise SlackApiError("Error getting channels", channels_response)
            
            conversations = []
            
            for channel in channels_response["channels"]:
                # Get messages for the specific day
                channel_messages = self._get_all_messages(
                    channel["id"], 
                    str(start_ts), 
                    str(end_ts)
                )
                
                relevant_messages = []
                
                for message in channel_messages:
                    # Check if user participated in the message
                    if (message.get("user") == user_id or 
                        f"<@{user_id}>" in message.get("text", "")):
                        
                        message_data = {
                            "text": message.get("text", ""),
                            "user": message.get("user", ""),
                            "timestamp": message.get("ts", ""),
                            "thread_ts": message.get("thread_ts", ""),
                        }
                        
                        # Get thread context if applicable
                        if "thread_ts" in message:
                            thread_messages = self._get_thread_replies(
                                channel["id"],
                                message["thread_ts"],
                                str(start_ts),
                                str(end_ts)
                            )
                            message_data["thread_messages"] = thread_messages
                            
                        relevant_messages.append(message_data)
                
                if relevant_messages:
                    conversations.append({
                        "channel_id": channel["id"],
                        "channel_name": channel.get("name", "direct-message"),
                        "messages": relevant_messages
                    })
            
            return json.dumps(conversations, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Error in get_conversations: {str(e)}", exc_info=True)
            return f"Error getting conversations: {str(e)}"