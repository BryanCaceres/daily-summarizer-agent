from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from typing import Optional, Any
from services import DynamoDbService
import json
from core.settings import settings

class GetTagsTool(BaseTool):
    """
    Tool to get existing tags in the database
    """
    name: str = "get_existing_tags"
    description: str = (
        "Get all existing tags in the database. "
        "Useful to verify previous tags before creating new ones."
    )

    def __init__(self, table_name: str = settings.TAGS_TABLE):
        super().__init__()
        self.dynamo_service = DynamoDbService(table_name=table_name)

    def _run(
        self, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            result = self.dynamo_service.get_all()
            return json.dumps(result['items'], ensure_ascii=False)
        except Exception as e:
            return f"Error getting tags: {str(e)}"