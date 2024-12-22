"""Base class for Slack tools."""

from langchain_core.tools import BaseTool
from src.services.slack.base_slack_service import BaseSlackService

class SlackBaseTool(BaseTool, BaseSlackService):
    """Base class for Slack tools."""
