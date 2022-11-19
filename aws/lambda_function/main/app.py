import json
import boto3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")

# import requests

DB = boto3.resource("dynamodb", region_name="eu-central-1")
TABLE = DB.Table("orders")


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

    TABLE.put_item(TableName="orders", Item=order, Exists=False)


def edit_order(oprimary_key, order):
    TABLE.update_item(TableName="orders", Key=oprimary_key, UpdateExpression=order)


def matching(order):
    order = {}

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
    empty = json.dumps({}, indent=4)
    with open(DB_PATH, "w") as file:
        file.write(empty),


def init_db(obj):
    with open(DB_PATH, "w") as file:
        file.write(json.dumps(obj, indent=4))


def read_db():
    with open(DB_PATH, "r") as file:
        data = json.load(file)
    return data


def _new_put_item(self, tableName, Item, Exists, *argparams, **kwparams):
    import json

    with open(DB_PATH, "w") as f:
        json.dump(Item, f)
        print("test put")


def _new_update_item(self, tableName, Key, UpdateExpression, *argparams, **kwparams):
    with open(DB_PATH, "w") as f:
        orders = json.loads(f)
        # orders[Key[0]][]
        # not working yet


# boto3.client.update_item = _new_update_item
