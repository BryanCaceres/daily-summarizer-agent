from langchain_community.tools import TavilySearchResults
from core.settings import settings

class TavilySearch:
    def __init__(self):
        if not settings.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is not set in the environment variables")
        self.set_tool()
    
    def set_tool(self):
        self.tool = TavilySearchResults(
            name="web_search",
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=True,
            description="Search the web for information about words or phrases to be clear in the meaning of a text, always use this tool to understand the meaning of words or phrases."
        )

tavily_search = TavilySearch()