from typing import List, Dict, Any
from slack_sdk.errors import SlackApiError
from .base_slack_service import SlackBaseClient
import logging
from datetime import datetime
import json
from .slack_users_service import SlackUsersService

class SlackMessagesService(SlackBaseClient):
    """Service for manage messages from a Slack workspace"""
    
    user_service: SlackUsersService = SlackUsersService()
    
    def _get_all_messages(self, channel_id: str, start_ts: str, end_ts: str) -> List[Dict[str, Any]]:
        """
        Retrieves all messages from a channel within a time range, handling pagination.
        Args:channel_id: The ID of the channel to fetch messages from
        Args:start_ts: Starting timestamp for message retrieval
        Args:end_ts: Ending timestamp for message retrieval  
        Returns:List of message dictionaries
        Note:Uses cursor-based pagination to handle large message sets
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

    def _get_thread_replies(self, channel_id: str, thread_ts: str, start_ts: str, end_ts: str) -> List[Dict[str, Any]]:
        """
        Retrieves all replies in a thread within a time range.
        Args:channel_id: The ID of the channel containing the thread
        Args:thread_ts: Timestamp of the parent message
        Args:start_ts: Starting timestamp for reply retrieval
        Args:end_ts: Ending timestamp for reply retrieval 
        Returns: List of reply message dictionaries
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

    def _process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process the messages to enrich them with user information"""
        enriched_messages = []
        
        for message in messages:
            # Enrich the main message
            enriched_message = message.copy()
            if "user" in message:
                user_info = self.user_service.get_user_info(message["user"])
                enriched_message["user_full_name"] = user_info["full_name"]
                enriched_message["user_display_name"] = user_info["display_name"]
            
            # Enrich thread messages if they exist
            if "thread_messages" in message:
                enriched_thread_messages = []
                for thread_message in message["thread_messages"]:
                    enriched_thread_message = thread_message.copy()
                    if "user" in thread_message:
                        user_info = self.user_service.get_user_info(thread_message["user"])
                        enriched_thread_message["user_full_name"] = user_info["full_name"]
                        enriched_thread_message["user_display_name"] = user_info["display_name"]
                    enriched_thread_messages.append(enriched_thread_message)
                enriched_message["thread_messages"] = enriched_thread_messages
                
            enriched_messages.append(enriched_message)
        
        return enriched_messages
    
    def get_user_conversations(self, user_id: str, day: str, **kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Method to get all conversations for a user on a specific day.
        
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

            channels_response = self.client.users_conversations(
                user=user_id,
                types="public_channel,private_channel,mpim,im",
                exclude_archived=True,
                limit=500
            )
            
            if not channels_response["ok"]:
                raise SlackApiError("Error getting channels", channels_response)
            
            logging.info(f"################## All Slack Channels in workspace: {channels_response}")
            
            conversations = []
            for channel in channels_response["channels"]:
                
                if channel["name"]:
                    logging.info(f"################## Searching Slack Messages in channel: {channel['name']}##################")
                # Get messages for a channel in the specific day
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
                    # Process the messages before adding them to the conversations
                    enriched_messages = self._process_messages(relevant_messages)
                    conversations.append({
                        "channel_id": channel["id"],
                        "channel_name": channel.get("name", "direct-message"),
                        "messages": enriched_messages
                    })
            

            return json.dumps(conversations, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Error in get_conversations: {str(e)}", exc_info=True)
            return f"Error getting conversations: {str(e)}"