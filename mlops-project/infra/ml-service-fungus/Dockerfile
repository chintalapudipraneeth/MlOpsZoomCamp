FROM python:3.9-slim-buster

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ["init.py", "models.py", "./"]
RUN chmod +x init.py

COPY app.py .
COPY templates/ templates/

COPY entrypoint.bash entrypoint.bash
RUN chmod +x entrypoint.bash

ENTRYPOINT [ "/opt/app/entrypoint.bash" ]
