import json
import boto3
from boto3.dynamodb.conditions import Key
import random
import string
from decimal import Decimal

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

def lambda_handler(event, context): # handles all requests received vi9a the API
    print(event)
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

    if event['body']:
        event["body"] = json.loads(event["body"]) if type(event["body"]) is str else event["body"]
    
    if requestPath == "/order":
        order = event["body"]
        if event["httpMethod"] == "POST":
            if order["side"] == "buy" or order["side"] == "sell":
                matching(order)
                return SUCCESS

        elif event["httpMethod"] == "DELETE":
            order = event["body"]
            delete_order(orderID=order["orderID"], sortKey=order["side"])
            return SUCCESS
                
        elif event["httpMethod"] == "GET": # when order is return set collected field True
            order = event["body"]
            if to_ret := get_order(orderID=event['queryStringParameters']['orderID']):
                update_order_userCollected(to_ret[0]['orderID'],to_ret[0]['side'])
                return success(to_ret)
            else:
                return FAILURE
        
    elif requestPath == "/orderList":  # Order book of open orders filtzer by status
        if event["httpMethod"] == "GET":
            if to_ret := get_all_unmatched_orders():
                return success(to_ret)
            else:
                return success([])

    elif requestPath == "/summary":  # Orderbook of user filzer by owner id
        if event["httpMethod"] == "GET":
            order = event["body"]
            if to_ret := get_all_user_orders(event['queryStringParameters']['ownerID']):
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/poll":  # return Order filtered by user and collected
        if event["httpMethod"] == "GET":
            order = event["body"]
            if to_ret := get_uncollected_user_orders(event['queryStringParameters']['ownerID']):
                return success(to_ret)
            else:
                return FAILURE

    elif requestPath == "/balance":
        if event["httpMethod"] == "POST":
            user = event["body"]
            if to_ret := get_user(user["ownerID"]):
                return success(to_ret)
            else:
                return success(give_new_user_balance(user["ownerID"],100))

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


def balance():   # calculate and attribute outstanding balances of users
    newUserBalance = {}
    orders = get_unbalanced_and_matched_orders()
    print(orders)
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
        currentUser = get_user(user)
        if currentUser:
            currentBalance = currentUser["balance"]
        else:
            currentBalance = 100
        update_user_balance(
            user, newUserBalance[user] + currentBalance
        )


def update_order_balanced(orderID, side): # Update order to have updated users balance 
    TABLE.update_item(
        Key={
            "orderID": orderID,
            "side": side,
        },
        UpdateExpression="SET balanced = :b",
        ConditionExpression="attribute_exists(orderID)",
        ExpressionAttributeValues={
            ":b": 1,
        },
        ReturnValues="NONE",
    )


def update_user_balance(ownerID, balance): # Update the balance of a user
    BALANCE.update_item(
        Key={
            "ownerID": ownerID,
        },
        UpdateExpression="SET balance = :b",
        ConditionExpression="attribute_exists(ownerID)",
        ExpressionAttributeValues={
            ":b": Decimal(balance),
        },
        ReturnValues="NONE",
    )

def give_new_user_balance(ownerID, balance): # Give new users a initial balance
    res = BALANCE.update_item(
        Key={
            "ownerID": ownerID,
        },
        UpdateExpression="SET balance = :b",
        ConditionExpression="attribute_not_exists(ownerID)",
        ExpressionAttributeValues={
            ":b": balance,
        },
        ReturnValues="ALL_NEW")
    if "Item" in res:
        res = [{
                'ownerID': i['ownerID'],
                "balance": float(i["balance"]),
            }
            for i in res["Item"]
        ]
        return res
    else:
        return 0

def update_order_userCollected(orderID, side): # Update order once it has been received by the user via api
    TABLE.update_item(
        Key={
            "orderID": orderID,
            "side": side
        },
        UpdateExpression="SET userCollected = :b",
        ExpressionAttributeValues={
            ":b": 1,
        },
        ReturnValues="NONE",
    )


def get_all_user_orders(ownerID): # get all orders of a certain user
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
                "balanced": int(i['balanced']),
                "userCollected": int(i['userCollected']),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def get_user(primaryKey: str): # get a certain user by its id
    res = BALANCE.get_item(Key={"ownerID": primaryKey})
    if not "Item" in res:
        return None
    return {
        "balance": int(res['Item']['balance']),
        "ownerID": str(res['Item']['ownerID'])
    }

def get_uncollected_user_orders(ownerID): # get all orders that have not been fetched yet by the api
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
                "balanced": int(i['balanced']),
                "userCollected": int(i['userCollected']),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0


def get_unbalanced_and_matched_orders():  # get all unbalanced and matched orders (settled orders that do not have their balance added to the user balances yet)
    response = TABLE.query(
        IndexName="balanced-status-index",
        KeyConditionExpression=Key("balanced").eq(0)
        & Key("status").eq(0), 
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
                "balanced": int(i['balanced']),
                "userCollected": int(i['userCollected']),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0

def delete_order(orderID, sortKey): # delete a certain order from the db. Only if not settled yet
    TABLE.delete_item(
        TableName="orders",
        Key={"orderID": orderID, "side": sortKey},
        ConditionExpression="attribute_exists(orderID)",
    )


def get_order(orderID): # Get a single order by orderID
    response = TABLE.query(
        KeyConditionExpression=Key("orderID").eq(orderID))
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
                "balanced": int(i['balanced']),
                "userCollected": int(i['userCollected']),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0

def get_all_unmatched_orders(): # Get all orders that are still unsetteled/open
    response = TABLE.query(
        IndexName="status-index",
        KeyConditionExpression=Key("status").eq(0),
    )
    if "Items" in response:
        res = [
            {
                **i,
                "price": float(i["price"]),
                "quantity": float(i["quantity"]),
                "status": int(i["status"]),
                "balanced": int(i['balanced']),
                "userCollected": int(i['userCollected']),
            }
            for i in response["Items"]
        ]
        return res
    else:
        return 0
        
def generateUID(): # generate a 
    random.shuffle
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(12)
    )


def matching(in_order): # Matching algorithm. Input = Buy or Sell orders
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

    balance()

def makeBatchPutRequests(requests): # Batch all put requests for the matching algorithm to optimise for speed
    with TABLE.batch_writer() as batch:
        for item in requests:
            batch.put_item(Item=item)




def reset(): # delete all items in the DB
    db = read_db()
    for item in db:
        print(item["orderID"], type(item["orderID"]))
        TABLE.delete_item(
            TableName="orders", Key={"orderID": item["orderID"], "side": item["side"]}
        )

def init_db(obj): # create Items for the unit tests 
    for o in obj:
        TABLE.put_item(Item=o)


def read_db(): # Read the whole table for the unit tests
    item_retrieved_from_db = TABLE.scan()["Items"]
    return item_retrieved_from_db

# CREATE all necessary users DB tables
def create_users_table(dynamodb):
    table = dynamodb.create_table(
        TableName="users",
        KeySchema=[
            {"AttributeName": "ownerID", "KeyType": "HASH"}        ],
        AttributeDefinitions=[
            {"AttributeName": "ownerID", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table

def create_orders_table(dynamodb):
    table = dynamodb.create_table(
        TableName="orders",
        KeySchema=[
            {"AttributeName": "orderID", "KeyType": "HASH"},
            {"AttributeName": "side", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "key2", "AttributeType": "S"},
            {"AttributeName": "key2", "AttributeType": "S"},  # N = Number
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    return table
