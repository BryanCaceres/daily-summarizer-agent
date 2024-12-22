import json
import logging
from typing import Any, Optional
from pydantic import BaseModel, Field
from services.slack.slack_channels_service import SlackChannelsService
from langchain_core.callbacks import CallbackManagerForToolRun
from .base import SlackBaseTool

class SlackGetChannel(SlackBaseTool):
    """Tool that gets Slack channels information where the user is a member."""

    name: str = "get_channelid_name_dict"
    description: str = (
        "Use this tool to get channelid-name dict. There is no input to this tool"
    )
    service: SlackChannelsService = SlackChannelsService()

    def _run(
        self, *args: Any, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            channels_info = self.service.get_channels_info()

            return json.dumps(channels_info, ensure_ascii=False)

        except Exception as e:
            logging.error(f"Error in get_channel: {str(e)}", exc_info=True)
            return "Error getting channels information: {}".format(e)
