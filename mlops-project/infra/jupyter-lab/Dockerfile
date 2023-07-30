FROM python:3.9-slim-buster

WORKDIR /opt/jupyter
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV GIT_PYTHON_REFRESH=quiet

EXPOSE 8888

CMD [ "jupyter-lab", "--allow-root", "--ip", "0.0.0.0", "--NotebookApp.token=''", "--NotebookApp.password=''" ]