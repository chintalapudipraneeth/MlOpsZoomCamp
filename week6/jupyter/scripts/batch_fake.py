import sys
import pickle
import pandas as pd
import os


def read_data(filename: str) -> pd.DataFrame:
    """Read parquet data from filename."""
    df = pd.read_parquet(filename)
    return df


def prepare_data(df: pd.DataFrame, categorical: list) -> pd.DataFrame:
    """Transform dataframe and prepare for the forecasting"""
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


def main(filename: str) -> None:
    categorical = ['PULocationID', 'DOLocationID']

    df = read_data(filename=filename)
    df = prepare_data(df=df, categorical=categorical)
    df['ride_id'] = '2022/02_' + df.index.astype('str')

    with open('./model/model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    print('duration_sum:', df_result.predicted_duration.sum())

    return

if __name__ == "__main__":
    filename = sys.argv[1]
    main(filename=filename)
