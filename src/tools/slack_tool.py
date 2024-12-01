from langchain_community.agent_toolkits import SlackToolkit
import os

class SlackTool:
    def __init__(self):
        if not os.getenv("SLACK_USER_TOKEN"):
            ValueError("SLACK_USER_TOKEN is not set in the environment variables")
        self.set_tool()

    def set_tool(self):
        toolkit = SlackToolkit()
        self.tool = toolkit.get_tools()

slack_tools = SlackTool().tool

    
