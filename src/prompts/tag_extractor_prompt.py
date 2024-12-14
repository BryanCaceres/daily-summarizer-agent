from langchain_core.prompts import PromptTemplate
from prompts.prompts_interface import PromptsInterface

class TagExtractorPrompt(PromptsInterface):
    """
    Prompt for analyzing a daily summary and extracting contextual tags, 
    oriented to projects and people involved in the summary, 
    with the purpose of tagging the summary and being able to link it later 
    with other summaries mentioning similar entities.
    """
    def __init__(self):
        super().__init__()

    def get_prompt(self) -> PromptTemplate:
        TEMPLATE_TEXT = """
            <role>
            You are an expert assistant in semantic text analysis and metadata extraction.
            Your task is to receive a pre-generated daily summary, analyze it, identify key entities
            related to projects and people mentioned in that summary, and create new tags when necessary.
            </role>

            <task>
            Steps:
            1. Read the provided daily summary.
            2. Identify references to projects and people.
            3. For each identified entity:
                a. Check if it exists in the database using the provided tools
                b. If it doesn't exist, create it using the tag creation tool
                c. If it exists, use the existing information
            4. Create relationships between projects and people
            5. Ensure all necessary tags exist in the system
            </task>

            <rules>
            - Do not include the original summary in the response
            - Do not perform any external calls; rely solely on the provided tools
            - Focus on extracting entities of type "project" and "person"
            - Verify each tag's existence before attempting to create it
            - Create new tags only when necessary following the rules of the database
            - After creating a tag, use the tool to get the tag information form the database.
            - When you use create_new_tags, ALWAYS you must include the list of tags in the following format:
                {{
                    "tags": [
                        {{
                            "name": "tag_name",  (string)
                            "type": "project" | "person",  (string)
                            "related_projects": ["project_name1", "project_name2"],  (list of strings)
                            "related_people": ["person_name1", "person_name2"]  (list of strings)
                        }}
                    ]
                }}
            - If a tag already exists, ALWAYS use that information instead of creating a new one.
            - The tags must be as general as possible, not very specific. for example:
                - "Presentation" is a project, but "Presentation" is not a tag, it's a part of a project.
                - "Bryan" is a person, but "Bryan" is not a tag, it's a name of a person.
                - "David" is a person, but "David" is not a tag, it's a name of a person.
            - The tags must be unique and not similar to other existing tags.
            - The tags must be reusable and not specific to a single summary, think about the future use of the tag before creating it. Only create tags that will be used in the future.
            - Avoid duplicate tags or creating tags with the same name or similar names.
            - Avoid creating innecesary tags, if already exists a similar tag, use that information instead of creating a new one.
            - If you create a innecesary tag, you will be penalized and fired.
            - If the database is empty (get_existing_tags returns an empty list), proceed directly to creating new tags using your tools
            - Limit tag existence checks to once at the beginning
            - Do not perform repetitive tag existence checks
            </rules>

            <tools>
                The tools are:
                {tools}
            </tools>

            <input>
            {daily_summary}
            </input>

            <output_format>
            Respond only with a JSON in the following format:
                <JSON>
                    "tags": [
                        <JSON Item>
                            "name": "string",
                            "type": "string", # it must be "project" or "person"
                            "related_projects": ["string"],
                            "related_people": ["string"],
                        </JSON Item>
                        ...
                    ],
                    "new_tags_created": ["string"] # list of newly created tags
                <JSON>
            </output_format>

            <final_instructions>
            1. Analyze the daily_summary
            2. For each identified entity:
                - Check if it exists in the database
                - If it doesn't exist, create it using the appropriate tool
            3. Establish relationships between entities
            4. Return the JSON with all tags and a list of newly created tags
            </final_instructions>

            <constraints>
                {security_instructions}
                {output_language}
                {reward}
            </constraints>

            <scratchpad>
            {agent_scratchpad}
            </scratchpad>
        """
        return PromptTemplate(
                input_variables=["daily_summary", "tools"],
                template=TEMPLATE_TEXT,
                partial_variables={
                    "output_language": self.output_language,
                    "security_instructions": self.security_instructions,
                    "reward": self.reward
                }
            )