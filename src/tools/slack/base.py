"""Base class for Slack tools."""

from langchain_core.tools import BaseTool
from slack_sdk import WebClient
from core.settings import settings

class SlackBaseTool(BaseTool):
    """Base class for Slack tools."""
    client: WebClient = WebClient(token=settings.slack_user_token)
    """The WebClient object."""
