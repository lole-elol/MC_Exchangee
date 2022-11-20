import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import botocore
import random
import string

DB = boto3.resource("dynamodb", region_name="eu-central-1")

TABLE = DB.Table("orders")
BALANCE = DB.Table("users")

SUCCESS = {
    "statusCode": 200,
    "body": json.dumps(
        {
            "message": "Success",
        }
    ),
}


FAILURE_DEL = {
    "statusCode": 400,
    "body": json.dumps(
        {
            "message": "Order cannot be deleted. It does not exist",
        }
    ),
}

FAILURE = {
    "statusCode": 400,
    "body": json.dumps(
        {
            "message": "Order does not exist",
        }
    ),
}


def success(order):
    return {"statusCode": 200, "body": json.dumps(order)}


def lambda_handler(event, context):
    requestPath = event["path"].split("/hackatum-BloombergBackend-1znJQelc3f38")[-1]
    print(
        "requestPath:",
        requestPath,
        "Method:",
        event["httpMethod"],
        "Body:",
        event["body"],
        "QueryStringParameters:",
        event["queryStringParameters"],
    )

    # Technically better via TryExcept but I can't remember the exact Error
    # event["body"] = json.loads(event["body"]) if event['body'] is not None else None

    if requestPath == "/order":
        if event["httpMethod"] == "POST":
            if event["body"]["side"] == "buy" or event["body"]["side"] == "sell":
                matching(event["body"])
                return SUCCESS

        elif event["httpMethod"] == "DELETE":
            order = event["body"]
            try:
                delete_order(orderID=order["orderID"], sortKey=order["side"])

                return SUCCESS
            except botocore.exceptions.ClientError:
                # if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                return FAILURE_DEL

        elif (
            event["httpMethod"] == "GET"
        ):  # when order is return set collected field True
            order = event["body"]
            if to_ret := get_order(orderID=order["orderID"]):
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/orderList":  # Order book of open orders filtzer by status
        if event["httpMethod"] == "GET":
            if to_ret := get_all_unmatched_orders():
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/summary":  # Orderbook of user filzer by owner id
        if event["httpMethod"] == "GET":
            if to_ret := get_all_user_orders(event["ownerID"]):
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/poll":  # return Order filtered by user and collected
        if event["httpMethod"] == "GET":
            order = event["body"]
            if to_ret := get_uncollected_user_orders(order["ownerID"]):
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/balance":
        if event["httpMethod"] == "GET":
            user = event["body"]
            if to_ret := get_user(user[""]):
                return success(to_ret)
            else:
                return FAILURE

    else:
        print("no viable path")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "hello world",
                }
            ),
        }


def balance():
    # claculate balance of users
    newUserBalance = {}
    orders = get_unbalanced_and_matched_orders()
    for order in orders:
        update_order_balanced(
            order["orderID"], order["side"]
        )  # set for all orders "balanced" to 1
        if order["ownerID"] in newUserBalance:
            if order["side"] == "buy":
                newUserBalance[order["ownerID"]] -= order["price"] * order["quantity"]
            else:
                newUserBalance[order["ownerID"]] += order["price"] * order["quantity"]
        else:
            if order["side"] == "buy":
                newUserBalance[order["ownerID"]] = -order["price"] * order["quantity"]
            else:
                newUserBalance[order["ownerID"]] = order["price"] * order["quantity"]

    for user in newUserBalance:  # update all users
        currentUser = get_user(user["ownerID"])
        update_user_balance(
            user["ownerID"], newUserBalance[user["ownerID"]] + currentUser["balance"]
        )


def update_order_balanced(orderID, side):
    TABLE.update_item(
        Key={
            "ownerID": orderID,
            "side": side,
        },
        UpdateExpression="SET balanced = :b",
        ConditionExpression="attribute_exists(orderID)",
        ExpressionAttributeValues={
            ":b": 1,
        },
        ReturnValues="NONE",
    )


