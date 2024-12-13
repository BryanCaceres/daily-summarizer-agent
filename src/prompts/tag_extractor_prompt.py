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
            Your task is to receive a pre-generated daily summary, analyze it, and identify key entities
            related to projects and people mentioned in that summary.

            With this information, you must generate a set of tags that will allow linking this summary
            to other summaries mentioning similar entities.

                The tags must follow the given schema. For each entity identified (projects or people):
                - "name": A descriptive name of the entity (e.g., project name or person's name).
                - "type": "project" or "person", depending on the entity.
                - "related_projects": For a project tag, include related projects if any; for a person tag,
                include the projects this person is involved in. For a project tag, list any people associated with it.
                - "related_people": For a person tag, include the projects they are involved in; for a project tag, 
                include the people associated with it.
                - "created_at": Must be the current UTC timestamp in ISO-8601 format.
                - "usage_count": Default to 1.
                </role>

                <task>
                Steps:
                1. Read the provided daily summary.
                2. Identify references to projects. A project could be named or hinted at by any recognizable initiative or code name.
                3. Identify references to people. This could be full names, Slack aliases, email addresses, or any identifiable personal handle.
                4. Create tags for each identified project (type="project") and each identified person (type="person").
                5. For each project tag, populate the "related_people" field with people involved in that project.
                6. For each person tag, populate the "related_projects" field with the projects they are involved in.
                7. Make sure the output follows the specified schema. Include the current UTC timestamp in ISO-8601 format for "created_at".
                8. Return only the JSON with the "tags" field as a list of objects representing the tags.

                </task>

                <rules>
                - Do not include the original summary in the response.
                - Do not perform any external calls; rely solely on the provided summary.
                - Focus on extracting entities of type "project" and "person".
                - If no projects or people are found, return an empty "tags" array.
                </rules>

                <tools>
                - Use the tools provided to extract the tags.
                - The tools are:
                    {tools}
                </tools>

                <input>
                {daily_summary}
                </input>

                <output_format>
                Respond only with a JSON in the following format:
                {
                "tags": [
                    {
                    "name": "string",
                    "type": "string", # it must be "project" or "person"
                    "related_projects": ["string"],
                    "related_people": ["string"],
                    },
                    ...
                ]
                }
                </output_format>

                <final_instructions>
                1. Analyze the {daily_summary}.
                2. Extract and normalize project and person names.
                3. Create the tag objects according to the json format defined in the output_format.
                4. Return only the JSON with the "tags" list.
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