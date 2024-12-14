from core.settings import settings
import boto3

class DynamoBaseClient:
    """Base class for DynamoDB clients"""
    dynamodb = boto3.resource('dynamodb', region_name=settings.DYNAMODB_REGION_NAME)
    """The DynamoDB resource"""