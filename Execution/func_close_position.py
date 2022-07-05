from config_execution_api import signal_positive_ticker, signal_negative_ticker, session_private
from Config.constant import *


# get position information
def get_position_info(ticker):
    side = ""
    size = 0

    # extract position info
    position = session_private.my_position(symbol=ticker)
    if "ret_msg" in position.keys():
        if position["ret_msg"] == "OK":
            if len(position["result"]) == 2:
                if position["result"][0]["size"] > 0:
                    size = position["result"][0]["size"]
                    side = ORDER_DIRECTION_BUY
                else:
                    size = position["result"][1]["size"]
                    side = ORDER_DIRECTION_SELL

    # return output
    return side, size


# place market close order
def place_market_close_order(ticker, side, size):
    # close position
    session_private.place_active_order(
        symbol=ticker,
        side=side,
        order_type=ORDER_TYPE_MARKET,
        qty=size,
        time_in_force="GoodTillCancel",
        reduce_only=True,
        close_on_trigger=False
    )

    return


# close all positions for both tickers
def close_all_positions(kill_switch):
    # cancel all active orders
    session_private.cancel_all_active_orders(symbol=signal_positive_ticker)
    session_private.cancel_all_active_orders(symbol=signal_negative_ticker)

    # get position info
    side_1, size_1 = get_position_info(signal_positive_ticker)
    side_2, size_2 = get_position_info(signal_negative_ticker)

    if size_1 > 0:
        # to close ticker_1, side = side_2 as it is the opposite
        place_market_close_order(signal_positive_ticker,
                                 ORDER_DIRECTION_BUY if side_1 == ORDER_DIRECTION_SELL else ORDER_DIRECTION_SELL,
                                 size_1)

    if size_2 > 0:
        # to close ticker_1, side = side_2 as it is the opposite
        place_market_close_order(signal_negative_ticker,
                                 ORDER_DIRECTION_BUY if side_2 == ORDER_DIRECTION_SELL else ORDER_DIRECTION_SELL,
                                 size_2)

    kill_switch = KILL_SWITCH_CAN_DO_NEW_TRADE

    return kill_switch
