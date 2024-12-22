from typing import Optional, Type
import logging
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from .base import SlackBaseTool
from services.slack.slack_channels_service import SlackChannelsService
class SendMessageSchema(BaseModel):
    """Input for SendMessageTool."""

    message: str = Field(
        ...,
        description="The message to be sent.",
    )
    channel: str = Field(
        ...,
        description="The channel, private group, or IM channel to send message to.",
    )


class SlackSendMessage(SlackBaseTool):
    """Tool for sending a message in Slack."""

    name: str = "send_message"
    description: str = (
        "Use this tool to send a message with the provided message fields. Its important send the messages just once, do not repeat the sending of a same message."
    )
    service: SlackChannelsService = SlackChannelsService()
    args_schema: Type[SendMessageSchema] = SendMessageSchema

    def _run(
        self,
        message: str,
        channel: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            message_was_sent = self.service.send_channel_message(message=message)
            if message_was_sent:
                return {"message_was_sent": True, "info": "The message was sent successfully", "message_text": message, "channel": channel}
            else:
                raise Exception("The message was not sent")

        except Exception as e:
            logging.error(f"Error in send_message: {str(e)}", exc_info=True)
            return "Error sending message: {}".format(e)
