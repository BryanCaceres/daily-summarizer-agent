import json
import logging
from typing import Optional, Type
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from .base import SlackBaseTool
from services.slack.slack_channels_service import SlackChannelsService
class SlackGetMessageSchema(BaseModel):
    """Input schema for SlackGetMessages."""

    channel_id: str = Field(
        ...,
        description="The channel id, private group, or IM channel to send message to.",
    )

class SlackGetMessage(SlackBaseTool):
    """Tool that gets Slack messages."""

    name: str = "get_messages"
    description: str = "Use this tool to get messages from a channel."
    service: SlackChannelsService = SlackChannelsService()

    args_schema: Type[SlackGetMessageSchema] = SlackGetMessageSchema

    def _run(
        self,
        channel_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            channel_messages = self.service.get_channel_messages(channel_id=channel_id)
            return json.dumps(channel_messages, ensure_ascii=False)

        except Exception as e:
            logging.error(f"Error in get_message from channel {channel_id}: {str(e)}", exc_info=True)
            return "Error getting channel messages: {}".format(e)