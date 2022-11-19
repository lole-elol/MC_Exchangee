import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import botocore
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")
DB = boto3.resource("dynamodb", region_name="eu-central-1")
TABLE = DB.Table("orders")
BALANCE = DB.Table("users")

SUCCESS = {"statusCode": 200,
    "body": json.dumps(
        {
            "message": "Success",
        }
    )}


FAILURE_DEL = {"statusCode": 400,
                "body": json.dumps(
                    {
                        "message": "Order cannot be deleted. It does not exist",
                    }
                )}

FAILURE = {"statusCode": 400,
                "body": json.dumps(
                    {
                        "message": "Order does not exist",
                    }
                )}



def success(order):
    return {"statusCode": 200, "body": json.dumps(order)}
    

def lambda_handler(event, context):
    requestPath = event['path'].split('/hackatum-BloombergBackend-1znJQelc3f38')[-1]
    print('requestPath:',requestPath,'Method:',event["httpMethod"],'Body:',event["body"],'QueryStringParameters:',event['queryStringParameters'])
    if requestPath == "/order":
        if event["httpMethod"] == "POST":
            if event["body"]["action"] == "buy" or event["body"]["action"] == "sell":
                matching(event['body'])
                return SUCCESS
                 

        elif event["httpMethod"] == "DELETE":
            # if event["body"]["action"] == "buy":
            order = event["body"]
            try:
                delete_order(primaryKey=order['orderID'],sortKey=order['side'])
            # Postponed
            # except: 
            #     return FAILURE_DEL
            # else:
                return SUCCESS
            except botocore.exceptions.ClientError:
                # if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                return FAILURE_DEL
                
                
        elif event["httpMethod"] == "GET": # when order is return set collected field True
            order = event["body"]
            if to_ret := get_order(primaryKey=order['orderID']):
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
            if to_ret := get_all_user_orders(event['ownerID']):
                return success(to_ret)
            else:
                return FAILURE
            

    elif requestPath == "/poll":  # return Order filtered by user and collected
        if event["httpMethod"] == "GET":
            order = event["body"]
            if to_ret := get_uncollected_user_orders(order['ownerID']):
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
        update_order_balanced(order['orderID'],order['side']) # set for all orders "balanced" to 1
        if order['ownerID'] in newUserBalance:
            if order["side"] == "buy":
                newUserBalance[order['ownerID']] -= order['price'] * order['quantity']
            else:
                newUserBalance[order['ownerID']] += order['price'] * order['quantity']
        else:
            if order["side"] == "buy":
                newUserBalance[order['ownerID']] = -order['price'] * order['quantity']
            else:
                newUserBalance[order['ownerID']] = order['price'] * order['quantity']
        
    for user in newUserBalance: # update all users
        currentUser = get_user(user['ownerID'])
        update_user_balance(user['ownerID'],newUserBalance[user['ownerID']] + currentUser['balance'])
    

def update_order_balanced(orderID,side):
    TABLE.update_item(
        Key={
            'ownerID': orderID,
            'side': side,
        },
        UpdateExpression="SET balanced = :b",
        ConditionExpression="attribute_exists(orderID)",
        ExpressionAttributeValues={
            ':b': 1,
        },
        ReturnValues="NONE"
    )


def update_user_balance(ownerID,balance):
    BALANCE.update_item(
        Key={
            'ownerID': ownerID,
        },
        UpdateExpression="SET balance = :b",
        ConditionExpression="attribute_exists(ownerID)",
        ExpressionAttributeValues={
            ':b': balance,
        },
        ReturnValues="NONE"
    )

def write_to_order_book(order) -> None:

    TABLE.put_item(TableName="orders", Item=order)

def get_all_user_orders(ownerID):
    response = TABLE.query(
        IndexName="ownerID-userCollected-index",
        KeyConditionExpression=Key("ownerID").eq(ownerID),
    )
    if 'Items' in response:
        res = [{**i,'price':float(i['price']),'quantity':float(i['quantity']),'status':int(i['status'])} for i in response['Items']]
        return res
    else:
        return 0

def get_user(primaryKey):
    result = BALANCE.get_item(Key={'ownerID':primaryKey})
    if 'Item' in result:
        return result['Item']
    else:
        return 0

def get_uncollected_user_orders(ownerID):
    response = TABLE.query(
        IndexName="ownerID-userCollected-index",
        KeyConditionExpression=Key("ownerID").eq(ownerID) & Key("userCollected").eq(0),
    )
    if 'Items' in response:
        res = [{**i,'price':float(i['price']),'quantity':float(i['quantity']),'status':int(i['status'])} for i in response['Items']]
        return res
    else:
        return 0

