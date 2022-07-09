from func_cointegration import extract_closes_prices
from func_cointegration import calculate_cointegration
from func_cointegration import calculate_spread
from func_cointegration import calculate_zscore
import matplotlib.pyplot as plt
import pandas as pd


# plot prices and trends
def analyse_pair(sym_1, sym_2, price_data, backtest_pair):

    # extract prices
    prices_1 = extract_closes_prices(price_data[sym_1])
    prices_2 = extract_closes_prices(price_data[sym_2])

    # get spread and zscores
    coint_flag, p_value, t_value, c_value, hedge_ratio, zero_crossing=calculate_cointegration(prices_1, prices_2)
    spread = calculate_spread(prices_1, prices_2, hedge_ratio)
    zscore = calculate_zscore(spread)

    # calculate percentage change
    df = pd.DataFrame(columns=[sym_1, sym_2])
    df[sym_1] = prices_1
    df[sym_2] = prices_2
    df[f"{sym_1}_pct"] = df[sym_1] / prices_1[0]
    df[f"{sym_2}_pct"] = df[sym_2] / prices_2[0]
    series_1 = df[f"{sym_1}_pct"].astype(float).values
    series_2 = df[f"{sym_2}_pct"].astype(float).values
    
    # save result for backtesting
    df_2 = pd.DataFrame()
    df_2[sym_1] = prices_1
    df_2[sym_2] = prices_2
    df_2["spread"] = spread
    df_2["zscore"] = zscore

    if is_skipped(df_2):
        return

    df_2.to_csv("Backtest/"+backtest_pair+"_backtest.csv")

    # plot charts
    fig, axs = plt.subplots(3, figsize=(16, 8))
    fig.suptitle(f"Price and Spread - {sym_1} vs {sym_2}")
    axs[0].plot(series_1)
    axs[0].plot(series_2)
    axs[1].plot(spread)
    axs[2].plot(zscore)
    plt.savefig(fname="Backtest/"+backtest_pair+"_backtest_fig.pdf", format="pdf")
    #plt.show()
    print(f"Backtesting file and fig for the pair {backtest_pair} saved.")


def is_skipped(pair_data):
    df_zscore_positive = pair_data.query('zscore > 0')
    df_zscore_negative = pair_data.query('zscore <= 0')
    df_spread_positive = pair_data.query('spread > 0')
    df_spread_negative = pair_data.query('spread <= 0')

    # if zscore doesn't change polarity at all, we don't need to further consider it
    if not (len(df_zscore_positive) > 0 and len(df_zscore_negative) > 0):
        print("zscore sign does not changed, the pair is skipped")
        return True

    if not (len(df_spread_positive) > 0 and len(df_spread_negative) > 0):
        print("spread sign does not changed, the pair is skipped")
        return True

    if not (len(df_zscore_positive)/len(df_zscore_negative) > 0.3 or len(df_zscore_negative)/len(df_zscore_positive) > 0.3):
        print("zscore reversal count is not balanced bewteen positive and negative, the pair is skipped")
        return True



    return False






