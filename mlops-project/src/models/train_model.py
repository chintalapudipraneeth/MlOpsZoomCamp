# -*- coding: utf-8 -*-
"""Module to train models
"""

import os
import warnings
from datetime import datetime

import click
import mlflow
from prefect import task

from utils.utils import MODELS, init_logger, read_features_xy
from utils.train_test_model import test_model, train_model_fit

warnings.filterwarnings("ignore", category=FutureWarning)


@click.command()
@click.pass_context
@click.option(
    "-i",
    "--input-filepath",
    type=click.Path(exists=True),
    default="data/features/",
)
def train_model(ctx, input_filepath):
    """This command train the models

    Keyword arguments:
    -i/--input-filepath -- folder where read the files to train the
        models
    Return: None
    """
    __train_model(ctx, input_filepath)


@task
def train_model_prefect(ctx, input_filepath, storage_options):
    """task to train models and register in mlflow

    Args:
        ctx (dict): dictionary with configuration to module
        input_filepath (str): filepath where is reading the files to
        train model
        storage_options (dict): dictionary to configure boto client in
        pandas
    """
    __train_model(ctx, input_filepath, storage_options, 'prefect')


def __train_model(ctx, input_filepath, storage_options=None, type_logger=None):
    logger = init_logger(ctx.obj["DEBUG"], type_logger)

    name = ctx.obj.get("PROJECT_NAME", "Fungus").capitalize()
    mlflow_uri = ctx.obj.get("MLFLOW_SET_TRACKING")

    if mlflow_uri is None:
        raise Exception("MLFlow uri is not set")

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(name)
    models = [model() for model in MODELS]

    logger.warning("reading files to train model")
    # pylint: disable=C0103
    X_train, y_train, X_test, y_test = read_features_xy(
        input_filepath, storage_options
    )
    today = str(datetime.now())

    for model in models:
        model_name = type(model).__name__
        logger.warning("training model: %s", model_name)
        with mlflow.start_run(run_name=f"project-{name}-{model_name}"):
            training_model = train_model_fit(model, X_train, y_train)
            mlflow.log_param(
                "train-data-path__X",
                os.path.join(input_filepath, "X_train.parquet"),
            )
            mlflow.log_param(
                "train-data-path__y",
                os.path.join(input_filepath, "y_train.parquet"),
            )
            mlflow.log_param(
                "test-data-path__X",
                os.path.join(input_filepath, "X_test.parquet"),
            )
            mlflow.log_param(
                "test-data-path__y",
                os.path.join(input_filepath, "y_test.parquet"),
            )
            mlflow.log_param("model", model_name)
            mlflow.set_tag("model", model_name)
            mlflow.set_tag("date", today)

            logger.warning("testing model amd get metrics")
            metrics = test_model(
                training_model, X_test, y_test, X_train, y_train
            )
            logger.debug(metrics)
            mlflow.log_metrics(metrics)

    logger.warning("end of process")
