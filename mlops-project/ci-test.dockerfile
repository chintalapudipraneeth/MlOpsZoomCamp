FROM python:3.9-buster

WORKDIR /opt/app

COPY . .
RUN pip install pip pipenv -U
RUN pipenv install && pipenv install --dev
RUN pipenv run isort src/
RUN pipenv run black src/
RUN pipenv run flake8 src/
RUN pipenv run mypy src/
RUN cd infra/ml-service-fungus && ls && pipenv run pytest tests/