def update_user_balance(ownerID, balance):
    BALANCE.update_item(
        Key={
            "ownerID": ownerID,
        },
        UpdateExpression="SET balance = :b",
        ConditionExpression="attribute_exists(ownerID)",
        ExpressionAttributeValues={
            ":b": balance,
        },
        ReturnValues="NONE",
    )


def write_to_order_book(order) -> None:
    TABLE.put_item(TableName="orders", Item=order)


def get_all_user_orders(ownerID):
    response = TABLE.query(
        IndexName="ownerID-userCollected-index",
        KeyConditionExpression=Key("ownerID").eq(ownerID),
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def get_user(primaryKey):
    result = BALANCE.get_item(Key={"ownerID": primaryKey})
    if "Item" in result:
        return result["Item"]
    else:
        return 0


def get_uncollected_user_orders(ownerID):
    response = TABLE.query(
        IndexName="ownerID-userCollected-index",
        KeyConditionExpression=Key("ownerID").eq(ownerID) & Key("userCollected").eq(0),
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def get_unbalanced_and_matched_orders():
    response = TABLE.query(
        IndexName="balanced-status-index",
        KeyConditionExpression=Key("balanced").eq(0)
        & Key("status").eq(1),  # get all unbalanced and matched orders
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def delete_order(orderID, sortKey):
    TABLE.delete_item(
        TableName="orders",
        Key={"orderID": orderID, "side": sortKey},
        ConditionExpression="attribute_exists(orderID)",
    )


def get_order(orderID):
    response = TABLE.get_item(Key={"orderID": orderID})
    if "Item" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
            }
            for i in response["Item"]
        ]
        return res
    else:
        return 0


def get_all_unmatched_orders():
    response = TABLE.query(
        IndexName="status-index",
        KeyConditionExpression=Key("status").eq(1),
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def generateUID():
    random.shuffle
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(12)
    )


def matching(in_order):
    in_order["orderID"] = generateUID()
    in_isBuyOrder = True if in_order["side"] == "buy" else False

    response = TABLE.query(
        IndexName="type-status-index",
        KeyConditionExpression=Key("type").eq(in_order["type"]) & Key("status").eq(1),
    )
    if "Items" in response:
        response = (
            [  # Get only orders which are on the opposite site of the incoming one
                order
                for order in response["Items"]
                if order["side"] != in_order["side"]
            ]
        )
        response.sort(  # sort based on the unit price
            key=lambda x: x.get("price"), reverse=False if in_isBuyOrder else True
        )

        firstRun = True
        putRequests = []
        if not response:
            putRequests.append(in_order)
        for order in response:
            if in_isBuyOrder:
                # buy order
                if in_order["price"] == order["price"]:

                    if in_order["quantity"] > order["quantity"]:
                        # buy qt > sell qt -> buy split
                        diff_buy = in_order.copy()
                        in_order["quantity"] = order["quantity"]
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        diff_buy["quantity"] -= order["quantity"]
                        diff_buy["split_link"] = diff_buy["orderID"]
                        diff_buy["orderID"] = generateUID()
                        putRequests.extend([diff_buy, in_order, order])

                        in_order = diff_buy.copy()
                        diff_buy["match_link"] = ""
                        diff_buy["status"] = 1

                    elif in_order["quantity"] < order["quantity"]:
                        # buy qt < sell qt -> sell split
                        diff_sell = order.copy()
                        order["quantity"] = in_order["quantity"]
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        # new child order_
                        diff_sell["quantity"] -= in_order["quantity"]
                        diff_sell["split_link"] = diff_sell["orderID"]
                        diff_sell["orderID"] = generateUID()
                        putRequests.extend([diff_sell, in_order, order])

                    else:
                        # buy qt = sell qt
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        putRequests.extend([in_order, order])

                elif in_order["price"] > order["price"]:
                    # buy order price > sell order

                    if in_order["quantity"] > order["quantity"]:
                        # buy qt > sell qt -> buy split
                        diff_buy = in_order.copy()
                        in_order["quantity"] = order["quantity"]
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        in_order["price"] = order["price"]

                        # new child order
                        diff_buy["quantity"] -= order["quantity"]
                        diff_buy["split_link"] = diff_buy["orderID"]
                        diff_buy["orderID"] = generateUID()
                        putRequests.extend([diff_buy, in_order, order])

                    elif in_order["quantity"] < order["quantity"]:
                        # buy qt < sell qt -> sell split
                        diff_sell = order.copy()
                        order["quantity"] = in_order["quantity"]
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        in_order["price"] = order["price"]

                        # new child order_
                        diff_sell["quantity"] -= in_order["quantity"]
                        diff_sell["split_link"] = diff_sell["orderID"]
                        diff_sell["orderID"] = generateUID()

                        # child = diff_sell["split_link"]
                        putRequests.extend([diff_sell, in_order, order])

                    else:
                        # buy qt = sell qt
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        in_order["price"] = order["price"]

                        putRequests.extend([in_order, order])
                else:

                    if firstRun:
                        putRequests.append(in_order)

            elif not in_isBuyOrder:
                # sell order
                if in_order["price"] == order["price"]:

                    if in_order["quantity"] > order["quantity"]:
                        # sell qt > buy qt -> sell split
                        diff_sell = in_order.copy()
                        in_order["quantity"] = order["quantity"]
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        diff_sell["quantity"] -= order["quantity"]
                        diff_sell["split_link"] = diff_sell["orderID"]
                        diff_sell["orderID"] = generateUID()
                        putRequests.extend([diff_sell, in_order, order])

                        in_order = diff_sell.copy()
                        diff_sell["match_link"] = ""
                        diff_sell["status"] = 1

                    elif in_order["quantity"] < order["quantity"]:
                        # sell qt < buy qt -> buy split
                        diff_buy = order.copy()
                        order["quantity"] = in_order["quantity"]
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        # new child order_
                        diff_buy["quantity"] -= in_order["quantity"]
                        diff_buy["split_link"] = diff_buy["orderID"]
                        diff_buy["orderID"] = generateUID()
                        putRequests.extend([diff_buy, in_order, order])

                    else:  # symmetrisch
                        # buy qt = sell qt
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        putRequests.extend([in_order, order])

                elif in_order["price"] < order["price"]:
                    # sell order price < buy order

                    if in_order["quantity"] > order["quantity"]:
                        # sell qt > buy qt -> sell split
                        diff_sell = in_order.copy()
                        in_order["quantity"] = order["quantity"]
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        order["price"] = in_order["price"]

                        # new child order
                        diff_sell["quantity"] -= order["quantity"]
                        diff_sell["split_link"] = diff_sell["orderID"]
                        diff_sell["orderID"] = generateUID()

                        # save split link id in child

                        putRequests.extend([diff_sell, in_order, order])

                    elif in_order["quantity"] < order["quantity"]:
                        # sell qt < buy qt -> buy split

                        diff_buy = order.copy()
                        order["quantity"] = in_order["quantity"]
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        order["price"] = in_order["price"]

                        # new child order_
                        diff_buy["quantity"] -= in_order["quantity"]
                        diff_buy["split_link"] = diff_buy["orderID"]
                        diff_buy["orderID"] = generateUID()

                        # save split link id in child
                        putRequests.extend([diff_buy, in_order, order])

                    else:
                        # buy qt = sell qt
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        order["price"] = in_order["price"]

                        putRequests.extend([in_order, order])

                else:
                    if firstRun:
                        putRequests.append(in_order)
            firstRun = False
            if len(putRequests) > 21:
                makeBatchPutRequests(putRequests)
                putRequests = []
        if putRequests:
            makeBatchPutRequests(putRequests)


def makeBatchPutRequests(requests):
    with TABLE.batch_writer() as batch:
        for item in requests:
            batch.put_item(Item=item)


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
