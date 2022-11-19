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


def test_matching_buy_qt_diff():
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
                "match_link": "2",
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
