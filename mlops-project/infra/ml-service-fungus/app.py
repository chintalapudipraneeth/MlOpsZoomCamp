import os
import pickle

import pandas as pd
import requests as reqs
from flask import Flask, jsonify, request, make_response, render_template
from pymongo import MongoClient
from flask_cors import CORS

from models import Field, Value

app = Flask('fungis')
app.config['DEBUG'] = True
CORS(app)


@app.template_filter()
def caps(text):
    """Convert a string to all caps."""
    text = text.replace('-', ' ').capitalize()

    return text


def load_model():
    """Function to load model

    Returns:
        scikit-learn-model: Model to predict new values
    """
    with open('model.pkl', 'rb') as f_in:
        model = pickle.load(f_in)

    return model


def transform_variables(data_response, fungis_characs):
    """transform variables from form to variables to use with the model,
    1 to selected variable 0 another variables

    Args:
        data_response (dict): data from fomr
        fungis_characs (dict): data in db

    Returns:
        pandas.DataFrame: datrafame to predict
    """
    data = {}

    for k, values in data_response.items():
        for v in values:
            v_fungi = fungis_characs[k]
            data[f'{k}_{v}'] = [1] if f"{k}_{v_fungi}" == f'{k}_{v}' else [0]

    df = pd.DataFrame(data)

    return df


def get_db():
    """Function to get db of mongodb, used to separate in unittest

    Returns:
        mongodb.Collection: Collection to insert data
    """
    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    db = os.getenv("MONGO_DB")
    host = os.getenv("MONGO_HOST")
    port = int(os.getenv("MONGO_PORT", "0"))
    collection = os.getenv("MONGO_COLLECTION")
    client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/')
    db = client[db]
    collection = db[collection]

    return collection


def save_registers(collection, register):
    """Funtion to save register with its prediction

    Args:
        register (dict): data send from form to predict

    Returns:
        str: id from mongodb
    """
    register = {k: v[0] for k, v in register.items()}
    collection.insert_one(register)

    return register


def send_evidently(value):
    value = {k: v for k, v in value.items() if k != "_id"}
    EVIDENTLY_SERVICE_ADDRESS = "http://evidently:5005"
    reqs.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/fungus", json=[value])


@app.route("/")
def home():
    """Home page of app flask

    Returns:
        render_template: html page
    """
    data_fields = Field.select(Field.field, Value.value).join(Value).dicts()
    data_response = {data['field']: [] for data in data_fields}

    for data in data_fields:
        data_response[data['field']].append(data['value'])

    data_response.pop('class', 'droped')

    return render_template('home.html', data=data_response)


@app.route('/api/predict', methods=['POST'])
def predict_endpoint():
    """funtion to predict with new values

    Returns:
        json: json with prediction
    """
    integration_test = os.getenv("INTEGRATION_TEST", "0")
    id_mongo = {"_id": None}
    fungis_characs = request.get_json()
    original_json = fungis_characs.copy()
    fungis_characs = {k: v.lower() for k, v in fungis_characs.items()}
    app.logger.info('logged in successfully')
    dict_error_response = {
        'not_valid_field': [],
        'error_value': {},
        'empty_value': [],
    }
    exists_errors = False

    data_fields = Field.select(Field.field, Value.value).join(Value).dicts()

    data_response = {data['field']: [] for data in data_fields}
    data_response_original = {data['field']: [] for data in data_fields}

    for data in data_fields:
        data_response[data['field']].append(data['value'].lower())

    for data in data_fields:
        data_response_original[data['field']].append(data['value'])

    data_response.pop('class', 'droped')
    data_response_original.pop('class', 'droped')

    for k, v in fungis_characs.items():
        value_valid = data_response.get(k, None)

        if value_valid is None:
            dict_error_response['not_valid_field'].append(k)
            exists_errors = True
            continue

        if v == "":
            exists_errors = True
            dict_error_response['empty_value'].append(k)
            continue

        if v not in value_valid:
            exists_errors = True
            dict_error_response['error_value'] = {
                k: {
                    'not_valid': v,
                    'valids': value_valid,
                }
            }

    if exists_errors:
        dict_clean_error_response = {
            k: v for k, v in dict_error_response.items() if v
        }
        return make_response(jsonify(dict_clean_error_response), 400)

    df = transform_variables(data_response_original, original_json)
    ml = load_model()
    pred = ml.predict(df)

    if integration_test == "0":
        register = df.to_dict(orient="list")
        register["class"] = [int(pred[0])]
        collection = get_db()
        id_mongo = save_registers(collection, register)
        send_evidently(id_mongo)

    app.logger.error(pred)
    app.logger.error(fungis_characs)
    app.logger.error(id_mongo)

    result = {'is_poisonous': int(pred[0]), 'id': str(id_mongo["_id"])}

    return make_response(jsonify(result), 201)


@app.route('/api/true_predict', methods=['POST'])
def true_predict():
    result = {'is_poisonous': "", 'id': ""}

    return make_response(jsonify(result), 201)
