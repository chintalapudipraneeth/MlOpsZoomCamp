# Fungus (mushroom) is poisonous or not?

> ![#f03c15](https://via.placeholder.com/15/f03c15/f03c15.png) This project is only check with dockers and compose using linux, when try to test in mac I have problems with storage s3, in Windows I don't try

# Table of Contents
1. [Objective](#objective)
2. [Motivation](#motivation)
3. [How to run](#how-to-run)
    - [Local environment](#local-environment)
    - [Using docker-compose](#using-docker-compose)
    - [Using k8s](#using-k8s)
    - [AWS environment](#aws-environment) - does not work, only create infra
4. [Project structure](#project-structure)
5. [CI in git](#CI-in-git)
6. [Commands in python](#commands-in-python)
7. [Run only service](#run-only-service)
8. [ToDos](#todos)

## Objective

The objective of this project is create a model that can predicts if a mushroom is poisonous or not, for this project is used the dataset in kaggle: https://www.kaggle.com/competitions/sera-venenoso.

For this project the firts steps was check the dataset using a [notebook](notebooks/analytics_df.ipynb), in this is check the type of variables in dataset, check correlation (I use the values between 0.5 and -0.5 this is the best parameters to get good accuraty), change values to matrix of 1 and 0, I try to change values depending the number of uniques, but with this the models get accuracy of 100% (I believe that is overfitting), I train with 6 types of ML algorithms using the classification to evaluate because is a binary problem.


## Motivation

For this project the motivation is put all knowledge into practice in the course, using MLOps and respective tools, for example MLFlow, Prefect, Git and other. For this is used multiple tools:

- Python, main tool to get data, transform and create the models.
- MLFlow, this tools is used to create register of models and get a registry of this models and save the parameters and metrics for every test.
- Prefect, used to create a pipeline and automate the code
- Docker, used to create all containers to up the tools and services
- MiniKube, this is used to create a local k8s cluster and test before send to cloud
- CloudFormation, this is used to create the infraestructure in cloud, using AWS this is divided in:
    - network, create VPC, subnets (private and public) to connect all resources
    - security groups, this create the ports access to the apps
    - rds, create databases to use with the project, use 3 in postgresql
    - s3 this create the necessaries buckets to save files
    - eks this create the cluster and node workers to submit the apps

In local test using only docker and docker compose is used *Recreate Deployment*, this destroy previous service and up service with new features, this is not recommended when is necessary that services is up all time.

## How to run

For run this project exists multiple ways to run, 2 locals and 1 in cloud (in beta):

### Local environment

For run in local is necesary:

- [Pipenv](https://pipenv-es.readthedocs.io/es/latest/)
- [docker](https://docs.docker.com/engine/install/)
- [awslocal](https://github.com/localstack/awscli-local)
- [docker compose](https://docs.docker.com/compose/#compose-v2-and-the-new-docker-compose-command)
- [minikube](https://minikube.sigs.k8s.io/docs/start/) *This is optional to run in K8s cluster

#### Using docker compose

Is posible to run using only commands or make:

*With commands*:

- **pipenv install** -- this install all libraries to execute script
- **pipenv run python src/main.py start local** -- this up docker-compose and create some configs to execute cli
- **awslocal s3 cp data/raw/sample_submission.csv s3://mlflow/data/raw/sample_submission.csv** -- copy file to model
- **awslocal s3 cp data/raw/test.csv s3://mlflow/data/raw/test.csv** -- copy file to model
- **awslocal s3 cp data/raw/train.csv s3://mlflow/data/raw/train.csv** -- copy file to model
- **pipenv run python src/main.py --debug make-dataset build-features train-model adjust-params register-model** -- this run complete 'pipeline' to test functions, **is optional**
- with this command is possible the deploy in prefect:
    - *Create and deploy model train*
        - **pipenv run prefect deployment build ./src/fungus_prefect.py:fungus -n fungus -t fungus -sb remote-file-system/fungusprefect**
	    - **pipenv run prefect deployment apply ./fungus-deployment.yaml**
    - *Create and deploy flow to deploy in jenkins*
        - **pipenv run prefect deployment build ./src/jenkins_prefect.py:jenkins_deploy -n jenkins_deploy -t fungus -sb remote-file-system/fungusprefect**
	    - **pipenv run prefect deployment apply ./jenkins_deploy-deployment.yaml**
- to access to mlflow and prefect is possible with:
    - mlflow -> localhost:5000
    - prefect -> localhost:4002
- before to run deploy in local using jenkins is necessary:
    - get and copy admin password from jenkins logs: *docker logs mlops-project-jenkins-1*
    - access to localhost:8010
    - paste admin password in the box
    - install suggested plugins
    - register using *neimv* as user and *12345678* as password, the others fields depends of user
    - in instance configuration only click in save and finish and before Start using jenkins
- **Setup to create job:**
    - In the main page of jenkins (localhost:8010), create a new job, with name *"fungus_deploy"* (this is necessary to execute with prefect) and select *Pipeline*
    - In the next page, select in **Build Triggers**, *Trigger builds remotly* and use the token: *fungus10c4l*
    - In section *Pipeline* copy code in [jenkins-pipeline](./jenkins-pipeline) to script section, this part needs user and password, this is only necesary if you want to submit images of service if not delete all docker submit and change variable **$USER_CREDENTIALS_USR** by neimv
- **Run experiment**:
    - To run experiment enter to: localhost:4002
    - In deployment select fungus/fungus deployment and run (take aprox. 20 minutes)
    - When finished, select, jenkins-deploy/jenkins_deploy and run
    - Check in jenkins the job, when finished the service is up
- *How to check*:
    - to check service of predicts is possible:
        - access to localhost:8000 and exists one page to select options and predict
        - to test by api use: localhost:8000/api/predict, the necessary data is in: [test_predict.py](./integration_test/test_predict.py) and values is possible see in: [test_data](./src/test_data/test_data.py)
- *View monitoring*:
    - grafana: localhost:3000, exists two monitors in use: *data_drift* and *cat_target_drift*, to test is possible execute: **"cd src/test_data/ && pipenv run python test_data.py"** this execute a random dataset to check monitors @TODO: add test_data to cli

*With makefile*
- Is possible use **make run_local**, this include some commands:
    - **setup_local**, this run the initial configs and up all dockers
    - **copy_local**, copy all files to train model to s3
    - **delete_prefect_files**, delete files of previous prefect deploys
    - **deploy_prefect**, this deploy the flow in prefect
- before to run deploy in local using jenkins is necessary:
    - get and copy admin password from jenkins logs: *docker logs mlops-project-jenkins-1*
    - access to localhost:8010
    - paste admin password in the box
    - install suggested plugins
    - register using *neimv* as user and *12345678* as password, the others fields depends of user
    - in instance configuration only click in save and finish and before Start using jenkins
- **Setup to create job:**
    - In the main page of jenkins (localhost:8010), create a new job, with name *"fungus_deploy"* (this is necessary to execute with prefect) and select *Pipeline*
    - In the next page, select in **Build Triggers**, *Trigger builds remotly* and use the token: *fungus10c4l*
    - In section *Pipeline* copy code in [jenkins-pipeline](./jenkins-pipeline) to script section, this part needs user and password, this is only necesary if you want to submit images of service if not delete all docker submit and change variable **$USER_CREDENTIALS_USR** by neimv
- **Run experiment**:
    - To run experiment enter to: localhost:4002
    - In deployment select fungus/fungus deployment and run (take aprox. 20 minutes)
    - When finished, select, jenkins-deploy/jenkins_deploy and run
    - Check in jenkins the job, when finished the service is up
- *How to check*:
    - to check service of predicts is possible:
        - access to localhost:8000 and exists one page to select options and predict
        - to test by api use: localhost:8000/api/predict, the necessary data is in: [test_predict.py](./integration_test/test_predict.py) and values is possible see in: [test_data](./src/test_data/test_data.py)
- *View monitoring*:
    - grafana: localhost:3000, exists two monitors in use: *data_drift* and *cat_target_drift*, to test is possible execute: **"cd src/test_data/ && pipenv run python test_data.py"** this execute a random dataset to check monitors @TODO: add test_data to cli

#### Using k8s

This is a test of how to use K8s in cloud with external services, is possible run manually or with make (for this is necesary minikube or replace by another tool):

**Manual**:

- **docker-compose -f cloud/docker-compose.yaml up -d** -> this up all dbs and localstack to use s3
- **minikube start --driver="docker"** -> this start minikube with dirver docker
- **docker network connect cloud_backend minikube** -> connect network of compose with minikube
- **minikube ip** -> get the access ip to check services
- **awslocal s3 cp data/raw/sample_submission.csv s3://mlflow/data/raw/sample_submission.csv** -- copy file to model
- **awslocal s3 cp data/raw/test.csv s3://mlflow/data/raw/test.csv** -- copy file to model
- **awslocal s3 cp data/raw/train.csv s3://mlflow/data/raw/train.csv** -- copy file to model
- **kubectl apply -f cloud/k8s/** -> this up all necesaries services:
    - mlflow -> {ip-minikube}:30009
    - prefect -> {ip-minikube}:30010
- **minikube dashboard** -> to see all services
- to execute and deploy service is necessary enter to jenkins -> *localhost:8010* and configure
    - is necesary to execute 2 or 3 variables (3 if you like submit the images in your repo)
        - **DOCKER_P**, this is a user and password credential to submit images to docker repository, is optional if this doesn't exists delete all command in [jenkins-pipeline](./jenkins-pipeline) in section: *k8s*
        - **minikubeconfig**, this file is necessary to execute deployments in minikube cluster, exists a template in [credential_config](./cloud/credential_config.template.yaml), to get the credencials is possible with *make get_credentials_local*, this is create as Secret file and select the file with credentials
        - **IPMINIKUBE**, this is the ip of minikube get with: *minikube ip*
    - to create the pipeline create a new Job with name *fungus_deploy* and type pipeline
    - copy content of [jenkins-pipeline](./jenkins-pipeline) of section *k8s*, with this is possible run job check in *minikube dashboard* if exists service
- to check service is possible in *{ip_minikube}:30080*

**Make**

- **make run_k8s_local** -> run all infra, docker-compose and minikube, this include some commands
    - **setup_k8s** this run the script to execute docker compose and minikube and copy some images of repo, this is because in my machine fails to deploy some pods
    - **copy_local** copy files to execute model in s3
    - **delete_prefect_files** delete previous files of deploys to prefect
    - **deploy_prefect** deploy commands to execute model
    - **get_credentials_local** get values of certs to use in deploy with jenkins
    - copy anothers images to work with the services
- to execute and deploy service is necessary enter to jenkins -> *localhost:8010* and configure
    - is necesary to execute 2 or 3 variables (3 if you like submit the images in your repo)
        - **DOCKER_P**, this is a user and password credential to submit images to docker repository, is optional if this doesn't exists delete all command in [jenkins-pipeline](./jenkins-pipeline) in section: *k8s*
        - **minikubeconfig**, this file is necessary to execute deployments in minikube cluster, exists a template in [credential_config](./cloud/credential_config.template.yaml), to get the credencials is possible with *make get_credentials_local*, this is create as Secret file and select the file with credentials
        - **IPMINIKUBE**, this is the ip of minikube get with: *minikube ip*
    - to create the pipeline create a new Job with name *fungus_deploy* and type pipeline
    - copy content of [jenkins-pipeline](./jenkins-pipeline) of section *k8s*, with this is possible run job check in *minikube dashboard* if exists service
- to check service is possible in *{ip_minikube}:30080*

### AWS environment

This is in beta in this moment.
@TODO: Exist one command in python to execute all infraestructure, but in this moment deploy is incomplete

## Project structure

This is possible check in [struct project](./docs/struct_project.md)

## CI in git

This project is saved in gitlab, the verification is in [.gitlab-ci.yaml](./.gitlab-ci.yaml), and is not possible to push in main, only with branchs and using admin role.

## Commands in python

- **adjust-params**   This command test with hyperopt the multiple models, and select the best using "f2_score" and get the before train register models
- **build-features**  This command is to create features of dataset, and change values for other, for example 'class' to 1 or 0
- **make-dataset**    This command is to create the dataset, clean some values innecesaries and modify another
- **register-model**  This command get the before training models and params, to train the last model that will be used with the deploy, using f2_score, recall_score and accuracy
- **start**           start the environment, exists two envs:
                        local: use a docker-compose and use the static variables
                        k8s: use minikube to deploy services, dbs and other storages
                            is created using docker compose
                        aws: create infra in aws and use variables of outputs and
                            secrets
- **submit-dockers**  Method to create and submit dockers of prefect and mlflow in docker registry
- **test-data**       Command to test data in grafana
- **train-model**     This command train the models

## Images of docker in the project

For this project is used multiple containers, and some are created in this same project in the folder infra, this contains:

- evidently_service     -> service to send monitoring
- grafana               -> service to check dashboards
- mlflow                -> service to tracking the experiment
- ml-service-fungus     -> service to predict
- prefect               -> service to orquest the experiment
- prometheus            -> service to manage monitoring

## Run only service

For run only service of predict only run *make run_local*, enter to prefect and execute deploy fungus/fungus, when this ends, run:

`cd infra/ml-service-fungus && docker build -t $USER_CREDENTIALS_USR/ml-service .`

`cd infra/ml-service-fungus && docker run --name ml-fungus -p 8000:8000 --network mlops-project_backend --env-file exp.env -d $USER_CREDENTIALS_USR/ml-service`

And check in **http://localhost:8000** in this exists a front end to testing.

## Todos
- monitoring
    - retrain model (check if endpoint or use only a process in prefect)
- scripts:
    - run experiment and deployment
    - run testing of data to dashboards
- eks - aws
    - deploy
    - jenkins
    - monitoreo
- makefile
    - run experiment from script
    - run deployment from script
- I use happy pack to test, change because the mushroom.csv file contains gray color
- in model exists value 'c' the original value is conical
- some code is not complete with quality
