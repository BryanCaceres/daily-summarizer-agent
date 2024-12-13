from prompts import GeneralSummarizerPrompt
from typing import List
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import tavily_search_tool


agent_prompt_template = GeneralSummarizerPrompt()

class GeneralSummarizerAgent(AIAgentInterface):
    """
    Agent to summarize daily gmail information
    """
    agent_prompt : str = agent_prompt_template.get_prompt()
    tools : List = [tavily_search_tool]

    def __init__(self, run_name: str = "general_summarizer_agent"):
        self._set_agent_config(run_name=run_name)

    def execute_agent(self, day: str, gmail_summary_json: str, slack_summary_json: str) -> dict:
        """
        Execute the gmail_summarizer agent
        :param day: YYYY-MM-DD str with the day to summarize
        :param gmail_summary_json: JSON str with the gmail summary
        :param slack_summary_json: JSON str with the slack summary
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

        result = agent_executor.invoke(
            {
                "day": day,
                "gmail_summary_json": gmail_summary_json,
                "slack_summary_json": slack_summary_json,
                "tools": formatted_tools
            }, 
            config=self.agent_config
        )
        parsed_result = self.json_parser.parse(result.get("output", "{}"))

        enriched_response = {
            "summary_result": parsed_result,
            "tool_usage": self._extract_tool_usage(result)
        }

        return enriched_response
