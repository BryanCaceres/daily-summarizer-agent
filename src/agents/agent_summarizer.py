from promts import DailyJobSummarizerPromt
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import gmail_tool, tavily_search_tool
import logging

agent_promt_template = DailyJobSummarizerPromt()

class DailyJobSummarizerAgent(AIAgentInterface):
    def __init__(self):
        super().__init__()
        self._set_agent_config(run_name="summarizer_agent")
        self.agent_promt = agent_promt_template.get_promt()
        self.tools = [gmail_tool]

    def execute_agent(self, day: str) -> dict:
        """
        Execute the summarizer agent
        :param day: YYYY-MM-DD str with the day to summarize
        :return: dict with the summary result
        """

        formatted_tools = """
        TavilySearch: To search the web.
        GmailCreateDraft: To create a draft email.
        GmailSendMessage: To send a message.
        GmailSearch: To search emails.
        GmailGetMessage: To get a single message.
        GmailGetThread: To get a thread.
        """

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
                "day": day,
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
