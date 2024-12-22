from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .base import SlackBaseTool
from .utils import UTC_FORMAT
from langchain_core.callbacks import CallbackManagerForToolRun
import json
from services import SlackMessagesService
from slack_sdk.errors import SlackApiError
import logging
from agents.dummy_agent_responses.slack_extractor import DUMMY_RESPONSE

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
    
    service: SlackMessagesService = SlackMessagesService()
    args_schema: Type[GetConversationsSchema] = GetConversationsSchema

    def _run(
        self,
        day: str,
        user_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Main execution method to get all conversations for a user on a specific day.
        Args: day: The day to search for in YYYY-MM-DD format
        Args: user_id: The Slack user ID to search conversations for
        Args: run_manager: Optional callback manager
        Returns:JSON string containing all relevant conversations
        """
        try:
            conversations = self.service.get_user_conversations(user_id, day)
            return json.dumps(conversations, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Error in get_conversations: {str(e)}", exc_info=True)
            return f"Error getting conversations: {str(e)}"