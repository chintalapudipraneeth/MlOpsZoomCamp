# -*- coding: utf-8 -*-
"""Main module to use and create the flow in prefect, to train and
and select model and register
"""
import os
import warnings
from typing import Any

from prefect import flow
from prefect.filesystems import S3, RemoteFileSystem
from prefect.blocks.system import JSON

from data.make_dataset import make_dataset_prefect
from models.train_model import train_model_prefect
from features.build_features import build_features_prefect
from register_model.register_model import register_model_prefect
from adjust_parameters.adjust_parameter import adjust_params_prefect

MLFLOW_S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
os.environ["MLFLOW_S3_ENDPOINT_URL"] = MLFLOW_S3_ENDPOINT_URL
MLFLOW_URI = os.getenv('MLFLOW_SET_TRACKING', 'http://localhost:5000')


# pylint: disable=R0903
class AutoContext:
    """This class is to replace the context of cli, and pass values to
    configs in prefect deploy
    """

    obj: dict[str, Any] = {}


@flow
def fungus():
    """Flow to execute all task of experiment fungus"""
    ctx = AutoContext()
    ctx.obj['DEBUG'] = False
    ctx.obj['MLFLOW_SET_TRACKING'] = MLFLOW_URI
    storage = os.getenv('STORAGE_S3', 'local')

    if not os.path.exists('models'):
        os.mkdir('models')

    if storage == 'local':
        s3 = RemoteFileSystem.load("fungusprefect")  # pylint: disable=C0103
    elif storage == 'aws':
        s3 = S3.load("fungusprefectaws")  # pylint: disable=C0103
    else:
        raise Exception('Value of $STORAGE is wrong')

    warnings.filterwarnings("ignore")
    configs = JSON.load("fungusconf")
    s3 = dict(s3)  # pylint: disable=C0103
    configs = dict(configs)["value"]

    if s3.get("setting", {}).get("key") is not None and s3.get(
        "setting", {}
    ).get("secret"):
        os.environ["AWS_ACCESS_KEY_ID"] = s3["setting"]["key"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = s3["setting"]["secret"]
        ctx.obj['AWS_ACCESS_KEY_ID'] = s3["setting"]["key"]
        ctx.obj['AWS_SECRET_ACCESS_KEY'] = s3["setting"]["secret"]

    s3_bucket = os.path.join("s3://", configs["MLFLOW"])
    input_make = os.path.join(s3_bucket, 'data/raw')
    output_make = os.path.join(s3_bucket, 'data/processed')
    train_f = configs["TRAIN_FILE"]
    test_f = configs["TEST_FILE"]
    sample_f = configs["OUTPUT_TEST"]
    ctx.obj["NUM_TOP_EXP"] = configs.get("NUM_TOP_EXP", 5)
    ctx.obj["PROJECT_NAME"] = configs.get("NAME_EXP_BASE", "Fingis")
    storage_configs = s3.get("settings")
    output_models = configs.get("OUTPUT_MODELS", "models/")

    if storage_configs is not None:
        storage_configs = {
            'client_kwargs': storage_configs.get('client_kwargs')
        }

    make_dataset_prefect(
        ctx,
        input_make,
        output_make,
        train_f,
        test_f,
        sample_f,
        storage_configs,
    )
    output_build = os.path.join(s3_bucket, "data/features/")
    build_features_prefect(ctx, output_make, output_build, storage_configs)
    train_model_prefect(ctx, output_build, storage_configs)
    adjust_params_prefect(ctx, output_build, storage_configs)
    register_model_prefect(ctx, output_build, output_models, storage_configs)


if __name__ == '__main__':
    fungus()
