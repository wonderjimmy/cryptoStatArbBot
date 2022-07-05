from config_execution_api import session_private
from Config.constant import *

# check for open position
def open_position_confirmation(ticker):
    try:
        position = session_private.my_position(symbol=ticker)
        if position["ret_msg"] == "OK":
            for item in position["result"]:
                if item["size"] > 0:
                    return True
    except:
        return True
    return False

# check for active position
def active_order_confirmation(ticker):
    try:
        active_order = session_private.get_active_order(
            symbol=ticker,
            order_status="Created,New,PartiallyFilled,Active"
        )
        if active_order["ret_msg"] == "OK":
            if active_order["result"]["data"] != None:
                return True
    except:
        return True
    return False


# get open position price and quantity
def get_open_position(ticker, direction=ORDER_DIRECTION_LONG):

    position = session_private.my_position(symbol=ticker)

    # select index to avoid looping through response
    index = 0 if direction == ORDER_DIRECTION_LONG else 1

    # construct a response
    if "ret_msg" in position.keys():
        if position["ret_msg"] == "OK":
            if "symbol" in position["result"][index].keys():
                position_price = position["result"][index]["entry_price"]
                position_quantity = position["result"][index]["size"]
                position_value = position["result"][index]["position_value"]
                return position_price, position_quantity, position_value
            return 0, 0
    return 0, 0


# get active position price and quantity
def get_active_order(ticker):

    active_order = session_private.get_active_order(
        symbol=ticker,
        order_status=ACTIVE_ORDER_STATUS
    )

    # construct a response
    if "ret_msg" in active_order.keys():
        if active_order["ret_msg"] == "OK":
            if active_order["result"]["data"] != None:
                order_price = active_order["result"]["data"][0]["price"]
                order_quantity = active_order["result"]["data"][0]["qty"]
                return order_price, order_quantity
            return 0, 0
    return 0, 0


# query existing order
def query_existing_order(ticker, order_id):

    order = session_private.query_active_order(symbol=ticker, order_id=order_id)

    if "ret_msg" in order.keys():
        if order["ret_msg"] == "OK":
            order_price = order["result"]["price"]
            order_quantity = order["result"]["qty"]
            order_status = order["result"]["order_status"]
            return order_price, order_quantity, order_status
    return 0, 0, 0





