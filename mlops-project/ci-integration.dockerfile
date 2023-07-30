FROM python:3.9-buster

WORKDIR /opt/app

COPY integration_test integration_test
COPY Pipfile .
COPY Pipfile.lock .
COPY integration_test/run_cmd.bash .
RUN chmod +x integration_test/run_cmd.bash
RUN pip install pip pipenv -U
RUN pipenv install && pipenv install --dev

ENV ON_DOCKER=1

CMD [ "bash", "run_cmd.bash" ]

# CMD [ "python", "-m", "http.server", "8000" ] to testing
