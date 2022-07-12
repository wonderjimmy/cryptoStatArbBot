import math
from config_strategy_api import z_score_window
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import pandas as pd
import numpy as np
from config_strategy_api import cointegrated_pairs_file_name


# calcualte z-score
def calculate_zscore(spread):
    df = pd.DataFrame(spread)
    mean = df.rolling(center=False, window=z_score_window).mean()
    std = df.rolling(center=False, window=z_score_window).std()
    x = df.rolling(center=False, window=1).mean()
    df["ZSCORE"] = (x * mean) / std
    return df["ZSCORE"].astype(float).values


# Calculate spread
def calculate_spread(series_1, series_2, hedge_ratio):
    spread = pd.Series(series_1) - (pd.Series(series_2) * hedge_ratio)
    return spread


# Calculate cointegration
def calculate_cointegration(series_1, series_2):
    coint_flag = 0
    coint_res = coint(series_1, series_2)
    coint_t = coint_res[0]
    p_value = coint_res[1]
    critical_value = coint_res[2][1]
    model = sm.OLS(series_1, series_2).fit()
    hedge_ratio = model.params[0]
    spread = calculate_spread(series_1, series_2, hedge_ratio)
    zero_crossing = len(np.where(np.diff(np.sign(spread)))[0])
    if p_value < 0.5 and coint_t < critical_value:
        coint_flag = 1
    return (
    coint_flag, round(p_value, 2), round(coint_t, 2), round(critical_value, 2), round(hedge_ratio, 2), zero_crossing)


# put close prices into a list
def extract_closes_prices(prices):
    close_prices = []
    for price_values in prices:
        if math.isnan(price_values["close"]):
            return []
        close_prices.append(price_values["close"])
    # print(close_prices)
    return close_prices


# Calculate cointegrated pairs
def get_cointegrated_pairs(prices):
    # loop coins and check for cointegration
    coint_pair_list = []
    included_list = []

    for sym_1 in prices.keys():
        # check each coin against sym_1
        for sym_2 in prices.keys():
            if sym_2 != sym_1:
                # print(sym_1, sym_2)
                # get unique combination
                sorted_characters = sorted(sym_1 + sym_2)
                unique = "".join(sorted_characters)
                if unique in included_list:
                    break

                # get closed prices
                series_1 = extract_closes_prices(prices[sym_1])
                series_2 = extract_closes_prices(prices[sym_2])

                # check for cointegration
                coint_flag, p_value, t_value, c_value, hedge_ratio, zero_crossing = calculate_cointegration(series_1,
                                                                                                            series_2)
                if coint_flag == 1:
                    included_list.append(unique)
                    coint_pair_list.append({
                        "sym_1": sym_1,
                        "sym_2": sym_2,
                        "p_value": p_value,
                        "t_value": t_value,
                        "c_value": c_value,
                        "hedge_ratio": hedge_ratio,
                        "zero_crossing": zero_crossing
                    })

    # output results
    df_coint = pd.DataFrame(coint_pair_list)
    #df_coint = df_coint.sort_values("zero_crossing", ascending=False)
    df_coint = df_coint.sort_values("p_value", ascending=True)
    df_coint.to_csv(cointegrated_pairs_file_name)
    return df_coint
