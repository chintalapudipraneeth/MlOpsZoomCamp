#!/usr/bin/env bash
set -e
echo "Running service $REGISTER_MODEL"

python init.py
pip install -r requirements_model.txt

# gunicorn -w 4 -b 0.0.0.0:8000 app:app
flask --app app --debug run --host=0.0.0.0 --port 8000
