from typing import Tuple

import pandas as pd
import argparse
from datetime import datetime
from enum import Enum


class DataType(str, Enum):
    EUR_HUF = "huf"
    EUR_RON = "ron"
    EUR_PLN = "pln"
    EUR_CZK = "czk"
    BUX = "bux"
    VIX = "vix"


class Frequency(str, Enum):
    DAILY = "D"
    MINUTELY = "m"


def load_timeseries(frequency: Frequency, data_type: DataType) -> pd.DataFrame:
    prefix = ""
    csv_name = ""
    separator = ","

    match frequency:
        case Frequency.DAILY:
            prefix = "daily/"
            match data_type:
                case DataType.EUR_HUF:
                    csv_name = "ECB_EUR_HUF"
                case DataType.EUR_RON:
                    csv_name = "ECB_EUR_RON"
                case DataType.EUR_PLN:
                    csv_name = "ECB_EUR_PLN"
                case DataType.EUR_CZK:
                    csv_name = "ECB_EUR_CZK"
                case DataType.BUX:
                    csv_name = "BET_BUX"
                case DataType.VIX:
                    csv_name = "VIX"
        case Frequency.MINUTELY:
            prefix = "minutely/"
            match data_type:
                case DataType.EUR_HUF:
                    csv_name = "EUR_HUF_2025"
                    separator = ";"
                case _:
                    raise RuntimeError("dataset does not exist")

    csv_path = f"data/{prefix}{csv_name}.csv"
    df = pd.read_csv(csv_path, parse_dates=['datetime'], sep=separator)
    return df


def filter_timeseries(df: pd.DataFrame, interval: Tuple[datetime, datetime], jump: float) -> pd.DataFrame:

    start, end = pd.to_datetime(interval[0]), pd.to_datetime(interval[1])
    df = df[(df['datetime'] >= start) & (df['datetime'] <= end)].copy()

    if jump:
        if 'high' in df.columns:
            df['jump'] = df['high'] - df['low']
        else:
            df['jump'] = abs(df.iloc[:, 2].diff())
        df = df[(df['jump'] >= jump)]

    return df


def main():
    parser = argparse.ArgumentParser(description="Filter and resample time series data from a CSV file.")
    parser.add_argument("--data_type", help="e.g. bux, huf, pln, ron, czk, vix", required=True)
    parser.add_argument("--start_date", help="Start date (YYYY-MM-DD)", required=True)
    parser.add_argument("--end_date", help="End date (YYYY-MM-DD)", required=True)
    parser.add_argument("--frequency", help="daily or minute (e.g., D, m)", required=True)
    parser.add_argument("--min_jump", help="filter for jump between steps", required=False)

    args = parser.parse_args()
    df = load_timeseries(args.frequency, args.data_type)
    jump_size = None
    if args.min_jump:
        jump_size = float(args.min_jump)
    filtered_df = filter_timeseries(df=df, interval=(args.start_date, args.end_date), jump=jump_size)
    print(filtered_df.to_string(index=False))


if __name__ == "__main__":
    main()
