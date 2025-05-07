from functools import reduce

import pandas as pd
import matplotlib.dates as mdates
import numpy as np
from matplotlib import pyplot as plt
plt.rcParams["figure.figsize"] = (20, 8)
from scipy.stats import norm

from fetch_data import load_timeseries, filter_timeseries

if __name__ == "__main__":
    all_df = []
    for data_type in ["huf", "ron", "pln", "czk"]:
        df = load_timeseries('D', data_type)
        df = filter_timeseries(df, ('2010-01-01', '2025-05-01'))
        all_df.append(df.drop(columns=["TIME PERIOD"]))

    merged_df = reduce(lambda left, right: pd.merge(left, right, on='datetime', how='outer'), all_df)
    merged_df = merged_df.sort_values("datetime").reset_index(drop=True)

    # Compute daily returns
    rates = merged_df[['EUR_HUF', 'EUR_RON', 'EUR_PLN', 'EUR_CZK']]
    rates.to_csv(f'currencies_raw.csv')
    rates.index = merged_df.datetime
    rates /= rates.iloc[1, :]
    rates['regional'] = rates[['EUR_RON', 'EUR_PLN', 'EUR_CZK']].mean(axis=1)
    rates['huf_relative'] = rates['EUR_HUF'] - rates['regional']
    rates.to_csv(f'currencies.csv')
    fig, ax = plt.subplots()
    rates['huf_relative'].plot(ax=ax)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Set minor ticks to months (no labels for these)
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    # Optional: Rotate the tick labels for better display
    fig.autofmt_xdate()
    plt.ylabel("EUR_HUF relative")
    plt.tight_layout()
    plt.gcf().savefig(f'EUR_HUF_relative.png')
    plt.close()
