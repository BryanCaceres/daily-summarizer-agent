from promts import DailyJobSummarizerPromt
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import gmail_toolkit, tavily_search_tool
import logging

agent_promt_template = DailyJobSummarizerPromt()

class DailyJobSummarizerAgent(AIAgentInterface):
    def __init__(self):
        self._set_agent_config(run_name="summarizer_agent")
        self.agent_promt = agent_promt_template.get_promt()
        self.tools = [*gmail_toolkit]

    def execute_agent(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the summarizer agent
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
            max_iterations=5,
            early_stopping_method="force",
            handle_parsing_errors=True,
            handle_tool_errors=True
        )
        
        logging.info(f"Executing summarizerrrrr for date: {day} (prev: {previous_day}, next: {next_day})")

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
