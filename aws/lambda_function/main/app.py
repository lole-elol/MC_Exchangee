import json
import boto3
import os
from boto3.dynamodb.conditions import Key

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")
DB = boto3.resource("dynamodb", region_name="eu-central-1")
TABLE = DB.Table("orders")
# import requests


def lambda_handler(event, context):

    if event["body"] is None:
        raise ValueError

    write_to_order_book(event)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }


def write_to_order_book(order) -> None:

    TABLE.put_item(TableName="orders", Item=order)


def edit_order(oprimary_key, order):
    TABLE.update_item(TableName="orders", Key=oprimary_key, UpdateExpression=order)


def matching(in_order):
    in_isBuyOrder = True if in_order["side"] == "buy" else False

    response = TABLE.query(
        IndexName="type-status-index",
        KeyConditionExpression=Key("type").eq(in_order["type"]) & Key("status").eq(1),
    )
    if "Items" in response:
        response = [
            order for order in response["Items"] if order["side"] != in_order["side"]
        ]
        response.sort(
            key=lambda x: x.get("price"), reverse=False if in_isBuyOrder else True
        )
        # print("response: ", response)
        for order in response:
            if in_isBuyOrder:
                if in_order["price"] == order["price"]:

                    in_order["match_link"] = order["orderID"]
                    order["status"], in_order["status"] = 0, 0
                    write_to_order_book(in_order)
                    write_to_order_book(order)


# lambda_handler("a", None)

eventBuy = {"uid": 123, "side": "BUY", "type": "ROCK", "quantity": 10, "price": 1000}

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


def reset():

    db = read_db()
    for item in db:
        print(item["orderID"], type(item["orderID"]))
        TABLE.delete_item(
            TableName="orders", Key={"orderID": item["orderID"], "side": item["side"]}
        )


def init_db(obj):

    for o in obj:
        TABLE.put_item(Item=o)


def read_db():
    item_retrieved_from_db = TABLE.scan()["Items"]
    return item_retrieved_from_db
