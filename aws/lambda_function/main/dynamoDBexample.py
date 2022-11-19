import boto3 as boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name="eu-central-1")
table = dynamodb.Table('orders')

table.update_item(
    Key={
        'key1': 123,
        'key2': 123
    },
    UpdateExpression="SET #uid = :i",
    ConditionExpression="attribute_exists(key1)",
    ExpressionAttributeValues={
        ':i': orderType,
    },
    ExpressionAttributeNames={
        '#uid' : "ordertype",
    },
    ReturnValues="NONE"
)
response = table.query(
                        KeyConditionExpression=Key('key1').eq(key1) & Key('key2').eq(key2)
                    )

serverItem = table.get_item(Key={'key1': key1})
table.put_item(Item={})
table.delete_item()


def create_orders_table(dynamodb):
    table = dynamodb.create_table(
        TableName='orders',
        KeySchema=[
            {
                'AttributeName': 'key1',
                'KeyType'      : 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key2',
                'AttributeType': 'N'  # N = Number
            }
        ],
        BillingMode='PAY_PER_REQUEST',
    )
    table.wait_until_exists()
    return table
