from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
import logging, traceback
import uuid
from datetime import datetime, timezone
from .dynamo_client import DynamoBaseClient
from decimal import Decimal


class DynamoDbService(DynamoBaseClient):
    """
    Class to manage the DynamoDB database
    """
    _table_cache = {} #Singleton instance per table using the base boto3 resource

    def __init__(self, table_name: str):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.table_name = table_name
            self.table = self._get_table(table_name)

    def _get_table(self, table_name: str) -> Any:
        """Gets and validates table exists in DynamoDB"""
        if table_name in self._table_cache:
            return self._table_cache[table_name]

        if self._validate_table_exists(table_name):
            table = self.dynamodb.Table(table_name)
            self._table_cache[table_name] = table
            return table

    def _validate_table_exists(self, table_name: str) -> bool:
        try:
            table = self.dynamodb.Table(table_name)
            table.load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError(f"Table {table_name} does not exist")
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
            
            parsed_response = {
                'items': self.parse_dynamo_response(response.get('Items', [])),
                'next_page_token': response.get('LastEvaluatedKey'),
                'consumed_capacity': response.get('ConsumedCapacity')
            }
            
            return parsed_response

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

            return {"status": "successful operation", "message": message, "items": created_items}
        except ClientError as e:
            logging.error(f"Error in batch write: {e}")
            raise e
    
    @staticmethod
    def parse_dynamo_response(dynamo_data: Any) -> Any:
        """
        Parses the DynamoDB response to handle special types like Decimal 
        Args: dynamo_data: Can be a dictionary, list or simple value from DynamoDB
        Returns: Parsed data in JSON serializable format
        """
        if isinstance(dynamo_data, dict):
            return {
                key: DynamoDbService.parse_dynamo_response(value) 
                for key, value in dynamo_data.items()
            }
        elif isinstance(dynamo_data, list):
            return [
                DynamoDbService.parse_dynamo_response(item) 
                for item in dynamo_data
            ]
        elif isinstance(dynamo_data, Decimal):
            return float(dynamo_data)
        elif isinstance(dynamo_data, (str, int, float, bool, type(None))):
            return dynamo_data
        else:
            return str(dynamo_data)