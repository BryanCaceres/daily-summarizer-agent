from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, List, Any, Type
from services import DynamoDbService
import json
from core.settings import settings
import logging

class CreateTagsSchema(BaseModel):
    """
    Esquema para crear nuevas tags
    """
    tags: List[dict] = Field(
        ..., 
        description="""List of tags objects to create with the following structure: 
        {{
            "name": "string",
            "type": "string", # "project", "person", "other"
            "related_projects": ["string"], # list of project names
            "related_people": ["string"] # list of people names
        }}
        the tags in the list must be valid."""
    )

class CreateTagsTool(BaseTool):
    """
    Tool to create new tags in the database if they are not already present.
    <example_usage>
    To create new tags, you must use the create_new_tags tool with the following structure:
    {
        "tags": [
            {
                "name": "Tag_name",
                "type": "project",
                "related_projects": ["Project_name1", "Project_name2"],
                "related_people": ["Person_name1", "Person_name2"]
            },
            {
                "name": "Tag_name2",
                "type": "area",
                "related_projects": ["Project_name3", "Project_name4"],
                "related_people": ["Person_name3", "Person_name4"]
            }
        ]
    }
    
    Remember:
    - The "type" field must be either "project" or "area"
    - "related_projects" and "related_people" are arrays of strings
    - Area is things like a "development", "marketing", "sales", "design", "etc"
    - Always include the "tags" key in the root of the object
    </example_usage>
    """
    name: str = "create_new_tags"
    description: str = (
        "Create new tags in the database. "
        "Allows adding multiple tags with detailed information."
    )

    dynamo_service: DynamoDbService = Field(default_factory=lambda: DynamoDbService(table_name=settings.TAGS_TABLE)) 
    args_schema: Type[CreateTagsSchema] = CreateTagsSchema
    
    _usage_count: int = PrivateAttr(default=0)
    _cached_created_tags: List = PrivateAttr(default_factory=list)

    def _run(
        self, 
        tags: List[dict],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            logging.info(f"########The agent is creating the following tags: {tags}")
            validated_tags = [
                {
                    "name": tag['name'],
                    "type": tag['type'],
                    "related_projects": tag.get('related_projects', []),
                    "related_people": tag.get('related_people', []),
                    "usage_count": 1
                } for tag in tags
            ]
            
            if self._usage_count > 0:
                return json.dumps(self._cached_created_tags['items'], ensure_ascii=False)

            result = self.dynamo_service.bulk_create(validated_tags)
            self._usage_count += 1
            self._cached_created_tags = result
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return f"Error creating tags: {str(e)}"
    
    @classmethod
    def reset_usage_count(cls):
        cls._usage_count = 0
        cls._cached_created_tags = []
    
create_tags_tool = CreateTagsTool()