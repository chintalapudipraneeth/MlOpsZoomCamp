mlops-project
==============================

this is a project to practice all of course mlops-zoomcamp

Project Organization
------------

.
├── cloud/                                                  <- Folder with files to execute in cloud/k8s
│   ├── aws_cf/                                             <- folder with files to execute and create infra in aws using cloudformation
│   │   ├── 01-network-cloudformation.yml
│   │   ├── 02-securitygroup-cloudformation.yml
│   │   ├── 03-s3-cloudformation.yaml
│   │   ├── 04-rds-cloudformation-prefect.yml
│   │   ├── 05-rds-cloudformation-service.yml
│   │   ├── 06-rds-cloudformation-mlflow.yml
│   │   └── 07-eks-cluster.yml
│   ├── infra/                                              <- setup to local cloud, db or s3
│   │   └── aws_pre/
│   │       └── s3.sh                                       <- file to create buckets
│   ├── k8s/                                                <- folder with manifest to create service in k8s
│   │   ├── integrations/                                   <- manifest to create integration test in k8s
│   │   │   ├── service-ml-deployment.yaml
│   │   │   └── service-ml-service.yaml
│   │   ├── local/                                          <- Folder to up services in local (it is hardcoded files)
│   │   │   ├── common_secrets.yaml
│   │   │   ├── evidently_deployment.yaml
│   │   │   ├── grafana_deployment.yaml
│   │   │   ├── mlflow_deployment.yaml
│   │   │   ├── mongo-deployment.yaml
│   │   │   ├── prefect_deployment_server.yaml
│   │   │   ├── prometheus_deployment.yaml
│   │   │   ├── secrets_mlflow.yaml
│   │   │   ├── secrets_orion.yaml
│   │   │   └── secrets_service.yaml
│   │   ├── services/                                       <- Folder with files to up service
│   │   │   ├── service-ml-deployment.yaml
│   │   │   └── service-ml-service.yaml
│   │   └── templates/                                      <- this folder is for create templates for create services in local or cloud
│   │       └── prefect_deployment_server.yaml
│   ├── POCs/                                               <- proof of concepts the new services in cloud
│   │   └── 07-ec2-mlflow-cloudformation.yaml
│   ├── credential_config.template.yaml                     <- template to create access in k8s, with variables to change
│   └──  docker-compose.yaml                                <- this docker is used to create a local services and test with minikube
├── data/                                                   <- folder to work save data to use in experiment
│   ├── external/                                           <- data external for use with model
│   ├── features/                                           <- files to ready to train
│   ├── interim/                                            <- internal data
│   ├── processed/                                          <- data processed to create the features
│   └── raw/                                                <- raw data to create the analitycs
│       ├── mushrooms.csv                                   <- file to test model with data random
│       ├── sample_submission.csv                           <- file with target of test dataset
│       ├── test.csv                                        <- file to test dataset
│       └── train.csv                                       <- file to train dataset
├── docs/                                                   <- documentation of project
│   └── struct_project.md                                   <- this document
├── infra/                                                  <- general infra to create docker images and docker-compose
│   ├── alertmanager/                                       <- alert manager for prometheus
│   │   └── config.yml
│   ├── aws_pre/                                            <- folder to create bucket in local infra
│   │   └── s3.sh
│   ├── bastion-k8s/                                        <- docker to create deployments in k8s from jenkins
│   │   ├── Dockerfile
│   │   └── run_init.py
│   ├── evidently_service/                                  <- service to send data to prometheus
│   │   ├── datasets/
│   │   │   ├── reference_df.parquet                        <- dataset of reference to drift data
│   │   ├── app.py*                                         <- main file to start server
│   │   ├── config.yaml
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── grafana/                                            <- grafana folder to create image
│   │   ├── config/
│   │   │   ├── grafana_dashboards.yaml
│   │   │   └── grafana_datasources.yaml
│   │   ├── dashboards/
│   │   │   ├── cat_target_drift.json
│   │   │   ├── data_drift.json
│   │   │   └── regression_performance.json
│   │   ├── dashboards_outs/
│   │   │   ├── classification_performance.json
│   │   │   └── num_target_drift.json
│   │   ├── provisioning/
│   │   │   ├── dashboards/
│   │   │   │   └── dashboard.yml
│   │   │   └── datasources/
│   │   │       └── datasource.yml
│   │   ├── config.monitoring
│   │   └── Dockerfile
│   ├── mlflow/                                             <- folder to create docker for mlflow
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── ml-service-fungus/                                  <- folder to create ml-service
│   │   ├── templates/                                      <- templates for web
│   │   │   └── home.html
│   │   ├── tests/                                          <- UnitTest of endpoint
│   │   │   └── test_app.py
│   │   ├── app.py                                          <- app start
│   │   ├── Dockerfile
│   │   ├── entrypoint.bash                                 <- file to setup dockerfile and run application
│   │   ├── exp.env                                         <- envs to execute docker in jenkins
│   │   ├── init.py                                         <- this start the docker and get model to save in docker
│   │   ├── models.py                                       <- models for database
│   │   └── requirements.txt
│   ├── nginx/                                              <- folder to create nginx image
│   │   ├── disabled_sites/                                 <- disabled sites of image docker
│   │   │   ├── airflow.conf
│   │   │   ├── jenkins.conf
│   │   │   ├── jupyter.conf
│   │   │   └── localstack.conf
│   │   ├── sites/                                          <- sites to access from nginx
│   │   │   ├── adminer.conf
│   │   │   ├── mlflow.conf
│   │   │   └── prefect.conf
│   │   ├── Dockerfile
│   │   └── nginx.conf                                      <- configuration for nginx image
│   ├── prefect/                                            <- folder to create prefect image server and queues
│   │   ├── Dockerfile
│   │   ├── remote_storage.py                               <- file to create remote storage and queue
│   │   ├── requirements.txt
│   │   └── start.sh*                                       <- file to entrypoint of docker, this select if is server or queue
│   └── prometheus/                                         <- folder to create docker of prometheus
│       ├── config/
│       │   └── prometheus.yml
│       ├── alert.rules
│       ├── Dockerfile
│       └── prometheus.yml
├── integration_test/                                       <- file to execute integrations test
│   ├── aws_pre/                                            <- files to submit to s3 local to use with integrations test
│   │   ├── mushrooms.csv
│   │   ├── s3.sh
│   │   ├── sample_submission.csv
│   │   ├── test.csv
│   │   └── train.csv
│   ├── docker-compose.yaml                                 <- Docker compose to create local services rds and s3
│   ├── run_cmd.bash                                        <- entrypoint for docker container
│   ├── run_experiment.py                                   <- this run experiment from jenkins
│   └── test_predict.py                                     <- this execute predicts for integration test
├── models/                                                 <- models created
├── notebooks/                                              <- notebooks of analitycs
│   └── analytics_df.ipynb
├── references/                                             <- files to references of data
├── reports/                                                <- reports and images of analitycs process
│   ├── figures/
│   ├── second_chance.html
│   └── sera_venenoso.html
├── src/                                                    <- code of experiment
│   ├── adjust_parameters/
│   │   ├── adjust_parameter.py                             <- script to adjust params of experiments
│   │   └── parameters.py                                   <- parameters to retrain models
│   ├── create_infra_cloud/
│   │   └── create_infra.py                                 <- this create the infraestructure in aws (in beta, only creates infra)
│   ├── data/
│   │   └── make_dataset.py                                 <- make first dataset and clean some values
│   ├── features/
│   │   └── build_features.py                               <- this create features to train the model
│   ├── models/
│   │   └── train_model.py                                  <- this train the model
│   ├── register_model/
│   │   └── register_model.py                               <- register model in mlflow
│   ├── test_data/
│   │   └── test_data.py                                    <- test to endpoint
│   ├── utils/
│   │   ├── train_test_model.py                             <- utilities to train and test model
│   │   └── utils.py                                        <- common utils to system, read files and write
│   ├── visualization/                                      <- this is for save images of training or analitycs
│   │   ├── analytics_df.py
│   │   └── visualize.py
│   ├── fungus_prefect.py                                   <- deploy of code to train model
│   ├── jenkins_prefect.py                                  <- deploy of function to execute jenkins from prefect
│   └── main.py                                             <- main file of code
├── ci-integration.dockerfile                               <- Docker to check integration test
├── ci-test.dockerfile                                      <- Docker to check continuos integration test
├── docker-compose.yml                                      <- docker compose for local setup
├── docker_stop.sh*                                         <- this file is used to delete and stop docker, check controls
├── jenkins-pipeline                                        <- jenkins pipelines to create jobs
├── LICENSE                                                 <- LICENCE of project
├── Makefile                                                <- makefile to execute some command
├── Pipfile                                                 <- Pipfile of project
├── Pipfile.lock                                            <- lock libraries
├── pyproject.toml                                          <- configuration for qualities of code
├── README.md                                               <- README of Project
├── run_integrations.bash*                                  <- this is a test file to check integrations
├── setup.py                                                <- in this moment this files is not used
├── tox.ini                                                 <- file to configure some apps of queality


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
