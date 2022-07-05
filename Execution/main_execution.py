import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

from config_execution_api import signal_positive_ticker, signal_negative_ticker, session_public, buy_leverage, sell_leverage
from config_execution_api import ticker_1, ticker_2, rounding_ticker_1, rounding_ticker_2, quantity_rounding_ticker_1, quantity_rounding_ticker_2
from func_position_calls import open_position_confirmation, active_order_confirmation
from func_trade_management import manage_new_trade
from func_execution_calls import set_leverage
from func_close_position import close_all_positions
from func_zscore import get_latest_zscore, is_reversal_happened
from func_save_status import save_status
from Config.constant import *
import logging.config
import sys
import time

"""
STATBOT

This bot is based on the course material provided in https://www.udemy.com/course/triangular-arbitrage/, with the following modifications:

- WebSocket is not used: the websocket API of ByBit has been changed significantly since the course was published, for simplicity only REST is used
- Logic is revised a bit to fit my coding style and makes it more understandable

"""

if __name__ == "__main__":
    logging.basicConfig(filename="logfile.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Stat bot initiated...")

    status_dict = {"message": "starting..."}
    is_signal_sign_positive = False
    signal_side = ""
    kill_switch = KILL_SWITCH_CAN_DO_NEW_TRADE

    # save status
    save_status(status_dict)

    # set leverage
    logger.info("Setting buy leverage: {buy_leverage}x...".format(buy_leverage=buy_leverage))
    logger.info("Setting sell leverage: {sell_leverage}x...".format(sell_leverage=sell_leverage))
    set_leverage(signal_positive_ticker, buy_leverage, sell_leverage)
    set_leverage(signal_negative_ticker, buy_leverage, sell_leverage)

    ''' 
    TODO - automate the setup of rounding ticker    
    '''
    # commence bot
    logger.info("Seeking trades...")

    while True:

        # Check if non-zero open position is found for the positive ticker
        is_p_ticker_open = open_position_confirmation(signal_positive_ticker)

        # Check if non-zero open position is found for the negative ticker
        is_n_ticker_open = open_position_confirmation(signal_negative_ticker)

        # Check if active order is found for the positive ticker
        is_p_ticker_active = active_order_confirmation(signal_positive_ticker)

        # Check if active order is found for the nagative ticker
        is_n_ticker_active = active_order_confirmation(signal_negative_ticker)

        # put all checking into an array
        checks_all = [is_p_ticker_open, is_n_ticker_open, is_p_ticker_active, is_n_ticker_active]

        # can start new trades only if none of the above check is true
        can_start_new_trade = not any(checks_all)

        # save status
        status_dict["message"] = "Initial checks made..."
        status_dict["checks"] = checks_all
        save_status(status_dict)

        # check for signal and place new trades
        if can_start_new_trade and kill_switch == KILL_SWITCH_CAN_DO_NEW_TRADE:
            status_dict["message"] = "Managing new trades..."
            save_status(status_dict)
            # after manage_new_trade is returned, kill_switch must either be KILL_SWITCH_OPENED_POSITION or KILL_SWITCH_CLOSE_ORDER_POSITION
            kill_switch, signal_side = manage_new_trade(kill_switch)

        # Managing open kill switch if position change or should reach KILL_SWITCH_CLOSE_ORDER_POSITION
        # check for signal to be false when mean reversion is happened
        if kill_switch == KILL_SWITCH_OPENED_POSITION:
            if is_reversal_happened(ticker_1, ticker_2, signal_side):
                logger.info("zscore reversal happened, ready to close positions...")
                kill_switch = KILL_SWITCH_CLOSE_ORDER_POSITION

        # close all active order and positions
        if kill_switch == KILL_SWITCH_CLOSE_ORDER_POSITION:
            logger.info("Closing all positions...")
            status_dict["message"] = "Closing existing trades..."
            save_status(status_dict)
            kill_switch = close_all_positions(kill_switch)

        time.sleep(1)
