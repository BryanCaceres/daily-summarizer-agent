import json
import traceback
from services import SummarizerService
from datetime import datetime

summarizer_service = SummarizerService()

def lambda_handler(event, context):
    """
    Langchain Lambda Summarizer
    """
    try:
        if "body" in event:  # API Gateway EndPoint
            request_body = json.loads(event["body"])
            date = request_body.get("date")
        elif "date" in event:  # EventBridge from CronJob
            date = event.get("date")
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        summary_result = summarizer_service.execute_summarizer(day=date)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "summary_result": summary_result
            })
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
