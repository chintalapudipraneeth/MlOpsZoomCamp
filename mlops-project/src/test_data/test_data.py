"""Module to get data to send and test api to predict fungus
"""

import os

import click
import pandas as pd
import requests as reqs  # type: ignore
from pandarallel import pandarallel

pandarallel.initialize(progress_bar=True, nb_workers=1)
replace = {
    'bruises': {'f': 'No Bruises', 't': 'Bruises'},
    'cap-color': {
        'b': 'buff',
        'c': 'cinnamon',
        'e': 'red',
        'g': 'green',  # using a happy pack original is gray #TODO
        'n': 'brown',
        'p': 'pink',
        'r': 'green',
        'u': 'purple',
        'w': 'white',
        'y': 'yellow',
    },
    'cap-shape': {
        'b': 'bell',
        'c': 'c',
        'f': 'flat',
        'k': 'knobbed',
        's': 'sunken',
        'x': 'convex',
    },
    'cap-surface': {
        'f': 'fibrous',
        'g': 'grooves',
        's': 'smooth',
        'y': 'scaly',
    },
    'gill-attachment': {
        'a': 'attached',
        'd': 'descending',
        'f': 'free',
        'n': 'notched',
    },
    'gill-color': {
        'b': 'buff',
        'e': 'red',
        'g': 'gray',
        'h': 'chocolate',
        'k': 'black',
        'n': 'brown',
        'o': 'orange',
        'p': 'pink',
        'r': 'green',
        'u': 'purple',
        'w': 'white',
        'y': 'yellow',
    },
    'gill-size': {'b': 'broad', 'n': 'narrow'},
    'gill-spacing': {'c': 'close', 'd': 'distant', 'w': 'crowded'},
    'habitat': {
        'd': 'wood',
        'g': 'grasses',
        'l': 'leaves',
        'm': 'meadows',
        'p': 'paths',
        'u': 'urban',
        'w': 'waste',
    },
    'odor': {
        'a': 'almond',
        'c': 'creosote',
        'f': 'foul',
        'l': 'anise',
        'm': 'musty',
        'n': 'none',
        'p': 'pungent',
        's': 'spicy',
        'y': 'fishy',
    },
    'population': {
        'a': 'abundant',
        'c': 'clustered',
        'n': 'numerous',
        's': 'scattered',
        'v': 'several',
        'y': 'solitary',
    },
    'ring-number': {'n': 'none', 'o': 'one', 't': 'two'},
    'ring-type': {
        'c': 'cobwebby',
        'e': 'evanescent',
        'f': 'flaring',
        'l': 'large',
        'n': 'none',
        'p': 'pendant',
        's': 'sheathing',
        'z': 'zone',
    },
    'spore-print-color': {
        'b': 'buff',
        'h': 'chocolate',
        'k': 'black',
        'n': 'brown',
        'o': 'orange',
        'r': 'green',
        'u': 'purple',
        'w': 'white',
        'y': 'yellow',
    },
    'stalk-color-above-ring': {
        'b': 'buff',
        'c': 'cinnamon',
        'e': 'red',
        'g': 'gray',
        'n': 'brown',
        'o': 'orange',
        'p': 'pink',
        'w': 'white',
        'y': 'yellow',
    },
    'stalk-color-below-ring': {
        'b': 'buff',
        'c': 'cinnamon',
        'e': 'red',
        'g': 'gray',
        'n': 'brown',
        'o': 'orange',
        'p': 'pink',
        'w': 'white',
        'y': 'yellow',
    },
    'stalk-root': {
        '?': 'missing',
        'b': 'bulbous',
        'c': 'club',
        'e': 'equal',
        'r': 'rooted',
        'u': 'cup',
        'z': 'rhizomorphs',
    },
    'stalk-shape': {'e': 'enlarging', 't': 'tapering'},
    'stalk-surface-above-ring': {
        'f': 'fibrous',
        'k': 'silky',
        's': 'smooth',
        'y': 'scaly',
    },
    'stalk-surface-below-ring': {
        'f': 'fibrous',
        'k': 'silky',
        's': 'smooth',
        'y': 'scaly',
    },
    'veil-color': {'n': 'brown', 'o': 'orange', 'w': 'white', 'y': 'yellow'},
    'veil-type': {'p': 'partial', 'u': 'universal'},
}


def send_data(value):
    """Function to send data to api prediction using pandas

    Args:
        value (pandas.Series): data to send api predict
    """
    dict_json = value.to_dict()
    dict_json.pop("class")
    url_service = dict_json.pop("url_service")
    url = f'http://{url_service}/api/predict'
    req = reqs.post(url, json=dict_json)

    if req.status_code == 400:
        click.echo(value)
        click.echo(req)
        click.echo(req.json())


@click.command()
@click.pass_context
@click.option(
    "-i",
    "--input-filepath",
    type=click.Path(exists=True),
    default="data/raw/",
)
@click.option("-f", "--file", default="mushrooms.csv")
@click.option(
    "-r", "--rerefence-file", default="data/processed/pre_features.parquet"
)
def test_data(ctx, input_filepath, file, reference_file):
    """Command to test data in grafana

    Args:
        ctx (object): is context to use in all cli with multiple confs
        input_filepath (str): path to get dataframe to send data
        file (str): name of file to get data and send
        reference_file (str): reference file to get only necessaries
            fields
    """
    url_service = ctx.obj.get("PREDICT_SERVICE_URL", "localhost:8000")
    df_ref = pd.read_parquet(reference_file)
    df = pd.read_csv(os.path.join(input_filepath, file))
    # print(df.head())

    for key, value in replace.items():
        value = {k: v.capitalize() for k, v in value.items()}
        df[key] = df[key].str.strip()
        df[key].replace(value, inplace=True)

    needs_columns = df_ref.columns.tolist()
    df = df[needs_columns]
    df["url_service"] = url_service
    # print(df.head())
    # print(df_ref.head())
    # print(df.columns.tolist())
    # print(df_ref.columns.tolist())

    df.parallel_apply(send_data, axis=1)


if __name__ == "__main__":
    test_data()
