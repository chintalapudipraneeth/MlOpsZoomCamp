import pickle

import numpy as np
import pandas as pd
import mongomock
from app import app, caps, load_model, save_registers, transform_variables
from mock import patch, mock_open
from sklearn.dummy import DummyRegressor


class TestApp:
    def test_caps(self):
        str_in = "hello-world"
        str_out = "Hello world"
        assert caps(str_in) == str_out

    def test_load_model(self):
        dummy_regr = DummyRegressor(strategy="mean")
        read_data = pickle.dumps(dummy_regr)
        mock_open_ = mock_open(read_data=read_data)
        with patch('builtins.open', mock_open_):
            obj = load_model()

        assert isinstance(obj, DummyRegressor)

    def test_transform_variables(self):
        data = {
            "test": ["1", "2", "3"],
            "prueba": ["4", "5", "6"],
        }
        fungis = {
            "test": "2",
            "prueba": "5",
        }
        values = {
            "test_1": [0],
            "test_2": [1],
            "test_3": [0],
            "prueba_4": [0],
            "prueba_5": [1],
            "prueba_6": [0],
        }
        df_test = pd.DataFrame(values)

        df_pd = transform_variables(data, fungis)

        assert df_pd.shape[0] == 1
        assert df_pd.shape[1] == 6
        assert df_pd.columns.tolist() == list(values.keys())
        assert df_test.equals(df_pd)

    def test_save_register(self):
        register = {"Hello": ["world"]}
        collection = mongomock.MongoClient().db.collection
        data = save_registers(collection, register)

        assert "_id" in data
        assert "Hello" in data
        assert data["Hello"] == "world"

    @patch("models.Field.select")
    def test_home(self, mock_field):
        field_support = SupportPWModel()
        mock_field.return_value = field_support
        app.testing = True
        with app.test_client() as test_client:
            response = test_client.get('/')
            assert response.status_code == 200

    @patch("models.Field.select")
    def test_predict_endpoint(self, mock_models):
        field_support = SupportPWModel()
        mock_models.return_value = field_support
        app.testing = True
        dummy = DummyRegressor(strategy="mean")
        X = np.array([1, 0, 1, 0])
        y = np.array([0, 1, 1, 1])
        dummy.fit(X, y)
        collection = mongomock.MongoClient().db.collection

        with app.test_client() as test_client:
            with patch("app.load_model", return_value=dummy):
                with patch("app.get_db", return_value=collection):
                    with patch("app.send_evidently", return_value=None):
                        response = test_client.post(
                            '/api/predict',
                            json={
                                "test": "1",
                                "prueba": "4",
                            },
                        )
                        assert response.status_code == 201
                        assert "is_poisonous" in response.json
                        assert response.json["is_poisonous"] == 0

                        response = test_client.post(
                            '/api/predict',
                            json={
                                "test": "3",
                                "prueba": "4",
                            },
                        )
                        assert response.status_code == 400
                        assert "error_value" in response.json
                        assert "test" in response.json["error_value"].keys()
                        assert (
                            "not_valid" in response.json["error_value"]["test"]
                        )
                        assert (
                            response.json["error_value"]["test"]["not_valid"]
                            == "3"
                        )
                        assert "valids" in response.json["error_value"]["test"]
                        assert response.json["error_value"]["test"][
                            "valids"
                        ] == [
                            "1",
                            "2",
                        ]

                        response = test_client.post(
                            '/api/predict',
                            json={
                                "test": "",
                                "prueba": "4",
                            },
                        )
                        assert response.status_code == 400
                        assert "empty_value" in response.json.keys()
                        assert response.json["empty_value"] == ["test"]

                        response = test_client.post(
                            '/api/predict',
                            json={
                                "error": "3",
                                "prueba": "4",
                            },
                        )
                        assert response.status_code == 400
                        assert "not_valid_field" in response.json.keys()
                        assert response.json["not_valid_field"] == ["error"]


class SupportPWModel:
    class DummyDict:
        def dicts(self):
            return [
                {
                    "field": "test",
                    "value": "1",
                },
                {
                    "field": "test",
                    "value": "2",
                },
                {
                    "field": "prueba",
                    "value": "4",
                },
                {
                    "field": "prueba",
                    "value": "5",
                },
            ]

    def join(self, dummy):
        return self.DummyDict()