def get_unbalanced_and_matched_orders():
    response = TABLE.query(
        IndexName="balanced-status-index",
        KeyConditionExpression=Key("balanced").eq(0) & Key("status").eq(1), #get all unbalanced and matched orders
    )
    if 'Items' in response:
        res = [{**i,'price':float(i['price']),'quantity':float(i['quantity']),'status':int(i['status'])} for i in response['Items']]
        return res
    else:
        return 0

# def edit_order(oprimary_key, order):
#     TABLE.update_item(TableName="orders", Key=oprimary_key, UpdateExpression=order)

def delete_order(primaryKey,sortKey):
    TABLE.delete_item(TableName="orders", Key={'orderID':primaryKey,'side':sortKey}, ConditionExpression="attribute_exists(orderID)")

def get_order(orderID):
    response = TABLE.get_item(Key={'orderID':orderID})
    if 'Item' in response:
        res = [{**i,'price':float(i['price']),'quantity':float(i['quantity']),'status':int(i['status'])} for i in response['Item']]
        return res
    else:
        return 0

def get_all_unmatched_orders():
    response = TABLE.query(
        IndexName="status-index",
        KeyConditionExpression=Key("status").eq(1),
    )
    if 'Items' in response:
        res = [{**i,'price':float(i['price']),'quantity':float(i['quantity']),'status':int(i['status'])} for i in response['Items']]
        return res
    else:
        return 0

def matching(in_order):
    in_order['orderID'] = str(uuid.uuid4())
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

                        # new child order
                        diff_buy["quantity"] -= order["quantity"]
                        diff_buy["split_link"] = diff_buy["orderID"]
                        diff_buy["orderID"] = str(uuid.uuid4())
                        
                        write_to_order_book(diff_buy)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

                        in_order = diff_buy.copy()
                        # in_order["orderID"] = str(
                        #     max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        # )
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
                        diff_sell["orderID"] = str(uuid.uuid4())
                        write_to_order_book(diff_sell)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

                    else:
                        # buy qt = sell qt
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        write_to_order_book(in_order)
                        write_to_order_book(order)

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
                        diff_buy["orderID"] = str(uuid.uuid4())
                        write_to_order_book(diff_buy)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

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
                        diff_sell["orderID"] = str(uuid.uuid4())

                        # child = diff_sell["split_link"]
                        write_to_order_book(diff_sell)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

                    else:
                        # buy qt = sell qt
                        in_order["match_link"] = order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        in_order["price"] = order["price"]

                        write_to_order_book(in_order)
                        write_to_order_book(order)
                else:
                    # buy order price < sell order
                    # if child is not None:
                    #     if in_order["split_link"] != child:
                    #         write_to_order_book(in_order)
                    # else:
                    if firstRun:
                        write_to_order_book(in_order)

            elif not in_isBuyOrder:
                # sell order
                if in_order["price"] == order["price"]:

                    if in_order["quantity"] > order["quantity"]:
                        # sell qt > buy qt -> sell split
                        diff_sell = in_order.copy()
                        in_order["quantity"] = order["quantity"]
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        # new child order
                        diff_sell["quantity"] -= order["quantity"]
                        diff_sell["split_link"] = diff_sell["orderID"]
                        diff_sell["orderID"] = str(
                            max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        )

                        # save split link id in child
                        # child = diff_sell["split_link"]

                        write_to_order_book(diff_sell)  #
                        write_to_order_book(in_order)  # replaces existing entry
                        write_to_order_book(order)  # replaces existing entry

                        in_order = diff_sell.copy()
                        # in_order["orderID"] = str(
                        #     max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        # )
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
                        diff_buy["orderID"] = str(uuid.uuid4())

                        # save split link id in child
                        # child = diff_buy["split_link"]

                        write_to_order_book(diff_buy)
                        write_to_order_book(order)
                        write_to_order_book(in_order)

                    else:
                        # buy qt = sell qt
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0

                        write_to_order_book(in_order)
                        write_to_order_book(order)

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
                        diff_sell["orderID"] = str(
                            max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        )

                        # save split link id in child
                        # child = diff_sell["split_link"]

                        write_to_order_book(diff_sell)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

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
                        diff_buy["orderID"] = str(uuid.uuid4())

                        # save split link id in child
                        # child = diff_buy["split_link"]

                        write_to_order_book(diff_buy)
                        write_to_order_book(in_order)
                        write_to_order_book(order)

                    else:
                        # buy qt = sell qt
                        order["match_link"] = in_order["orderID"]
                        order["status"], in_order["status"] = 0, 0
                        order["price"] = in_order["price"]

                        write_to_order_book(in_order)
                        write_to_order_book(order)

                else:
                    if firstRun:
                        write_to_order_book(in_order)
            firstRun = False


# lambda_handler("a", None)

# eventBuy = {"uid": 123, "side": "BUY", "type": "ROCK", "quantity": 10, "price": 1000}

#    {
#       "orderID": STR ----> PARTITION K
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
