import pandas as pd
import pytest
from scripts.batch import prepare_data
from datetime import datetime


def dt(hour, minute, second: int = 0) -> datetime:
    return datetime(2022, 1, 1, hour, minute, second)


class TestPrepareData():
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

    expected_data = [
        ("-1", "-1", dt(1, 2), dt(1, 10),
            (dt(1, 10) - dt(1, 2)).total_seconds() / 60),
        ("1", "-1", dt(1, 2), dt(1, 10),
            (dt(1, 10) - dt(1, 2)).total_seconds() / 60),
        ("1", "2", dt(2, 2), dt(2, 3),
            (dt(2, 3) - dt(2, 2)).total_seconds() / 60),
        ("-1", "1", dt(1, 2, 0), dt(1, 2, 50),
            (dt(1, 2, 50) - dt(1, 2, 0)).total_seconds() / 60),
        ("2", "3", dt(1, 2, 0), dt(1, 2, 59),
            (dt(1, 2, 59) - dt(1, 2, 0)).total_seconds() / 60),
        ("3", "4", dt(1, 2, 0), dt(2, 2, 1),
            (dt(2, 2, 1) - dt(1, 2, 0)).total_seconds() / 60)
    ]
    expected = list(pd.DataFrame(
        expected_data[:3], columns=columns + ['duration']
    ))

    def test_prepare_data(self):
        actual = list(prepare_data(df=self.df, categorical=self.columns[:2]))
        assert actual == self.expected
