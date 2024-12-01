from agents import GeneralModerationAgent, HatespeechExpertAgent

class CommentModerationService:
    def __init__(self):
        self.general_moderator = GeneralModerationAgent()
        self.hatespeech_expert = HatespeechExpertAgent()

    def execute_moderation(self, execution_info: dict) -> dict:
        """
        Execute the moderation process with de diferent agents
        :param execution_info: dict with the execution info
        :return: dict with the moderation result
        """
        comment_body = execution_info.get("comment_body", "")

        agents_execution_workflow = []

        general_moderation = self.general_moderator.moderate(comment_body)
        agents_execution_workflow.append(general_moderation)
        
        general_moderation_result = general_moderation.get("moderation_result", {})

        if general_moderation_result.get("general_result", False) and general_moderation_result.get("hate_speech", False):
            hatespeech_expert_result = self.hatespeech_expert.moderate(
                comment_body=comment_body,
                moderation_name=general_moderation_result.get("short_name", ""),
                moderation_reason=general_moderation_result.get("reason", ""),
                infraction_evidence=general_moderation_result.get("evidence", "")
            )
            agents_execution_workflow.append(hatespeech_expert_result)

        return agents_execution_workflow
