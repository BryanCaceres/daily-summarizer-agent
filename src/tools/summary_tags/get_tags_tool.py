from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Optional
from services import DynamoDbService
import json
from core.settings import settings
from pydantic import Field

class GetTagsTool(BaseTool):
    """
    Tool to get existing tags from the database
    """
    name: str = "get_existing_tags"
    description: str = (
        "Get all existing tags in the database. "
        "Useful to verify previous tags before creating new ones."
    )

    dynamo_service: DynamoDbService = Field(default_factory=lambda: DynamoDbService(table_name=settings.TAGS_TABLE))

    def _run(
        self, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            result = self.dynamo_service.get_all()
            return json.dumps(result['items'], ensure_ascii=False)
        except Exception as e:
            return f"Error getting tags: {str(e)}"

get_tags_tool = GetTagsTool()