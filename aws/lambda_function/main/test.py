# import pytest

import app
from boto3.dynamodb.types import Decimal


def test_matching_sell_buy():
    # 1:1 match ( SELL -> BUY) (same price + qty)
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
    ]

    app.matching(order_in)
    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]

    # assert db_state == db_expected
    print("actual: ", db_state)
    print("expected: ", db_expected)


def test_matching_buy_sell():
    # 1:1 match (BUY -> SELL) (same price + qty)

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "2",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


############price different, qty same#######################
# 		- sell x, with price > x; buy with price < x
#     - buy price x -> sell price y < x --> match
#     - buy price x -> sell price y > x --> no match

#     - sell price x -> buy price y > x --> match
#     - sell price x -> buy price y < x --> no match


def test_matching_buy_price_diff_1_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "2",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_price_diff_2_no_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("30"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("30"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_price_diff_1_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_price_diff_2_no_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


############price different, qty different (INCLUDES SPLIT CASES)##########

# -  sell x qt y -> buy u > x qt v > y --> part_match
# -  sell x qt y -> buy u < x qt v < y --> no match

# -  sell x qt y -> buy u > x qt v < y --> part match
# -  sell x qt y -> buy u < x qt v > y --> no match


# -  buy x qt y -> sell u > x qt v > y --> no match
# -  buy x qt y -> sell u < x qt v < y --> part match

# -  buy x qt y -> sell u > x qt v < y --> no match
# -  buy x qt y -> sell u < x qt v > y --> part match


def test_matching_sell_price_qt_diff_1_part_match():

    # -  sell x qt y -> buy u > x qt v > y --> part_match

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "2",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_price_qt_diff_2_no_match():
    # -  sell x qt y -> buy u < x qt v < y --> no match

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_price_qt_diff_3_part_match():
    # -  sell x qt y -> buy u > x qt v < y --> part match

    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "3",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "1",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_price_qt_diff_4__no_match():
    # -  sell x qt y -> buy u < x qt v > y --> no match
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


########################################################


def test_matching_buy_price_qt_diff_1_no_match():
    # -  buy x qt y -> sell u > x qt v > y --> no match
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_price_qt_diff_2_part_match():
    # -  buy x qt y -> sell u < x qt v < y --> part match
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "2",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "1",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_price_qt_diff_3_no_match():
    # -  buy x qt y -> sell u > x qt v < y --> no match
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_price_qt_diff_4_part_match():
    # -  buy x qt y -> sell u < x qt v > y --> part match
    app.reset()

    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]

    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("10"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "2",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "3",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("10"),
            "status": Decimal("1"),
            "split_link": "2",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


###################### max stuff #############
# BUY perspective:

# - qty buy < qty sell √
# - qty buy > qty sell √
# - qty buy > qty sell -> partly fill √

# sell perspective:
# - qty buy < qty sell √
# - qty buy < qty sqll -> partly fill √
# - qty buy > qty sell √


def test_matching_sell_qt_diff_buy_smaller_partlyFilled():
    # qty buy < qty sqll & partly fill

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("17"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]
    app.init_db(db)

    order_in = {
        "orderID": "3",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "3",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("20"),
            "price": Decimal("17"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "4",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "2",
            "match_link": "",
        },
    ]

    app.matching(order_in)
    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_qt_diff_buy_smaller_allFilled():
    # qty buy < qty sqll -> all filled

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("15"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]
    app.init_db(db)

    order_in = {
        "orderID": "3",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "3",
        },
        {
            "orderID": "2",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "4",
        },
        {
            "orderID": "3",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "4",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "3",
            "match_link": "",
        },
        {
            "orderID": "5",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "2",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_sell_qt_diff_buy_bigger_allFilled():
    # - qty buy > qty sell

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("15"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        }
    ]
    app.init_db(db)

    order_in = {
        "orderID": "2",
        "side": "sell",
        "type": "wood",
        "quantity": Decimal("10"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "2",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "1",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


###
def test_matching_buy_qt_diff_buy_smaller_allFilled():
    # qty buy < qty sqll -> all filled

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("15"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]
    app.init_db(db)

    order_in = {
        "orderID": "3",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "4",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "3",
            "match_link": "2",
        },
        {
            "orderID": "5",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "2",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_qt_diff_buy_bigger_allFilled():
    # - qty buy > qty sell

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]
    app.init_db(db)

    order_in = {
        "orderID": "3",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("15"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "4",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "3",
            "match_link": "2",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]


def test_matching_buy_qt_diff_buy_bigger_partlyFilled():
    # - qty buy > qty sell -> partly fill

    app.reset()
    db = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "",
            "match_link": "",
        },
    ]
    app.init_db(db)

    order_in = {
        "orderID": "3",
        "side": "buy",
        "type": "wood",
        "quantity": Decimal("20"),
        "price": Decimal("20"),
        "status": Decimal("1"),
        "split_link": "",
        "match_link": "",
    }

    db_expected = [
        {
            "orderID": "1",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "2",
            "side": "sell",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "",
        },
        {
            "orderID": "3",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("10"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "",
            "match_link": "1",
        },
        {
            "orderID": "4",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("0"),
            "split_link": "3",
            "match_link": "2",
        },
        {
            "orderID": "5",
            "side": "buy",
            "type": "wood",
            "quantity": Decimal("5"),
            "price": Decimal("20"),
            "status": Decimal("1"),
            "split_link": "4",
            "match_link": "",
        },
    ]

    app.matching(order_in)

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]

    ###

    db_state = app.read_db()
    for el in db_expected:
        for el_a in db_state:
            if el["orderID"] == el_a["orderID"]:
                assert el["side"] == el_a["side"]
                assert el["type"] == el_a["type"]
                assert el["quantity"] == el_a["quantity"]
                assert el["price"] == el_a["price"]
                assert el["status"] == el_a["status"]
                assert el["split_link"] == el_a["split_link"]
                assert el["match_link"] == el_a["match_link"]
