from promts import DailyGmailSummarizerPromt
from typing import List
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import gmail_toolkit
import logging

agent_promt_template = DailyGmailSummarizerPromt()

class GmailSummarizerAgent(AIAgentInterface):
    """
    Agent to summarize daily gmail information
    """
    agent_promt : str = agent_promt_template.get_prompt()
    tools : List = [*gmail_toolkit]

    def __init__(self):
        self._set_agent_config(run_name="gmail_summarizer_agent")

    def execute_agent(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the gmail_summarizer agent
        :param day: YYYY-MM-DD str with the day to summarize
        :return: dict with the summary result
        """
        formatted_tools = self._get_agent_tools_string()

        summarizer_agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_promt
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
