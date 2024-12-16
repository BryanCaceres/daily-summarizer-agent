from prompts import DailyGmailSummarizerPrompt
from typing import List
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import gmail_toolkit
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
agent_prompt_template = DailyGmailSummarizerPrompt()
from .dummy_agent_responses.gmail_extractor import DUMMY_RESPONSE
from langsmith import traceable


class GmailSummarizerAgent(AIAgentInterface):
    """
    Agent to summarize daily gmail information
    """
    agent_prompt : str = agent_prompt_template.get_prompt()
    tools : List = [*gmail_toolkit]
    run_name: str = "gmail_summarizer_agent"

    def __init__(self, dummy_mode: bool = False, dummy_response: dict = DUMMY_RESPONSE):
        self._set_agent_config(run_name=self.run_name)
        self.dummy_mode = dummy_mode
        self.dummy_response = dummy_response

    @traceable
    def execute_agent(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the gmail_summarizer agent
        :param day: YYYY-MM-DD str with the day to summarize
        :return: dict with the summary result
        """
        if self.dummy_mode:
            return self.dummy_response
        
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
            max_iterations=15,
            early_stopping_method="force",
            handle_parsing_errors=True,
            handle_tool_errors=True
        )
        
        logging.info(f"Executing gmail summarizer agent for date: {day} (prev: {previous_day}, next: {next_day})")

        result = agent_executor.invoke(
            {
                "day": day,
                "previous_day": previous_day,
                "next_day": next_day,
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
