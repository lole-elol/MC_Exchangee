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


def test_matching_sell_price_diff():
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
            }
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
