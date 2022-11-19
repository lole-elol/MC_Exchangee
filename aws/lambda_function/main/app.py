import json

# import requests


def lambda_handler(event, context):

    if event:
        # write_to_order_book(event)
        pass

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }


def write_to_order_book(event):
    pass


def edit_order():
    pass


def matching():
    order = {}

    write_to_order_book(order)


lambda_handler("a", None)
