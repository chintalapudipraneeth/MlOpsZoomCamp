# -*- coding: utf-8 -*-
"""module to create dataset, this read train and test files, join and
delete innecesary data
"""

import os
import warnings

import click
import numpy as np
import pandas as pd
from prefect import task

from utils.utils import init_logger

# this is to ignore warnings in some libraries
warnings.filterwarnings("ignore")


@click.command()
@click.pass_context
@click.option(
    "-i", "--input-filepath", type=click.Path(exists=True), default="data/raw/"
)
@click.option(
    "-o", "--output-filepath", type=click.Path(), default="data/processed/"
)
@click.option("--train-file", type=str, default="train.csv")
@click.option("--test-file", type=str, default="test.csv")
@click.option("--output-test", type=str, default="sample_submission.csv")
def make_dataset(
    ctx, input_filepath, output_filepath, train_file, test_file, output_test
):
    """This command is to create the dataset, clean some values
    innecesaries and modify another

    Keyword arguments:
    -i/--input-filepath -- folder where read the files
    -o/--output-filepath -- folder where save the file
    --train-file -- file to train (this is joined with test)
    --test-file -- file to train (this is joined with train)
    --output-test -- output values of test
    Return: None
    """
    __make_dataset(
        ctx,
        input_filepath,
        output_filepath,
        train_file,
        test_file,
        output_test,
    )


@task
def make_dataset_prefect(
    ctx,
    input_filepath,
    output_filepath,
    train_file,
    test_file,
    output_test,
    storage_options,
):
    """Task to create dataset, this read files and delete innecesaries
    values

    Args:
        ctx (dict): dictionary with configuration to module
        input_filepath (str): filepath where is reading files
        output_filepath (str): filepath where is saved the files
        train_file (str): train file of fungus
        test_file (str): test file of fungus
        output_test (str): output of test file
        storage_options (dict): dictionary whit configuration to client
        in pandas
    """
    __make_dataset(
        ctx,
        input_filepath,
        output_filepath,
        train_file,
        test_file,
        output_test,
        storage_options,
        'prefect',
    )


def __make_dataset(
    ctx,
    input_filepath,
    output_filepath,
    train_file,
    test_file,
    output_test,
    storage_options=None,
    logger_type=None,
):
    logger = init_logger(ctx.obj["DEBUG"], logger_type)

    logger.info("Reading the files to create the dataframe")
    df_train = pd.read_csv(
        os.path.join(input_filepath, train_file),
        storage_options=storage_options,
    )
    df_test = pd.read_csv(
        os.path.join(input_filepath, test_file),
        storage_options=storage_options,
    )
    df_class_test = pd.read_csv(
        os.path.join(input_filepath, output_test),
        storage_options=storage_options,
    )
    logger.warning("replace values of edibla and poisonous")
    df_class_test.replace(
        {"Edibla": "Edible", "Poisonousa": "Poisonous"}, inplace=True
    )
    df_test = df_test.merge(df_class_test, on="id")
    logger.info("concat both dataframes")
    # pylint: disable=C0103
    df = pd.concat([df_train, df_test]).sort_values("id")
    logger.warning("delete id column")
    df.drop("id", inplace=True, errors="ignore", axis=1)

    logger.warning(
        "Delete innecesaries rows"
        "veil-type only one value"
        "Drop columns with NaN (None and ?) values"
    )
    df = df.replace({"None": np.NaN})  # pylint: disable=C0103
    df = df.replace({"?": np.NaN})  # pylint: disable=C0103
    df.dropna(axis=1, inplace=True)

    logger.info("get correlation of dataset")
    corr = df.apply(lambda x: pd.factorize(x)[0]).corr(
        method="pearson", min_periods=1
    )
    colums_corr = corr[["class"]][
        (corr['class'] <= 0.50) & (corr['class'] >= -0.50)
    ]
    logger.warning("delete all duplicated values")
    df.drop_duplicates(inplace=True)

    logger.warning("Saving data preprocess")
    df[colums_corr.index.tolist() + ['class']].to_parquet(
        os.path.join(output_filepath, "pre_features.parquet"),
        index=False,
        storage_options=storage_options,
    )
