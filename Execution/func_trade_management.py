from config_execution_api import ticker_1, ticker_2, signal_positive_ticker, signal_negative_ticker, \
    wait_min_for_market_order
from config_execution_api import signal_trigger_thresh, tradeable_capital_usdt
from config_execution_api import limit_order_basis, session_private
from config_execution_api import is_debug
from func_price_calls import get_ticker_trade_liquidity, get_ticker_trade_liquidity_vwap
from func_zscore import get_latest_zscore, is_zscore_sign_changed
from func_execution_calls import initialise_order_execution, cancel_order
from Config.constant import *
from func_order_review import check_order
from datetime import datetime
import time
import math


# manage new trade assessment
def manage_new_trade(kill_switch):
    # set variables
    order_long_id = ""
    order_short_id = ""
    signal_side = ""
    is_hot = False

    # Get and save the latest zscore
    zscore = get_latest_zscore(ticker_1, ticker_2)
    print(f"Checking zscore({ticker_1}, {ticker_2}): {zscore}")

    # switch to is_hot if meets signal threshold
    # Note: You can add in coint-flag check too if you want extra vigilance
    if abs(zscore) > signal_trigger_thresh:
        is_hot = True
        print(f"-- abs(zscore) > {signal_trigger_thresh}, Trade Status HOT --")
        print("-- Placing and Monitoring Existing Trades --")

    # Place and manage trades
    if is_hot and kill_switch == KILL_SWITCH_CAN_DO_NEW_TRADE:
        # get trades history for liquidity, and maximise the usage of available capital
        print(f"Checking liquidity for {signal_positive_ticker}...")
        # avg_liquidity_ticker_p, last_price_p = get_ticker_trade_liquidity(signal_positive_ticker)
        avg_liquidity_ticker_p, last_price_p = get_ticker_trade_liquidity_vwap(signal_positive_ticker)
        print(f"Checking liquidity for {signal_negative_ticker}...")
        # avg_liquidity_ticker_n, last_price_n = get_ticker_trade_liquidity(signal_negative_ticker)
        avg_liquidity_ticker_n, last_price_n = get_ticker_trade_liquidity_vwap(signal_negative_ticker)

        # Determine long ticker vs short ticker
        if zscore > 0:
            long_ticker = signal_positive_ticker
            short_ticker = signal_negative_ticker
            avg_liquidity_long = avg_liquidity_ticker_p
            avg_liquidity_short = avg_liquidity_ticker_n
            last_price_long = last_price_p
            last_price_short = last_price_n
        else:
            long_ticker = signal_negative_ticker
            short_ticker = signal_positive_ticker
            avg_liquidity_long = avg_liquidity_ticker_n
            avg_liquidity_short = avg_liquidity_ticker_p
            last_price_long = last_price_n
            last_price_short = last_price_p

        if is_debug:
            print(f"Tradeable_capital_usdt: {tradeable_capital_usdt}")

        # Fill target
        tradeable_capital_long = tradeable_capital_usdt * 0.5
        tradeable_capital_short = tradeable_capital_usdt - tradeable_capital_long
        initial_fill_target_long_usdt = math.floor(avg_liquidity_long * last_price_long)
        initial_fill_target_short_usdt = math.floor(avg_liquidity_short * last_price_short)

        # Use full integer for injection amount
        initial_capital_injection_usdt = min(initial_fill_target_long_usdt, initial_fill_target_short_usdt)

        if is_debug:
            print(f"initial_fill_target_long_usdt: {initial_fill_target_long_usdt}, "
                  f"initial_fill_target_short_usdt: {initial_fill_target_short_usdt}, "
                  f"initial_capital_injection_usdt: {initial_capital_injection_usdt} ")

        # Ensure initial capital does not exceed limits set in configuration
        if limit_order_basis:
            if initial_capital_injection_usdt > tradeable_capital_long:
                initial_capital_usdt = tradeable_capital_long
            else:
                # if the available capital can absorb the average liquidity, use it as the initial capital
                initial_capital_usdt = initial_capital_injection_usdt
        else:
            initial_capital_usdt = tradeable_capital_long

        # Initialize the remaining capital
        remaining_capital_long = tradeable_capital_long
        remaining_capital_short = tradeable_capital_short

        if is_debug:
            print(
                f"remaining_capital_long:{remaining_capital_long}, remaining_capital_short:{remaining_capital_short}, initial_capital_usdt:{initial_capital_usdt}")

        # trade until filled or signal is false
        order_status_long = ""
        order_status_short = ""
        counts_long = 0
        counts_short = 0

        while kill_switch == KILL_SWITCH_CAN_DO_NEW_TRADE:

            # place an order - long
            if counts_long == 0:
                order_long_id = initialise_order_execution(long_ticker, ORDER_DIRECTION_LONG, initial_capital_usdt, limit_order_basis)
                if order_long_id:
                    counts_long = 1
                    long_order_time = datetime.now()
                remaining_capital_long = remaining_capital_long - initial_capital_usdt

            # place an order - short
            if counts_short == 0:
                order_short_id = initialise_order_execution(short_ticker, ORDER_DIRECTION_SHORT, initial_capital_usdt, limit_order_basis)
                if order_short_id:
                    counts_short = 1
                    short_order_time = datetime.now()
                remaining_capital_short = remaining_capital_short - initial_capital_usdt

            # update signal side
            if zscore > 0:
                signal_side = SIGNAL_SIDE_POSITIVE
            else:
                signal_side = SIGNAL_SIDE_NEGATIVE

            # Handle kill switch for market orders
            if not limit_order_basis and counts_short and counts_short:
                kill_switch = KILL_SWITCH_OPENED_POSITION

            # allow for time to register the limit orders
            time.sleep(3)

            # Check limit orders and ensure z_score is still within range
            zscore_new = get_latest_zscore(ticker_1, ticker_2)

            if kill_switch == KILL_SWITCH_CAN_DO_NEW_TRADE:
                # Final checking on zscore
                if abs(zscore_new) > signal_trigger_thresh * 0.95 and not is_zscore_sign_changed(zscore, zscore_new):

                    # check long order status
                    if counts_long == 1:
                        order_status_long = check_order(long_ticker, order_long_id, remaining_capital_long, ORDER_DIRECTION_LONG)

                    # check short order status
                    if counts_short == 1:
                        order_status_short = check_order(short_ticker, order_short_id, remaining_capital_short, ORDER_DIRECTION_SHORT)

                    # if long order done but short order pending and already pass 3 mins, execute market order
                    if order_status_long == ORDER_STATUS_POSITION_FILLED and \
                            (order_status_short == ORDER_STATUS_ACTIVE or order_status_short == ORDER_STATUS_PARTIAL_FILL):
                        time_diff = datetime.now() - long_order_time
                        if (time_diff.seconds/60) > wait_min_for_market_order:
                            print(f"Long order filled but short order still active after {wait_min_for_market_order} mins, use market order for short position instead...")
                            if cancel_order(short_ticker, order_short_id):
                                order_short_id = initialise_order_execution(short_ticker, ORDER_DIRECTION_SHORT,
                                                                            initial_capital_usdt, is_limit_order=False)
                                time.sleep(1)
                                order_status_short = check_order(short_ticker, order_short_id, remaining_capital_short,
                                                                 ORDER_DIRECTION_SHORT)

                    # if short order done but long order pending and already pass 3 mins, execute market order
                    if order_status_short == ORDER_STATUS_POSITION_FILLED and \
                            (order_status_long == ORDER_STATUS_ACTIVE or order_status_long == ORDER_STATUS_PARTIAL_FILL):
                        time_diff = datetime.now() - short_order_time
                        if (time_diff.seconds/60) > wait_min_for_market_order:
                            print(f"Short order filled but long order still active after {wait_min_for_market_order} mins, use market order for long position instead...")
                            if cancel_order(long_ticker, order_long_id):
                                order_long_id = initialise_order_execution(long_ticker, ORDER_DIRECTION_LONG,
                                                                            initial_capital_usdt, is_limit_order=False)
                                time.sleep(1)
                                order_status_long = check_order(long_ticker, order_long_id, remaining_capital_short,
                                                                 ORDER_DIRECTION_LONG)

                    # if order still active, do nothing
                    if order_status_long == ORDER_STATUS_ACTIVE or order_status_short == ORDER_STATUS_ACTIVE:
                        continue

                    # if order partially filled, do nothing
                    if order_status_long == ORDER_STATUS_PARTIAL_FILL or order_status_short == ORDER_STATUS_PARTIAL_FILL:
                        continue

                    # if position filled - place another trade
                    if order_status_long == ORDER_STATUS_POSITION_FILLED and order_status_short == ORDER_STATUS_POSITION_FILLED:
                        if remaining_capital_long <= initial_capital_usdt or remaining_capital_short <= initial_capital_usdt:
                            print("Trade completed, long and short positions established")
                            kill_switch = KILL_SWITCH_OPENED_POSITION
                        else:
                            print("Positions are filled, start another pair of trade")
                            if is_debug:
                                print(
                                    f"remaining_capital_long:{remaining_capital_long}, remaining_capital_short:{remaining_capital_short}, initial_capital_usdt:{initial_capital_usdt}")
                            counts_long = 0
                            counts_short = 0

                    # if order cancelled for long, try again
                    if order_status_long == ORDER_STATUS_TRY_AGAIN:
                        print("Long order failed, retrying...")
                        counts_long = 0

                    # if order cancelled for short, try again
                    if order_status_short == ORDER_STATUS_TRY_AGAIN:
                        print("Short order failed, retrying...")
                        counts_short = 0

                else:

                    # Cancel all active orders if zscore check is failed
                    session_private.cancel_all_active_orders(symbol=signal_positive_ticker)
                    session_private.cancel_all_active_orders(symbol=signal_negative_ticker)
                    kill_switch = KILL_SWITCH_CLOSE_ORDER_POSITION

    # output status
    return kill_switch, signal_side
