# -*- coding: utf-8 -*-
"""Module to adjust params using hyperopt in the models and register in
mlops
"""
import os
from datetime import datetime

import click
import mlflow
from prefect import task
from hyperopt import STATUS_OK, Trials, tpe, fmin
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

from utils.utils import init_logger, read_features_xy
from utils.train_test_model import test_model

from .parameters import SPACES


# pylint: disable=C0103
def model_adjust_param(model, space, X_train, y_train, X_test, y_test, name):
    """Function to check the space and get the best results

    Args:
        model (scikit-learn model): model to train and test and get the
            best f2_score
        space (dict): dictionary of spaces
        X_train (pandas dataframe): values of x to train
        y_train (pandas dataframe): values of y to train
        X_test (pandas dataframe): values of x to test
        y_test (pandas dataframe): values of y to test
        name (str): _description_
    """

    def objective(params):
        ml = model(**params)  # pylint: disable=C0103
        ml.fit(X_train, y_train)
        model_name = type(ml).__name__
        today = str(datetime.now())
        with mlflow.start_run(run_name=f"project-{name}-{model_name}"):
            mlflow.set_tag("model", model_name)
            mlflow.log_params(params)
            metrics = test_model(ml, X_test, y_test, X_train, y_train)
            mlflow.log_metrics(metrics)
            mlflow.set_tag("date", today)

        return {"loss": metrics["f2_score"], "status": STATUS_OK}

    fmin(
        fn=objective,
        space=space,
        algo=tpe.suggest,
        max_evals=100,
        trials=Trials(),
    )


@click.command()
@click.pass_context
@click.option(
    "-i",
    "--input-filepath",
    type=click.Path(exists=True),
    default="data/features/",
)
def adjust_params(ctx, input_filepath):
    """This command test with hyperopt the multiple models, and select
    the best using "f2_score" and get the before train register models

    Keyword arguments:
    -i/--input-filepath -- folder where read the files
    Return: None
    """
    __adjust_params(ctx, input_filepath)


@task
def adjust_params_prefect(ctx, input_filepath, storage_options):
    """Task to testing all models using hyperopt and registers the best
    params

    Args:
        ctx (dict): dictioanry with values to configurate task
        input_filepath (str): file where read to process
        storage_options (dict): dictionary to config boto client in
        pandas
    """
    __adjust_params(ctx, input_filepath, storage_options, 'prefect')


def __adjust_params(
    ctx, input_filepath, storage_options=None, logger_type=None
):
    logger = init_logger(ctx.obj["DEBUG"], logger_type)
    integration_test = os.getenv("INTEGRATION_TEST", "0")
    name = ctx.obj.get("PROJECT_NAME", "Fungus").capitalize()

    pre_experiment = name
    log_top = int(ctx.obj.get("NUM_TOP_EXP", 5))
    name = f"{name}-Adjust-Params"
    mlflow_uri = ctx.obj.get("MLFLOW_SET_TRACKING", None)

    if mlflow_uri is None:
        raise Exception("MLFlow uri is not set")

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(name)
    client = MlflowClient(tracking_uri=mlflow_uri)

    logger.warning("get pre experiment to get train models")
    experiment = client.get_experiment_by_name(pre_experiment)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        filter_string="metrics.f2_score > 0.7",
        order_by=["tags.date DESC", "metrics.f2_score DESC"],
    )[:2]

    logger.warning("get name of models")
    models_to_params = {run.data.params["model"] for run in runs}
    logger.warning(models_to_params)

    logger.info("reading files")
    # pylint: disable=C0103
    X_train, y_train, X_test, y_test = read_features_xy(
        input_filepath, storage_options
    )

    for values in SPACES:
        model = values.pop("model")
        ml = model()
        model_name = type(ml).__name__
        logger.warning("working with model: %s", model_name)

        if model_name not in models_to_params:
            logger.warning("model %s is not used", model_name)
            continue

        if integration_test == "0":
            logger.warning('training with adjust of model')
            model_adjust_param(
                model, values, X_train, y_train, X_test, y_test, name
            )

        logger.warning("Train model without changes")
        with mlflow.start_run(run_name=f"project-{name}-{model_name}"):
            today = str(datetime.now())
            ml.fit(X_train, y_train)
            metrics = test_model(ml, X_test, y_test, X_train, y_train)
            params = ml.get_params()
            mlflow.set_tag("model", model_name)
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.set_tag("date", today)
