from prompts import TagExtractorPrompt
from typing import List
from .agent_interface import AIAgentInterface
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import get_tags_tool, create_tags_tool
from langsmith import traceable


agent_prompt_template = TagExtractorPrompt()

class TagExtractorAgent(AIAgentInterface):
    """
    Agent to summarize daily gmail information
    """
    agent_prompt : str = agent_prompt_template.get_prompt()
    tools : List = [get_tags_tool, create_tags_tool]
    run_name: str = "tag_extractor_agent"

    def __init__(self):
        self._set_agent_config(run_name=self.run_name)

    @traceable
    def execute_agent(self, summary: str) -> dict:
        """
        Execute the tag_extractor agent
        :param summary: str with the summary
        :return: dict with the tags
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
            max_iterations=10,
            early_stopping_method="force",
            handle_parsing_errors=True,
            handle_tool_errors=True
        )

        result = agent_executor.invoke(
            {
                "daily_summary": summary,
                "tools": formatted_tools
            },
            config=self.agent_config
        )
        parsed_result = self.json_parser.parse(result.get("output", "{}"))

        enriched_response = {
            "tags_result": parsed_result,
            "tool_usage": self._extract_tool_usage(result)
        }

        create_tags_tool.reset_usage_count()

        return enriched_response

