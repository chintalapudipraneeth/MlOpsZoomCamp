# -*- coding: utf-8 -*-
"""Main module, this contains 3 functions, CLI as main endpoint of cli
start is a module to start the local infra, create configuration and
create a AWS infra, and the third is a endpoint to prefect deploy
"""

import time
import logging
import subprocess
from pathlib import Path

import click
import requests  # type: ignore
from kubernetes import utils, client, config

from utils.utils import (
    CONFS,
    init_logger,
    loading_envs,
    create_submit_docker,
    get_git_revision_short_hash,
)
from data.make_dataset import make_dataset
from models.train_model import train_model
from test_data.test_data import test_data
from features.build_features import build_features
from register_model.register_model import register_model
from create_infra_cloud.create_infra import create_infra
from adjust_parameters.adjust_parameter import adjust_params


@click.group(chain=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    """CLI to create a chain of training models, and registers in miflow

    Keyword arguments:
    ctx -- context of cli, for example connections or configs
    debug -- flag to on/off debug, default: off
    Return: None
    """
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = debug


@cli.command()
@click.pass_context
@click.argument(
    "env", type=click.Choice(["local", "k8s", "aws"], case_sensitive=True)
)
@click.option("-n", "--name", type=str, default="fungus")
@click.option("--delete/--no-delete", default=False)
@click.option("--build/--no-build", default=False)
@click.option("--top-exp", type=int, default=5)
def start(ctx, env, name, delete, build, top_exp):
    """start the environment, exists two envs:
        local: use a docker-compose and use the static variables
        k8s: use minikube to deploy services, dbs and other storages
            is created using docker compose
        aws: create infra in aws and use variables of outputs and
            secrets

    Keyword arguments:
    ctx -- context of cli, for example connections or configs
    env -- enviroment where to use, local or aws
    Return: None
    """
    # flake8: noqa: C901
    init_logger(ctx.obj["DEBUG"], None)
    attemps = 10

    # create docker local and .env to use with local
    if env == "local":
        logging.info("running infra in local env")
        logging.warning("Down docker compose")
        docker_down = "" if not delete else "--volumes"
        docker_build = "" if not build else "--build"
        subprocess.run(
            f"docker compose down {docker_down}", shell=True, check=True
        )
        logging.warning("running docker-compose")
        subprocess.run(
            f"docker compose up {docker_build} -d", shell=True, check=True
        )
        logging.warning("infra is up")
    elif env == "k8s":
        logging.warning("running docker-compose")
        subprocess.run(
            "docker compose -f cloud/docker-compose.yaml up -d",
            shell=True,
            check=True,
        )
        logging.warning("running minikube")
        subprocess.run(
            'minikube start --driver="docker" --cpus 4', shell=True, check=True
        )
        subprocess.run(
            "docker network connect cloud_backend minikube",
            shell=True,
            check=True,
        )
        subprocess.run(
            "docker network connect minikube cloud-jenkins-1",
            shell=True,
            check=True,
        )
        ip_minikube = subprocess.run(
            "minikube ip",
            shell=True,
            check=True,
            capture_output=True,
            encoding='utf-8',
        )

        if ip_minikube.stderr != "":
            raise Exception(ip_minikube.stderr)

        ip_minikube = ip_minikube.stdout.replace("\n", "")
        config.load_kube_config()
        k8s_client = client.ApiClient()
        client_api = client.CoreV1Api()
        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name="url-prefect-access"),
            data={},
            string_data={"ip_cluster": f"http://{ip_minikube}:30010/api"},
        )

        client_api.create_namespaced_secret(namespace="default", body=secret)
        yaml_dir = './cloud/k8s/local/'
        utils.create_from_directory(k8s_client, yaml_dir)
        CONFS["MLFLOW_SET_TRACKING"] = f"http://{ip_minikube}:30009"
        CONFS["PREFECT_API_URL"] = f"http://{ip_minikube}:30010/api"
    elif env == "aws":
        create_infra(ctx)

        return

    with open(".env", "w", encoding="utf-8") as envfile:
        logging.info("Creating .env with default values and name of project")
        for key, value in CONFS.items():
            envfile.write(f"{key}={value}\n")

        envfile.write(f"PROJECT_NAME={name}\n")
        envfile.write(f"NUM_TOP_EXP={top_exp}\n")

    url_mlflow = CONFS["MLFLOW_SET_TRACKING"]
    url_prefect = CONFS["PREFECT_API_URL"]
    ml_health = "/ajax-api/2.0/preview/mlflow/experiments/list"
    pr_health = "/health"
    blocks_uri = "/block_documents/filter"
    necesary_blocks = {
        "fungusconf": False,
        "fungusprefect": False,
        "fungusprefectaws": False,
    }

    while True and env == "local":
        time.sleep(60)
        logging.warning("Checking healths")
        try:
            ml_200 = (
                requests.get(
                    f'{url_mlflow}{ml_health}', timeout=10
                ).status_code
                == 200
            )
            pr_200 = (
                requests.get(
                    f'{url_prefect}{pr_health}', timeout=10
                ).status_code
                == 200
            )
            blocks = requests.post(
                f"{url_prefect}{blocks_uri}", timeout=10
            ).json()
            blocks = [b["name"] for b in blocks]

            necesary_blocks = {
                k: k in blocks for k, _ in necesary_blocks.items()
            }
        except Exception as exp:  # pylint: disable=W0703
            logging.error(exp)
            ml_200 = False
            pr_200 = False

        logging.error(necesary_blocks)

        if ml_200 and pr_200 and all(necesary_blocks.values()):
            break

        if attemps == 0:
            logging.error("failed num of attemps")
            raise Exception("Failed to start servers")


