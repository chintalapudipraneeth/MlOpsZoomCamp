# CA_CERT := $(shell cat $(HOME)/.minikube/ca.crt | base64 -w 0; echo)
# CL_CERT := $(shell cat $(HOME)/.minikube/profiles/minikube/client.crt | base64 -w 0; echo)
# CL_KEY := $(shell cat $(HOME)/.minikube/profiles/minikube/client.key | base64 -w 0; echo)

get_credentials_local:
	@echo "ca.cert"
	$(shell cat $(HOME)/.minikube/ca.crt | base64 -w 0; echo)
	@echo "client.crt"
	$(shell cat $(HOME)/.minikube/profiles/minikube/client.crt | base64 -w 0; echo)
	@echo "client.key"
	$(shell cat $(HOME)/.minikube/profiles/minikube/client.key | base64 -w 0; echo)

# Local
setup_local:
	rm -f *-deployment.yaml
	rm -f *-manifest.json
	rm -f .prefectignore
	pip install pipenv pre-commit awscli-local -U
	pipenv install
	pipenv install --dev
	pre-commit install
	pipenv run python src/main.py start local

create_service:
	cd infra/ml-service-fungus && docker build -t neimv/ml-service:latest .
	cd infra/ml-service-fungus && docker run --name ml-fungus -p 8000:8000 --network mlops-project_backend --env-file exp.env -d neimv/ml-service
	docker logs -f ml-fungus

copy_local:
	awslocal s3 cp data/raw/sample_submission.csv s3://mlflow/data/raw/sample_submission.csv
	awslocal s3 cp data/raw/test.csv s3://mlflow/data/raw/test.csv
	awslocal s3 cp data/raw/train.csv s3://mlflow/data/raw/train.csv

deploy_prefect:
	pipenv run prefect deployment build ./src/fungus_prefect.py:fungus -n fungus -t fungus -sb remote-file-system/fungusprefect
	pipenv run prefect deployment apply ./fungus-deployment.yaml
	pipenv run prefect deployment build ./src/jenkins_prefect.py:jenkins_deploy -n jenkins_deploy -t fungus -sb remote-file-system/fungusprefect
	pipenv run prefect deployment apply ./jenkins_deploy-deployment.yaml

delete_prefect_files:
	rm -f *-deployment.yaml
	rm -f *-manifest.json

down_local:
	docker compose down --volumes

quality_checks:
	pipenv run isort src/
	pipenv run black src/
	pipenv run flake8 src/
	pipenv run mypy src/
	cd infra/ml-service-fungus && ls && pipenv run pytest tests/
	pipenv run pylint -rn --ignore-paths src/visualization,src/create_infra_cloud,src/test src/

run_cli_experiment:
	pipenv run python src/main.py --debug make-dataset build-features train-model adjust-params register-model

run_deploy_prefect_complete: delete_prefect_files copy_local deploy_prefect

run_local: setup_local copy_local delete_prefect_files deploy_prefect

# Local k8s
minikube_run:
	docker compose -f cloud/docker-compose.yaml up -d
	minikube start --driver="docker"
	docker network connect cloud_backend minikube
	minikube ip
	eval $$(minikube docker-env)

minikube_down:
	minikube stop & minikube delete
	docker compose -f cloud/docker-compose.yaml down --volumes
	docker network rm minikube
	# docker system prune -a --volumes -f

delete_minikube:
	minikube delete
	docker compose -f cloud/docker-compose.yaml down

setup_k8s:
	pipenv run python src/main.py start k8s
	sleep 60
	@echo $$(minikube ssh-key)
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/mlflow
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/prefect
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/prometheus
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/grafana
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/evidently
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull mongo
	sleep 90

run_k8s_local: setup_k8s copy_local delete_prefect_files deploy_prefect get_credentials_local
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/ml-service-integration
	ssh -o "StrictHostKeyChecking no" -i $$(minikube ssh-key) docker@$$(minikube ip) docker pull neimv/ml-service

# Cloud


# kubectl port-forward pods/mlflow-neimv-6b6cdb9db7-2h6v7 5000:5000
# aws eks \
# 	--region us-east-1 update-kubeconfig \
# 	--name EKS
# cat /home/neimv/.minikube/ca.crt | base64 -w 0; echo
# cat /home/neimv/.minikube/profiles/minikube/client.crt | base64 -w 0; echo
# cat /home/neimv/.minikube/profiles/minikube/client.key | base64 -w 0; echo

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  get_credentials_local\t\t\tget credentials to use with config of minikube"
	@echo "  setup_local\t\t\t\tis used to set local environment with docker"
	@echo "  create_services\t\t\tcreate the predict service, with name ml-fungus"
	@echo "  copy_local\t\t\t\tcopy files to train model using localstack and awslocal"
	@echo "  deploy_prefect\t\t\tdeploy flows to train and deploy service"
	@echo "  delete_prefect_files\t\t\tdelete files to deploy in prefect, in case of changes"
	@echo "  down_local\t\t\t\tdown docker compose with volumes"
	@echo "  quality_checks\t\t\tcheck that code accomplish the necesary rules"
	@echo "  run_minikube\t\t\t\tthis start minikube and add external services of docker using the same network"
	@echo "  run_cli_experiment\t\t\tthis run experiment using a cli created in python, in the same machine"
	@echo "  run_deploy_prefect_complete\t\tdelete and deploy services in prefect (train model and deploy with jenkins)"
	@echo "  run_local\t\t\t\trun completly all services and deploys in prefect, this not execute testings, jobs in jenkins or deploy service"
	@echo "  minikube_run\t\t\t\trun docker with services and minikube, connect between networks to work"
	@echo "  minikube_down\t\t\t\tstop all container, delete volumes and stop/delete minikube"
	@echo "  delete minikube\t\t\t\tdelete cluster minikube and stop all external infra"
	@echo "  setup_k8s\t\t\t\tthis call python setup to start all clusters and configure some attributes"
	@echo "  run_k8s_local\t\t\t\tcomplete run for minikube"
