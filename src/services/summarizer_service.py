from agents import DailyJobSummarizerAgent
import logging

class SummarizerService:
    def __init__(self):
        self.summarizer = DailyJobSummarizerAgent()

    def execute_summarizer(self, day: str, previous_day: str, next_day: str) -> dict:
        """
        Execute the summarizer process with the different agents
        :param day: YYYY-MM-DD str with the day to summarize
        :param previous_day: YYYY-MM-DD str with the previous day
        :param next_day: YYYY-MM-DD str with the next day
        :return: dict with the summary result
        """
        logging.info(f"Executing summarizer for date: {day} (prev: {previous_day}, next: {next_day})")
        
        summary_result = self.summarizer.execute_agent(
            day=day,
            previous_day=previous_day,
            next_day=next_day
        )

        if summary_result.get("summary_result", {}).get("day") != day:
            logging.warning(f"Date mismatch in result. Expected: {day}, Got: {summary_result.get('summary_result', {}).get('day')}")

        return summary_result
