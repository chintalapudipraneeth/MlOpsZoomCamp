import pandas as pd
from batch import save_data
from datetime import datetime


def dt(hour, minute, second: int = 0) -> datetime:
    return datetime(2022, 1, 1, hour, minute, second)


if __name__ == "__main__":
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2), dt(1, 10)),
        (1, 2, dt(2, 2), dt(2, 3)),
        (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    columns = [
        'PULocationID', 'DOLocationID',
        'tpep_pickup_datetime', 'tpep_dropoff_datetime'
    ]

    df = pd.DataFrame(data, columns=columns)
    save_data(df=df, output_path='./data/integration_file.parquet')
