FROM python:3.8-alpine

WORKDIR /opt/app
RUN pip install kubernetes
ENV INTEGRATION=0
ENV KUBECONFIG=/opt/app/credential_config.yaml
COPY infra/bastion-k8s/run_init.py .
COPY cloud/credential_config.yaml credential_config.yaml
COPY cloud/k8s/services/service-ml-deployment.yaml k8s/service-ml-deployment.yaml
COPY cloud/k8s/services/service-ml-service.yaml k8s/service-ml-service.yaml
COPY cloud/k8s/integrations/service-ml-deployment.yaml integrations/service-ml-deployment.yaml
COPY cloud/k8s/integrations/service-ml-service.yaml integrations/service-ml-service.yaml

CMD [ "python", "/opt/app/run_init.py" ]
