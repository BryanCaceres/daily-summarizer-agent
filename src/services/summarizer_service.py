import logging
import traceback

from agents import SlackSummarizerAgent, GmailSummarizerAgent, GeneralSummarizerAgent, TagExtractorAgent
from .pinecone_service import PineconeService
from .dynamo.dynamo_db_service import DynamoDbService
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential
from .slack_notification_service import SlackNotificationService
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from core.settings import settings

class SummarizerService:
    """
    Service to execute the summarizer workflow
    Get the summary from the different work sources and send the summary to the slack channel
    """
    def __init__(self, slack_notification_service: SlackNotificationService = None):
        self.slack_notification_service = slack_notification_service if slack_notification_service is not None else SlackNotificationService()
        self.gmail_summarizer = GmailSummarizerAgent(dummy_mode=True)
        self.slack_summarizer = SlackSummarizerAgent(dummy_mode=True)
        self.general_summarizer = GeneralSummarizerAgent()
        self.vector_store = PineconeService()
        self.tag_extractor = TagExtractorAgent()
        self.summaries_db = DynamoDbService(table_name=settings.SUMMARY_TABLE)
        
    def execute_summarizer(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the summarizer process with the different agents
        :param day: YYYY-MM-DD str with the day to summarize
        :param previous_day: YYYY-MM-DD str with the previous day
        :param next_day: YYYY-MM-DD str with the next day
        :return: dict with the summary result
        """
        logging.debug(f"Executing summarizer for date: {day} (prev: {previous_day}, next: {next_day})")
        
        try:
            gmail_summary_result = self.gmail_summarizer.execute_agent(
            day=day,
            previous_day=previous_day,
            next_day=next_day
            )
            
            slack_summary_result = self.slack_summarizer.execute_agent(
                day=day,
                previous_day=previous_day,
                next_day=next_day
            )

            general_summary_result = self.general_summarizer.execute_agent(
                day=day,
                gmail_summary_json=gmail_summary_result,
                slack_summary_json=slack_summary_result
            )
                        
            raw_summary = general_summary_result['summary_result']['daily_summary']
            tag_extractor_result = self.tag_extractor.execute_agent(
                summary=raw_summary
            )

            summary_tags = tag_extractor_result['tags_result']['tags']
            
            people = [tag['name'] for tag in summary_tags if tag['type'] == 'person']
            projects = [tag['name'] for tag in summary_tags if tag['type'] == 'project']
            areas = [tag['name'] for tag in summary_tags if tag['type'] == 'area']
            
            people_str = f"Personas involucradas: {', '.join(people)}"
            projects_str = f"Proyectos involucrados: {', '.join(projects)}"
            areas_str = f"Areas involucradas: {', '.join(areas)}"
            
            semantic_raw_summary = f"{raw_summary}\n\n{str(people_str)}\n\n{str(projects_str)}\n\n{str(areas_str)}"

            self.slack_notification_service.send_notification(
                    semantic_raw_summary,
                    channel='#daily-bot'
            )

            general_summary_result['tags'] = summary_tags

            flattened_metadata = self.vector_store.flatten_metadata(general_summary_result)
            self.vector_store.add_documents([Document(page_content=semantic_raw_summary, metadata=flattened_metadata)])
            
            self.summaries_db.create(general_summary_result)
            
            return {
                "general_summary_result": general_summary_result,
                "slack_summary_result": slack_summary_result,
                "gmail_summary_result": gmail_summary_result
            }

        except Exception as e:
            logging.error(f"Error executing summarizer: {e}")
            logging.error(traceback.format_exc())
            raise e