from prompts import DailySlackSummarizerPrompt
from typing import List
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import slack_search_toolkit
from core.settings import settings
import logging

agent_prompt_template = DailySlackSummarizerPrompt()

class SlackSummarizerAgent(AIAgentInterface):
    """
    Agent to summarize daily gmail information
    """
    agent_prompt : str = agent_prompt_template.get_prompt()
    tools : List = [*slack_search_toolkit]

    def __init__(self):
        self._set_agent_config(run_name="slack_summarizer_agent")

    def execute_agent(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the slack summarizer agent
        :param day: YYYY-MM-DD str with the day to summarize
        :return: dict with the summary result
        """
        formatted_tools = self._get_agent_tools_string()

        summarizer_agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt
        )

        agent_executor = AgentExecutor(
            agent=summarizer_agent, 
            tools=self.tools, 
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5,
            early_stopping_method="force",
            handle_parsing_errors=True,
            handle_tool_errors=True
        )
        
        logging.info(f"Executing slack summarizer agent for date: {day} (prev: {previous_day}, next: {next_day})")

        result = agent_executor.invoke(
            {
                "day": day,
                "previous_day": previous_day,
                "next_day": next_day,
                "slack_user_display_name": settings.slack_user_display_name,
                "slack_member_id": settings.slack_member_id,
                "tools": formatted_tools
            }, 
            config=self.agent_config
        )

        logging.debug(f'Result: {result}')

        parsed_result = self.json_parser.parse(result.get("output", "{}"))

        enriched_response = {
            "summary_result": parsed_result,
            "tool_usage": self._extract_tool_usage(result)
        }

        return enriched_response
