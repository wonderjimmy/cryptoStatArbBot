from Config.constant import *
from Execution.func_position_calls import query_existing_order
from config_execution_api import session_private, limit_order_basis, session_public
from config_ws_connect import ws_public
from func_calculations import get_trade_details
from func_order_book import get_order_book
from time import sleep

global __ORDER_COUNT__


# set leverage
def set_leverage(ticker, buy_leverage, sell_leverage):

    # setting the leverage

    try :
        leverage_set = session_private.cross_isolated_margin_switch(
            symbol=ticker,
            is_isolated=True,
            buy_leverage=buy_leverage,
            sell_leverage=sell_leverage
        )
    except Exception as e:
        pass

    return


# place limit or market order
def place_order(ticker, price, quantity, direction, stop_loss, is_limit_order):

    # set variables
    if direction == ORDER_DIRECTION_LONG:
        side = ORDER_DIRECTION_BUY
    else:
        side = ORDER_DIRECTION_SELL

    reduce_only = False

    # place limit order
    if is_limit_order:
        order = session_private.place_active_order(
            symbol=ticker,
            side=side,
            order_type=ORDER_TYPE_LIMIT,
            qty=quantity,
            price=price,
            time_in_force=ORDER_TIF_POST_ONLY,
            reduce_only=reduce_only,
            close_on_trigger=False,
            stop_loss=stop_loss
        )
    else:
        order = session_private.place_active_order(
            symbol=ticker,
            side=side,
            order_type=ORDER_TYPE_MARKET,
            qty=quantity,
            time_in_force=ORDER_TIF_GOOD_TILL_CANCEL,
            reduce_only=reduce_only,
            close_on_trigger=False,
            stop_loss=stop_loss
        )

    return order


# Initialise execution
def initialise_order_execution(ticker, direction, capital, is_limit_order):
    orderbook = get_order_book(ticker)
    if orderbook:
        mid_price, stop_loss, quantity = get_trade_details(orderbook, direction, capital)
        if quantity > 0:
            order = place_order(ticker, mid_price, quantity, direction, stop_loss, is_limit_order)
            if "result" in order.keys():
                if "order_id" in order["result"]:
                    return order["result"]["order_id"]
    return 0


def cancel_order(ticker, old_order_id):
    
    try :
        result = session_private.cancel_active_order(symbol=ticker, order_id=old_order_id)
        if result["ret_msg"] == "OK":
            print(f"{ticker} Order {old_order_id} cancelled successfully")
            return True
    except Exception as e:
        print(f"{ticker} Order {old_order_id} cannot be cancelled!")
        return False


####################
