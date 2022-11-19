# import pytest

import app


def test_matching_sell_buy():
    # 1:1 match ( SELL -> BUY) (same price + qty)    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "1",
        "side": "buy",
        "type": "wood",
        "quantity": "10",
        "price": "10",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "1",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_buy_sell():
    # 1:1 match (BUY -> SELL) (same price + qty)

    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "sell",
        "type": "wood",
        "quantity": "10",
        "price": "10",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "2",
            },
            {
                "uid": "2",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


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

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "sell",
        "type": "wood",
        "quantity": "10",
        "price": "10",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "2",
            },
            {
                "uid": "2",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_buy_price_diff_2_no_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "sell",
        "type": "wood",
        "quantity": "10",
        "price": "30",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "30",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_sell_price_diff_1_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "buy",
        "type": "wood",
        "quantity": "10",
        "price": "20",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "1",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_sell_price_diff_2_no_match():
    # price different, qty same
    # sell x, with price > x

    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "buy",
        "type": "wood",
        "quantity": "10",
        "price": "10",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected

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

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "buy",
        "type": "wood",
        "quantity": "20",
        "price": "20",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
             {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "1",
            },
            {
                "uid": "3",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "2",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_sell_price_qt_diff_2_no_match():

def test_matching_sell_price_qt_diff_3_part_match():

def test_matching_sell_price_qt_diff_4__no_match():


def test_matching_buy_price_qt_diff_1_no_match():

def test_matching_buy_price_qt_diff_2_part_match():

def test_matching_buy_price_qt_diff_3_no_match():

def test_matching_buy_price_qt_diff_4_part_match():


###################### max stuff #############
# BUY perspective:

# - qty buy < qty sell
# - qty buy < qty sqll & partly fill
# - qty buy > qty sell
# - qty buy > qty sell & partly fill

# sell perspective:
# - qty buy < qty sell
# - qty buy < qty sqll & partly fill
# - qty buy > qty sell
# - qty buy > qty sell & partly fill


def test_matching_sell_qt_diff_buy_smaller_partlyFilled():
    # qty buy < qty sqll -> partly fill

    app.reset()
    db = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "20",
                "price": "17",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }
    app.init_db(db)

    order_in = {
        "uid": "3",
        "side": "sell",
        "type": "wood",
        "quantity": "20",
        "price": "20",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": False,
                "split_link": "",
                "match_link": "3",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "20",
                "price": "17",
                "status": True,
                "split_link": "4",
                "match_link": "",
            },
            {
                "uid": "3",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "4",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "2",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)
    assert app.read_db() == db_expected


def test_matching_sell_qt_diff_buy_smaller_allFilled():
    # qty buy < qty sqll -> partly fill

    app.reset()
    db = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "15",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }
    app.init_db(db)

    order_in = {
        "uid": "3",
        "side": "sell",
        "type": "wood",
        "quantity": "20",
        "price": "20",
        "quantity": "10",
        "price": "20",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "2",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)

    assert app.read_db() == db_expected


def test_matching_buy_qt_price_diff():
    # price different, qty different
    # sell x, with buy price > x

    app.reset()

    db = {
        "orders": [
            {
                "uid": "1",
                "side": "sell",
                "type": "wood",
                "quantity": "100",
                "price": "10",
                "status": True,
                "split_link": "",
                "match_link": "",
            },
        ]
    }

    app.init_db(db)

    order_in = {
        "uid": "2",
        "side": "buy",
        "type": "wood",
        "quantity": "10",
        "price": "20",
        "status": True,
        "split_link": "",
        "match_link": "",
    }

    db_expected = {
        "orders": [
            {
                "uid": "1",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "10",
                "status": False,
                "split_link": "",
                "match_link": "2",
            },
            {
                "uid": "2",
                "side": "buy",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": False,
                "split_link": "",
                "match_link": "4",
            },
            {
                "uid": "3",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "price": "5",
                "status": False,
                "split_link": "",
                "match_link": "",
            },
            {
                "uid": "3",
                "side": "sell",
                "type": "wood",
                "quantity": "90",
                "price": "5",
                "status": True,
                "split_link": "2",
                "match_link": "",
            },
            {
                "uid": "4",
                "side": "sell",
                "type": "wood",
                "quantity": "10",
                "price": "20",
                "status": False,
                "split_link": "3",
                "match_link": "",
            },
            {
                "uid": "5",
                "side": "buy",
                "type": "wood",
                "quantity": "5",
                "price": "20",
                "status": True,
                "split_link": "2",
                "match_link": "",
            },
        ]
    }

    app.matching(order_in)
    assert app.read_db() == db_expected
