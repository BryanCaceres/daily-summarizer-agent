from promts import DailyJobSummarizerPromt
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import gmail_tools, slack_tools, tavily_search
import logging

agent_promt_template = DailyJobSummarizerPromt()

class DailyJobSummarizerAgent(AIAgentInterface):
    def __init__(self):
        super().__init__()
        self._set_agent_config(run_name="summarizer_agent")
        self.agent_promt = agent_promt_template.get_promt()
        self.tools = [gmail_tools, slack_tools, tavily_search]

    def execute_agent(self, comment_body: str, moderation_name: str, moderation_reason: str, infraction_evidence: str) -> dict:
        """
        Execute the hatespeech expert agent
        :param comment_body: str with the comment body
        :param moderation_name: str with the moderation name
        :param moderation_reason: str with the moderation reason
        :param infraction_evidence: str with the infraction evidence
        :return: dict with the moderation result
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
            max_iterations=20,
            early_stopping_method="force"
        )

        result = agent_executor.invoke(
            {
                "comment_body": comment_body,
                "moderation_name": moderation_name, 
                "moderation_reason": moderation_reason, 
                "infraction_evidence": infraction_evidence, 
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
