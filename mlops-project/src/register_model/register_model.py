# -*- coding: utf-8 -*-
"""Module to select the best model, register and create model in
registry
"""

import os
import logging
from datetime import datetime

# pylint: disable=C0412
import click
import mlflow
from prefect import task
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from prefect.blocks.system import JSON

from utils.utils import (
    MODELS,
    dump_pickle,
    init_logger,
    try_convert,
    read_features_xy,
)


@click.command()
@click.pass_context
@click.option(
    "-i",
    "--input-filepath",
    type=click.Path(exists=True),
    default="data/features/",
)
@click.option("-o", "--output-models", type=click.Path(), default="models/")
def register_model(ctx, input_filepath, output_models):
    """This command get the before training models and params, to train
    the last model that will be used with the deploy, using f2_score,
    recall_score and accuracy

    Keyword arguments:
    -i/--input-filepath -- folder where read the files
    -o/--ouput-filepath -- folder where save the model
    Return: None
    """
    __register_model(ctx, input_filepath, output_models)


@task
def register_model_prefect(
    ctx, input_filepath, output_models, storage_options
):
    """task to register the best model

    Args:
        ctx (dict): dictionary with configuration to module
        input_filepath (str): filepathe where read the file to train
        model
        output_models (str): where is saved the model
        storage_options (dict): dictionary to configure boto client
        in pandas
    """
    __register_model(
        ctx, input_filepath, output_models, storage_options, 'prefect'
    )


def __register_model(
    ctx, input_filepath, output_models, storage_options=None, logger_type=None
):
    logger = init_logger(ctx.obj["DEBUG"], logger_type)

    name = ctx.obj.get("PROJECT_NAME", "Fungus").capitalize()
    name_experiment = f"{name}-Final"
    pre_experiment = f"{name}-Adjust-Params"
    log_top = int(ctx.obj.get("NUM_TOP_EXP", 5))
    mlflow_uri = ctx.obj.get("MLFLOW_SET_TRACKING", None)
    if (
        ctx.obj.get("AWS_ACCESS_KEY_ID") is not None
        and ctx.obj.get("AWS_SECRET_ACCESS_KEY") is not None
    ):
        os.environ["AWS_ACCESS_KEY_ID"] = ctx.obj.get("AWS_ACCESS_KEY_ID")
        os.environ["AWS_SECRET_ACCESS_KEY"] = ctx.obj.get(
            "AWS_SECRET_ACCESS_KEY"
        )

    if mlflow_uri is None:
        raise Exception("MLFlow uri is not set")

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(name_experiment)
    client = MlflowClient(tracking_uri=mlflow_uri)

    logger.info("Get pre-experiments, to select the best")
    experiment = client.get_experiment_by_name(pre_experiment)
    run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        filter_string=(
            "metrics.f2_score > 0.7 "
            "and metrics.recall_score < 1 "
            "and metrics.accuracy > 0.6"
        ),
        order_by=["tags.date DESC", "metrics.recall_score DESC"],
    )[0]

    logger.warning("Get the name of model to train and submit to registry")
    model_name = run.data.tags["model"]
    params_dirty = run.data.params

    logger.info("reading files")
    X_train, y_train, _, _ = read_features_xy(  # pylint: disable=C0103
        input_filepath, storage_options
    )

    ml = [  # pylint: disable=C0103
        model for model in MODELS if type(model()).__name__ == model_name
    ].pop()

    with mlflow.start_run(run_name=f"project-{name}-{model_name}"):
        logger.warning("training and register the best experiment")
        today = datetime.today().strftime("%Y-%m-%d")
        params = {k: try_convert(v) for k, v in params_dirty.items()}

        ml = ml(**params)  # pylint: disable=C0103
        ml.fit(X_train, y_train)
        mlflow.set_tag("model", model_name)
        mlflow.log_params(params)
        mlflow.set_tag("date", today)

        dump_pickle(ml, f"models/ml-{model_name}-{today}.b")

        log_model = mlflow.sklearn.log_model(
            ml,
            artifact_path=os.path.join(
                output_models, f"ml-{model_name}-{today[:10]}.b"
            ),
        )

        logger.warning("registring the model")
        model_uri = log_model.model_uri
        registered = mlflow.register_model(
            model_uri=model_uri, name="FungusBinaryClassifier"
        )

        registered = {k: str(v) for k, v in dict(registered).items() if v}
        logger.error(dict(registered))
        value = {
            'creation_timestamp': registered['creation_timestamp'],
            'last_updated_timestamp': registered['last_updated_timestamp'],
            'name': registered['name'],
            'run_id': registered['run_id'],
            'status': registered['status'],
            'version': registered['version'],
        }
        logging.error(value)
        json_block = JSON(value=value)
        json_block.save(f"ml{name.lower()}todeploy", overwrite=True)