@cli.command()
@click.option("-u", "--user", required=True, type=str)
@click.option("-p", "--password", required=True, type=str)
@click.option(
    "--prefect-docker",
    type=click.Path(exists=True),
    default="infra/prefect/",
)
@click.option(
    "--mlflow-docker", type=click.Path(exists=True), default="infra/mlflow/"
)
@click.option(
    "--service",
    type=click.Path(exists=True),
    default="infra/ml-service-fungus/",
)
@click.option(
    "--grafana-docker", type=click.Path(exists=True), default="infra/grafana/"
)
@click.option(
    "--prometheus-docker",
    type=click.Path(exists=True),
    default="infra/prometheus/",
)
@click.option(
    "--evidently-docker",
    type=click.Path(exists=True),
    default="infra/evidently_service/",
)
@click.option(
    "--jenkins-docker",
    type=click.Path(exists=True),
    default="infra/jenkins/",
)
def submit_dockers(
    user,
    password,
    prefect_docker,
    mlflow_docker,
    service,
    grafana_docker,
    prometheus_docker,
    evidently_docker,
    jenkins_docker,
):
    """Method to create and submit dockers of prefect and mlflow in
    docker registry

    Args:
        user (str): username of docker registry
        password (str): password of docker registry
        prefect_docker (str): path where is saved prefect docker
        mlflow_docker (str): pathe where is saved mlflow docker
        service (str): path where is saved service docker
    """
    hash_version = get_git_revision_short_hash()
    click.echo(hash_version)
    dockers = {
        'prefect': prefect_docker,
        'mlflow': mlflow_docker,
        'ml-service': service,
        'prometheus': prometheus_docker,
        'grafana': grafana_docker,
        'evidently': evidently_docker,
        'jenkins': jenkins_docker,
    }

    logging.warning("Creating dockers")
    for key, value in dockers.items():
        logging.warning("Creating %s image" % key)
        create_submit_docker(user, password, value, hash_version, key)
        create_submit_docker(user, password, value, "latest", key)


if __name__ == "__main__":
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    context = loading_envs()

    cli.add_command(make_dataset)
    cli.add_command(build_features)
    cli.add_command(train_model)
    cli.add_command(adjust_params)
    cli.add_command(register_model)
    cli.add_command(test_data)

    # Is not necesary send debug because is pased in cli
    # pylint: disable=E1120
    cli(obj=context)
