import sys
import pickle
import pandas as pd
import os


storage_options = {
    'client_kwargs': {
        'endpoint_url': os.getenv('AWS_ENDPOINT_URL')
    }
}


def read_data(filename: str) -> pd.DataFrame:
    """Read parquet data from filename."""
    df = pd.read_parquet(filename)
    return df


def save_data(df: pd.DataFrame, output_path: str) -> None:
    df.to_parquet(
        output_path,
        engine='pyarrow',
        compression=None,
        index=False,
    )


def get_input_path(year, month: str):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year, month):
    default_output_pattern = './data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def prepare_data(df: pd.DataFrame, categorical: list) -> pd.DataFrame:
    """Transform dataframe and prepare for the forecasting"""
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


def main(year, month: int) -> None:
    input_file = get_input_path(year=year, month=month)
    output_file = get_output_path(year=year, month=month)
    categorical = ['PULocationID', 'DOLocationID']

    df = read_data(filename=input_file)
    df = prepare_data(df=df, categorical=categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    with open('./model/model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    df_result.to_parquet(output_file, engine='pyarrow', index=False)

    return

if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year=year, month=month)
