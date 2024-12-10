import logging
import traceback

from agents import SlackSummarizerAgent, GmailSummarizerAgent, GeneralSummarizerAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from .slack_notification_service import SlackNotificationService
import logging

class SummarizerService:
    """
    Service to execute the summarizer workflow
    Get the summary from the different work sources and send the summary to the slack channel
    """
    def __init__(self, slack_notification_service: SlackNotificationService = None):
        self.slack_notification_service = slack_notification_service if slack_notification_service is not None else SlackNotificationService()
        self.gmail_summarizer = GmailSummarizerAgent()
        self.slack_summarizer = SlackSummarizerAgent()
        self.general_summarizer = GeneralSummarizerAgent()

    @retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=4, max=15))
    def execute_summarizer(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the summarizer process with the different agents
        :param day: YYYY-MM-DD str with the day to summarize
        :param previous_day: YYYY-MM-DD str with the previous day
        :param next_day: YYYY-MM-DD str with the next day
        :return: dict with the summary result
        """
        logging.info(f"Executing summarizer for date: {day} (prev: {previous_day}, next: {next_day})")
        
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
            
            logging.info(f"##########General summary result: {general_summary_result}")

            self.slack_notification_service.send_notification(
                    str(general_summary_result['summary_result']['daily_summary']),
                    channel='#daily-bot'
            )

            return general_summary_result

        except Exception as e:
            logging.error(f"Error executing summarizer: {e}")
            logging.error(traceback.format_exc())
            raise e
