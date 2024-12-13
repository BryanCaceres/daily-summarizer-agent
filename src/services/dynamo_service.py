import boto3
from core.settings import settings
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
import logging, traceback
import uuid
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from botocore.config import Config

class DynamoDbService:
    """
    Singleton Client Service to manage the DynamoDB database
    """
    _instances = {}  # Singleton per table
    _table_cache = {}  # Shared table cache for all instances
    dynamodb_client = None

    def __new__(cls, table_name: str):
        if table_name not in cls._instances:
            instance = super(DynamoDbService, cls).__new__(cls)
            instance.dynamodb_client = boto3.resource('dynamodb', region_name=settings.DYNAMODB_REGION_NAME)
            instance.table_name = table_name
            cls._instances[table_name] = instance
        return cls._instances[table_name]

    def __init__(self, table_name: str):
        if not hasattr(self, '_initialized'):
            self._initialized = True
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
            table.load()
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
                    },
                    {
                        'AttributeName': 'created_at',
                        'AttributeType': 'N'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {
                        'Key': 'Environment',
                        'Value': settings.ENVIRONMENT
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Summarizer AI'
                    }
                ]
            )

            table.meta.client.get_waiter('table_exists').wait(
                TableName=table_name,
                WaiterConfig={
                    'Delay': 5,
                    'MaxAttempts': 10
                }
            )
            
            table.update_time_to_live(
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )

            table.update(
                PointInTimeRecoverySpecification={
                    'PointInTimeRecoveryEnabled': True
                }
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
        Gets a item by its UUID
        :param primary_key: Primary key of the item to get
        :return: Found item or error message
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
        Creates a new single item in DynamoDB
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

    def bulk_create(self, items: List[Dict]) -> Dict:
        """
        Creates multiple items in DynamoDB using batch operations
        :param items: List of items to create
        :return: Status of the operation
        """
        try:
            date_now = datetime.now(timezone.utc).isoformat()
            created_items = []
            with self.table.batch_writer() as batch:
                for item in items:
                    item_uuid = str(uuid.uuid4())
                    item['uuid'] = item_uuid
                    item['created_at'] = date_now
                    batch.put_item(Item=item)
                    created_items.append(item)
            message = f"Wrote {len(items)} items successfully"
            logging.info(message)

            return {"status": "success", "message": message, "items": created_items}
        except ClientError as e:
            logging.error(f"Error in batch write: {e}")
            raise e
