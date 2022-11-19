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
        # print("response: ", response)

        # match = True
        ### while match:

        # for order in response
        # ........
        # match case -> tempdb.append
        # non match case -> match = False

        #### Optimise matching ###

        # sort temp tmpdb
        child = None
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
                        diff_buy["orderID"] = str(
                            max(int(diff_buy["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later + remove max
                        # child = diff_buy["split_link"]
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
                        diff_sell["orderID"] = str(
                            max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later

                        # child = diff_sell["split_link"]
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
                        diff_buy["orderID"] = str(
                            max(int(diff_buy["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later + remove max

                        # child = diff_buy["split_link"]
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
                        diff_sell["orderID"] = str(
                            max(int(diff_sell["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later

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
                        diff_buy["orderID"] = str(
                            max(int(diff_buy["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later

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
                        diff_buy["orderID"] = str(
                            max(int(diff_buy["orderID"]), int(in_order["orderID"])) + 1
                        )  # TODO change to uid later

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

eventBuy = {"uid": 123, "side": "BUY", "type": "ROCK", "quantity": 10, "price": 1000}

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
