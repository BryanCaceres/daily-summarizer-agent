from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Type
from services import DynamoDbService
import json
from core.settings import settings

class CreateTagsSchema(BaseModel):
    """
    Esquema para crear nuevas tags
    """
    tags: List[dict] = Field(
        ..., 
        description="List of tags to create with the following structure: {name, type, related_projects?, related_people?} the tags in the list must be valid."
    )

class CreateTagsTool(BaseTool):
    """
    Tool to create new tags in the database if they are not already present.
    """
    name: str = "create_new_tags"
    description: str = (
        "Create new tags in the database. "
        "Allows adding multiple tags with detailed information."
    )
    args_schema: Type[CreateTagsSchema] = CreateTagsSchema

    def __init__(self, table_name: str = settings.TAGS_TABLE):
        super().__init__()
        self.dynamo_service = DynamoDbService(table_name=table_name)

    def _run(
        self, 
        tags: List[dict],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            validated_tags = [
                {
                    "name": tag['name'],
                    "type": tag['type'],
                    "related_projects": tag.get('related_projects', []),
                    "related_people": tag.get('related_people', []),
                    "usage_count": 1
                } for tag in tags
            ]

            result = self.dynamo_service.bulk_create(validated_tags)
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return f"Error creating tags: {str(e)}"