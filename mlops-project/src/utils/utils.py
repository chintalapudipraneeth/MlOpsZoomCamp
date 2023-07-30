# -*- coding: utf-8 -*-
"""Module where is created the common functions to use with the cli and
flow prefect
"""

import os
import pickle
import logging
import subprocess

import docker
import pandas as pd
import coloredlogs
from dotenv import find_dotenv, load_dotenv
from prefect import get_run_logger
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

CONFS = {
    "PREFECT_API_URL": "http://localhost:4200/api",
    "MLFLOW_SET_TRACKING": "http://localhost:5000",
    "MLFLOW_S3_ENDPOINT_URL": "http://localhost:4566",
    "PREDICT_SERVICE_URL": "localhost:8000",
}

MODELS = [
    LogisticRegression,
    GaussianNB,
    KNeighborsClassifier,
    SVC,
    DecisionTreeClassifier,
    RandomForestClassifier,
]

NAMES = [
    "X_train.parquet",
    "X_test.parquet",
    "y_train.parquet",
    "y_test.parquet",
]


def read_features_xy(input_filepath, storage_options):
    """Function to read all files created as features, this returns
    multiple datasets of X and y to train and test models

    Args:
        input_filepath (str): filepath of files to read
        storage_options (dict): dictionary of options to read the files

    Returns:
        tuple(pandas.DataFrame): tuple of dataframe of X and y to train
        and test models
    """
    X_train = pd.read_parquet(  # pylint: disable=C0103
        os.path.join(input_filepath, "X_train.parquet"),
        storage_options=storage_options,
    )
    y_train = pd.read_parquet(
        os.path.join(input_filepath, "y_train.parquet"),
        storage_options=storage_options,
    )
    X_test = pd.read_parquet(  # pylint: disable=C0103
        os.path.join(input_filepath, "X_test.parquet"),
        storage_options=storage_options,
    )
    y_test = pd.read_parquet(
        os.path.join(input_filepath, "y_test.parquet"),
        storage_options=storage_options,
    )

    return X_train, y_train, X_test, y_test


def save_features(data, name, output, storage_options):
    """Funtion to save features of dataframe, this save X and y values
    and change pandas.Series to dataframe to save in parquet

    Args:
        data (pandas.Dataframe|pandas.Series): data to save en parquet
        name (str): Name to save file
        output (str): pathfile to save
        storage_options (dict): dictionary of options to save dataframe
    """
    logging.info(name)

    if isinstance(data, pd.DataFrame):
        data.to_parquet(
            os.path.join(output, name),
            index=False,
            storage_options=storage_options,
        )
    else:
        data.to_frame().to_parquet(
            os.path.join(output, name),
            index=False,
            storage_options=storage_options,
        )


def dump_pickle(obj, filename):
    """Function to save object to binary

    Args:
        obj (class): object to save
        filename (str): filepath where save the pickle
    """
    with open(filename, "wb") as f_out:
        pickle.dump(obj, f_out)


def load_pickle(filename):
    """Funtion to load binary object

    Args:
        filename (filepath): filepath where read the binary file

    Returns:
        object: object binary to use predict
    """
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def try_convert(value):
    """Funtion to try convert some values to original values, this is
    used to change values used in train model

    Args:
        value (str): value to try convert

    Returns:
        Any: Depending the value is the response
    """
    if value == "True":
        return True
    if value == "False":
        return False
    if value == "None":
        return None

    try:
        try:
            return int(value)
        except ValueError:
            return float(value)
    except ValueError:
        return value


def init_logger(debug, type_logger):
    """Funtion to initialize the logger

    Args:
        debug (bool): value to check level of logging (DEBUG or WARNING)
    """

    if type_logger == 'prefect':
        logger = get_run_logger()

        return logger

    level_log = logging.DEBUG if debug else logging.WARNING
    level_clog = "DEBUG" if debug else "WARNING"
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level_log, format=log_fmt)
    coloredlogs.install(level=level_clog)

    logger = logging.getLogger()

    return logger


def loading_envs():
    """find .env automagically by walking up directories until it's
    found, then load up the .env entries as environment variables

    Returns:
        dict: dictionary with the values to use by the system
    """
    load_dotenv(find_dotenv())
    env_list = CONFS.keys()
    context = {k: os.getenv(k) for k in env_list if os.getenv(k) is not None}

    return context


def get_git_revision_short_hash():
    """Funtion to get the git hash commit in the moment

    Returns:
        str: short hash of actually commit
    """
    return (
        subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        .decode('ascii')
        .strip()
    )


def create_submit_docker(user, password, path, hash_version, image):
    """Funtion to build new image docker and submit in the repo

    Args:
        user (str): username of docker hub
        password (str): password of docker hub
        path (str): path where is the dockerfile to process
        hash_version (str): hash version of actual repo
        image (str): name to save image
    """
    client = docker.from_env()
    client.login(username=user, password=password)
    client.images.build(
        path=path, tag=f"{user}/{image}:{hash_version}", quiet=True
    )

    for line in client.api.push(
        f"{user}/{image}:{hash_version}", stream=True, decode=True
    ):
        logging.warning(line)
