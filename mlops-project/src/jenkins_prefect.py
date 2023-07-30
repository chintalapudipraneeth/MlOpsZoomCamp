"""This is a module to create and deploy the service in local
"""
import os

import requests as reqs  # type: ignore
from prefect import flow, task
from prefect.blocks.system import JSON


@task
def call_jenkins():
    """Task for call deploy of jenkins"""
    in_docker = os.getenv("IN_DOCKER", "0")
    configs = JSON.load("jenkinscredentials").value
    configs["HOST"] = "localhost:8010" if in_docker == "0" else configs["HOST"]
    call_str = (
        f"http://{configs['USER']}:{configs['PASSWORD']}"
        f"@{configs['HOST']}/job/{configs['JOB_DEPLOY']}/build"
        f"?token={configs['TOKEN']}"
    )
    print("*" * 80)
    print(call_str)
    print("*" * 80)

    petition = reqs.get(call_str, timeout=10)
    print(petition)


@flow
def jenkins_deploy():
    """Main flow for deploy in jenkins"""
    call_jenkins()


if __name__ == "__main__":
    jenkins_deploy()
