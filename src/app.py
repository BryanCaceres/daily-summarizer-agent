import json
import traceback
from services import CommentModerationService

moderation_service = CommentModerationService()

def lambda_handler(event, context):
    """
    Langchain Lambda Moderator
    """
    try:
        request_body = json.loads(event["body"])
        moderation_result = moderation_service.execute_moderation(request_body)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "moderation_result": moderation_result
            })
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
