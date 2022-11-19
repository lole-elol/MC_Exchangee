import boto3 as boto3
from boto3.dynamodb.conditions import Key
import uuid,random
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name="eu-central-1")
table = dynamodb.Table('orders')


#    {
#       "orderID": STR ----> PARTITION KEY
#       "uid": STR,
#       "side": STR, -> "SELL/BUY" ----> SORT KEY
#       "type": str, -> ['rock','stone','dirt','gold','diamond']
#       "quantity": INT,
#       "price": DECIMAL,
#       "status": bool,
#       "split_link": str,
#       "match_link": str
#       }


# table.update_item(
#     Key={
#         'key1': 123,
#         'key2': 123
#     },
#     UpdateExpression="SET #uid = :i",
#     ConditionExpression="attribute_exists(key1)",
#     ExpressionAttributeValues={
#         ':i': orderType,
#     },
#     ExpressionAttributeNames={
#         '#uid' : "ordertype",
#     },
#     ReturnValues="NONE"
# )
# response = table.query(
#                         KeyConditionExpression=Key('key1').eq(key1) & Key('key2').eq(key2)
#                     )

# serverItem = table.get_item(Key={'key1': key1})
# table.put_item(Item={})
# table.delete_item()




def create_orders_table(dynamodb):
    table = dynamodb.create_table(
        TableName="orders",
        KeySchema=[
            {"AttributeName": "orderID", "KeyType": "HASH"},
            {"AttributeName": "side", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "orderID", "AttributeType": "S"},
            {"AttributeName": "side", "AttributeType": "S"},  # N = Number
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table

def generateTestData():
    with table.batch_writer() as writer:
        for i in range(2000):
            order = {
                "orderID": str(uuid.uuid4()),
                "uid": str(uuid.uuid4()),
                "side": random.choice(['rock','stone','dirt','gold','diamond',]),
                "type": random.choice(['BUY','SELL']),
                "quantity": random.choice(range(1, 100)),
                "price": Decimal(str(random.uniform(10.5, 75.5)))
            }
            # print(order)
            writer.put_item(Item=order)

