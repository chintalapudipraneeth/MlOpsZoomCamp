#!/usr/bin/env python3
import os
import shutil

import pandas as pd
from mlflow.tracking import MlflowClient

from models import Field, Value, psql_db

REGISTER_MODEL = os.getenv("REGISTER_MODEL")
MLFLOW_S3_ENDPOINT_URL = os.getenv("MLFLOW_S3_ENDPOINT_URL")

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "test")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv(
    "AWS_SECRET_ACCESS_KEY", "test"
)
os.environ["AWS_DEFAULT_REGION"] = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
options = {
    'client_kwargs': {
        'endpoint_url': MLFLOW_S3_ENDPOINT_URL,
    }
}


def db_create():
    base_path = os.getenv('BASE_PATH_DF')
    train = 'pre_features.parquet'
    psql_db.connect()
    psql_db.create_tables([Field, Value])

    print("*" * 80)
    print("Reading files of s3")
    print("*" * 80)
    print(os.path.join(base_path, train))
    df = pd.read_parquet(
        os.path.join(base_path, train), storage_options=options
    )
    values = {column: [] for column in df.columns.tolist()}

    for v in values:
        values[v] = df[v].unique()

    for k, v in values.items():
        field = Field.get_or_none(Field.field == k)

        if field is None:
            field = Field.create(field=k)

        for i in v:
            exists = Value.get_or_none(value=i, field_id=field)

            if exists is None:
                Value.create(value=i, field_id=field)

    print("*" * 80)
    print("Created registers")
    print("*" * 80)


def main():
    if REGISTER_MODEL is None:
        raise Exception("REGISTER_MODEL variable is None")

    mlflow_uri = os.getenv("MLFLOW_SET_TRACKING", "http://localhost:5000")
    print('*' * 80)
    print(mlflow_uri)
    print('*' * 80)
    client = MlflowClient(tracking_uri=mlflow_uri)
    db_create()

    max_version = max(
        [
            dict(mdl)["version"]
            for mdl in client.search_model_versions(f"name='{REGISTER_MODEL}'")
        ]
    )

    for mdl in client.search_model_versions(f"name='{REGISTER_MODEL}'"):
        model_data = dict(mdl)
        if model_data["version"] == max_version:
            break

    print(model_data)
    local_dir = "/tmp/artifact_downloads"
    folder = "models"
    if not os.path.exists(local_dir):
        os.mkdir(local_dir)

    local_path = client.download_artifacts(
        model_data["run_id"], folder, local_dir
    )
    print("Artifacts downloaded in: {}".format(local_path))
    print("Artifacts: {}".format(os.listdir(local_path)))
    max_path = max(os.listdir(local_path))
    shutil.move(
        os.path.join(local_dir, folder, max_path, "requirements.txt"),
        "./requirements_model.txt",
    )
    shutil.move(
        os.path.join(local_dir, folder, max_path, "model.pkl"), "./model.pkl"
    )


if __name__ == "__main__":
    main()
