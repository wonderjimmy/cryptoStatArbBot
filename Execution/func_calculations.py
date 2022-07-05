from config_execution_api import stop_loss_fail_safe, ticker_1, ticker_2, rounding_ticker_1, rounding_ticker_2, quantity_rounding_ticker_1, quantity_rounding_ticker_2
from Config.constant import *
import math


# Puts all close prices in a list
def extract_close_prices(prices):
    close_prices = []
    for price_values in prices:
        if math.isnan(price_values["close"]):
            return []
        close_prices.append(price_values["close"])
    return close_prices


# get trade details and latest prices
def get_trade_details(orderbook, direction=ORDER_DIRECTION_LONG, capital=0):

    # set the calculation output variables
    price_rounding = 0
    quantity_rounding = 0
    mid_price = 0
    quantity = 0
    stop_loss = 0
    bid_items_list = []
    ask_items_list = []

    # get prices, stop loss and quantity
    if orderbook:
        # set price rounding
        price_rounding = rounding_ticker_1 if orderbook[0]["symbol"] == ticker_1 else rounding_ticker_2
        quantity_rounding = quantity_rounding_ticker_2 if orderbook[0]["symbol"] == ticker_1 else quantity_rounding_ticker_2

        # organize prices
        for level in orderbook:
            if level["side"] == ORDER_DIRECTION_BUY:
                bid_items_list.append(float(level["price"]))
            else:
                ask_items_list.append(float(level["price"]))

        # calculate price, size, stop loss and average liquidity
        if len(ask_items_list) > 0 and len(bid_items_list) > 0:

            # sort the list
            ask_items_list.sort()
            bid_items_list.sort()
            bid_items_list.reverse()

            # get nearest ask, nearest bid and orderbook spread
            nearest_ask = ask_items_list[0]
            nearest_bid = bid_items_list[0]

            # calculate hard stop loss
            if direction == ORDER_DIRECTION_LONG:
                # mid_price = (nearest_ask + nearest_bid)/2
                # placing at bid has higher probability of not being cancelled, but may not fill
                mid_price = nearest_bid
                stop_loss = round(mid_price * (1 - stop_loss_fail_safe), price_rounding)
            else:
                mid_price = nearest_ask
                stop_loss = round(mid_price * (1 + stop_loss_fail_safe), price_rounding)

            # calculate the quantity
            quantity = round(capital / mid_price, quantity_rounding)

    # output the result
    return mid_price, stop_loss, quantity
