from abc import ABC, abstractmethod
from typing import List
from core.settings import settings
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig

class AIAgentInterface(ABC):
    tools: List = []
    json_parser : JsonOutputParser = JsonOutputParser()
    llm : ChatOpenAI = ChatOpenAI(
            model_name=settings.default_open_ai_model,
            temperature=settings.default_temperature,
            openai_api_key=settings.openai_api_key
        )

    def _get_agent_tools_string(self) -> str:
        """
        Get the agent tools in a formatted string to use in the promts
        """
        formatted_tools = ""
        if self.tools:
            formatted_tools = "\n".join([f"{tool.__class__.__name__}: {tool.description}" for tool in self.tools])
        return formatted_tools
    
    def _set_agent_config(self, run_name: str):
        """
        Set the agent config for the agent, base config for all agents is set in the interface, the specific config for each agent is set in the agent class
        """
        self.agent_config = RunnableConfig(
            max_concurrency=5, 
            tags=["summarizer", "v1"],
            metadata={
                "project": "daily_job_summarizer_agent",
                "version": "1.0.0"
            },
            run_name=run_name
        )

    def _extract_tool_usage(self, result: dict) -> list:
        """
        Extrae información sobre el uso de herramientas de los pasos intermedios
        """
        tool_usage = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                tool_action = step[0]
                tool_output = step[1]
                
                tool_usage.append({
                    "tool_name": tool_action.tool,
                    "tool_input": tool_action.tool_input,
                    "tool_output": tool_output
                })
        return tool_usage
        
    @abstractmethod
    def execute_agent(self, context: str) -> str:
        pass
    