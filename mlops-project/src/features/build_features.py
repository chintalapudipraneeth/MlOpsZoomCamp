# -*- coding: utf-8 -*-
"""Module to create features of the models
"""

import os
import warnings

import click
import pandas as pd
from prefect import task
from sklearn.model_selection import train_test_split

from utils.utils import NAMES, init_logger, save_features

warnings.filterwarnings("ignore")


@click.command()
@click.pass_context
@click.option(
    "-i",
    "--input-filepath",
    type=click.Path(exists=True),
    default="data/processed/",
)
@click.option(
    "-o", "--output-pickle", type=click.Path(), default="data/features/"
)
def build_features(ctx, input_filepath, output_pickle):
    """This command is to create features of dataset, and change values
    for other, for example 'class' to 1 or 0

    Keyword arguments:
    -i/--input-filepath -- folder where read the files
    -o/--output-filepath -- folder where save the file
    Return: None
    """
    __build_features(ctx, input_filepath, output_pickle)


@task
def build_features_prefect(
    ctx, input_filepath, output_pickle, storage_options
):
    """This is a task to create the features of dataset

    Args:
        ctx (dict): configurations of module
        input_filepath (str): filepath of file to transform
        output_pickle (str): output of features
        storage_options (dict): dictionary to config client of boto in
        pandas
    """
    __build_features(
        ctx, input_filepath, output_pickle, storage_options, 'prefect'
    )


def __build_features(
    ctx, input_filepath, output_pickle, storage_options=None, type_logger=None
):
    logger = init_logger(ctx.obj["DEBUG"], type_logger)
    # pylint: disable=C0103
    df = pd.read_parquet(
        os.path.join(input_filepath, "pre_features.parquet"),
        storage_options=storage_options,
    )

    logger.warning("transform variables")
    for column in df:
        if column == "class":
            df[column] = df[column].apply(
                lambda x: 1 if x == "Poisonous" else 0
            )
            continue

        uniques = df[column].unique().tolist()
        for unique in uniques:
            # pylint: disable=W0640
            df[f"{column}_{unique}"] = df[column].apply(
                lambda x: 1 if x == unique else 0
            )

        df.drop(column, axis=1, inplace=True)

    df.to_parquet('reference_df.parquet', index=False)
    logger.info('Get "X" and "y" to train model')
    X = df.iloc[:, 1:]  # pylint: disable=C0103
    y = df["class"]  # pylint: disable=C0103

    logger.warning("train and test dataset split")
    datas = train_test_split(X, y, test_size=0.2)

    logger.warning("Saving split dataframes")
    for i, name in enumerate(NAMES):
        save_features(datas[i], name, output_pickle, storage_options)
