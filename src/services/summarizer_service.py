from agents import DailyJobSummarizerAgent

class SummarizerService:
    def __init__(self):
        self.summarizer = DailyJobSummarizerAgent()

    def execute_summarizer(self, day: str) -> dict:
        """
        Execute the summarizer process with the different agents
        :param day: YYYY-MM-DD str with the day to summarize
        :return: dict with the summary result
        """

        summary_result = self.summarizer.execute_agent(day)

        return summary_result
