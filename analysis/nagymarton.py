from functools import reduce

import pandas as pd
from matplotlib import pyplot as plt

from fetch_data import load_timeseries, filter_timeseries

if __name__ == "__main__":
    all_df = []
    for data_type in ["huf", "ron", "pln", "czk",]:
        df = load_timeseries('D', data_type)
        df = filter_timeseries(df, ('2022-05-01', '2025-05-01'))
        all_df.append(df.drop(columns=["TIME PERIOD"]))
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='datetime', how='outer'), all_df)
    rates = merged_df[['EUR_HUF', 'EUR_RON', 'EUR_PLN', 'EUR_CZK']].pct_change()
    rolling_corrs = pd.DataFrame(index=merged_df.index)
    for col in ['EUR_RON', 'EUR_PLN', 'EUR_CZK']:
        rolling_corrs[col] = rates['EUR_HUF'].rolling(3, center=True).corr(merged_df[col])
    rolling_similarity = rolling_corrs.mean(axis=1)
    rolling_similarity.index = pd.to_datetime(merged_df.datetime)
    rolling_similarity.plot()
    plt.gcf().savefig('nagymarton.png')