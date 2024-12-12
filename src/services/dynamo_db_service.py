import boto3
from core.settings import settings
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
import logging, traceback
import uuid
from datetime import datetime, timezone

class DynamoDbService:
    """
    Singleton Service to manage the DynamoDB database
    """
    dynamodb_client = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DynamoDbService, cls).__new__(cls)
            cls.instance.dynamodb_client = boto3.resource('dynamodb', region_name=settings.DYNAMODB_REGION_NAME)
        return cls.instance

    def __init__(self, table_name: str):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.table_name = table_name
            self.table = self._get_or_create_table(table_name)

    def _get_or_create_table(self, table_name: str) -> Any:
        """
        Gets or creates a table in DynamoDB
        :param table_name: Name of the table
        :return: Table object
        """
        if table_name in self._table_cache:
            return self._table_cache[table_name]

        try:
            table = self.dynamodb_client.Table(table_name)
            table.load()  # Try to load the table to verify if it exists
            self._table_cache[table_name] = table
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return self._create_table(table_name)
            raise e
        
    def _create_table(self, table_name: str) -> Any:
        """
        Creates a new table in DynamoDB with standard configuration
        :param table_name: Name of the table to create
        :return: Table object
        """
        try:
            table = self.dynamodb_client.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'uuid',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'uuid',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )

            table.meta.client.get_waiter('table_exists').wait(
                TableName=table_name
            )
            
            self._table_cache[table_name] = table
            logging.info(f"Table {table_name} created successfully")
            return table
            
        except ClientError as e:
            logging.error(f"Error creating table {table_name}: {e}")
            logging.error(traceback.format_exc())
            raise e

    def get_all(self, last_evaluated_key: Optional[Dict] = None, limit: int = 50) -> Dict:
        """
        Gets all items from DynamoDB table
        :params:
            last_evaluated_key: Last evaluated key from previous scan
            limit: Limit of items to return
        :return: List of items from table
        """
        try:
            query_params = {
                'Limit': limit,
                'ReturnConsumedCapacity': 'TOTAL',
                'ConsistentRead': False
            }
            
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.scan(**query_params)
            
            return {
                'items': response.get('Items', []),
                'next_page_token': response.get('LastEvaluatedKey'),
                'consumed_capacity': response.get('ConsumedCapacity')
            }

        except ClientError as e:
            logging.error(f"Error getting all {self.table.name}: {e}")
            logging.error(traceback.format_exc())
            raise e
    
    def get_by_pk(self, primary_key: str) -> Optional[Dict]:
        """
        Gets a product by its UUID
        :param primary_key: Primary key of the product to get
        :return: Found product or error message
        """
        try:
            response = self.table.get_item(
                Key={'uuid': primary_key},
                ConsistentRead=True
            )
            
            item = response.get('Item')
            if not item:
                raise ClientError(f'Item not found for {self.table} with id {primary_key}')

            return item
        except ClientError as e:
            logging.error(f"Error getting by id: {e}")
            logging.error(traceback.format_exc())
            raise e

    def create(self, item: Dict) -> Dict:
        """
        Creates a new item in DynamoDB
        :param item: Dictionary with the item data
        :return: Created item
        """
        try:
            item_uuid = str(uuid.uuid4())
            item['uuid'] = item_uuid
            item['created_at'] = datetime.now(timezone.utc).isoformat()
            self.table.put_item(Item=item)

            return item
        except ClientError as e:
            logging.error(f"Error creating {self.table.name}: {e}")
            logging.error(traceback.format_exc())
            raise e
