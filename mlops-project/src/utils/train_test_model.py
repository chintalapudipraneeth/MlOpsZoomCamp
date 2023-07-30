"""Common functions to train and test models
"""

import logging

from sklearn.metrics import (
    f1_score,
    fbeta_score,
    recall_score,
    accuracy_score,
    precision_score,
    confusion_matrix,
)
from sklearn.model_selection import cross_val_score


def train_model_fit(model, X, y):  # pylint: disable=C0103
    """function to train the model

    Args:
        model (scikit-learn model): model scikit learn to train
        X (dataframe pandas): dataset to train the model
        y (dataframe pandas): dataset outputs to train the model

    Returns:
        scikit-learn model: this is the model trained
    """
    model.fit(X, y)

    return model


def test_model(model, x_test, y_test, x_train, y_train):
    """function to test the models, and get some metrics of model

    Args:
        model (scikit-lear model): model trained to test
        x_test (dataframe pandas): variables to test of dataframe
        y_test (dataframe pandas): ouputs values of dataframe test
        x_train (dataframe pandas): values to train
        y_train (dataframe pandas): outputs values of train dataset

    Returns:
        dictionary: dictionary with some metrics of model
    """
    logger = logging.getLogger(__name__)
    run = {}
    y_pred = model.predict(x_test)

    logger.info("get the confusion matrix")
    # pylint: disable=C0103
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    # report = classification_report(y, y_pred)
    scores = cross_val_score(model, x_train, y_train, cv=10)
    logger.debug(scores)
    logger.debug(scores.mean())

    logger.info("Get all metrics")
    false_positive_rate = fp / (fp + tn)
    false_negative_rate = fn / (tp + fn)
    true_negative_rate = tn / (tn + fp)
    negative_predictive_value = tn / (tn + fn)
    false_discovery_rate = fp / (tp + fp)
    recall = recall_score(y_test, y_pred)  # or optionally tp / (tp + fn)
    precision = precision_score(y_test, y_pred)  # or optionally tp/ (tp + fp)
    # or optionally (tp + tn) / (tp + fp + fn + tn)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    f2 = fbeta_score(y_test, y_pred, beta=2)

    logger.info("saving metrics")
    run["true_positive"] = tp
    run["false_positive"] = fp
    run["true_negative"] = tn
    run["false_negative"] = fn
    run["false_positive_rate"] = false_positive_rate
    run["false_negative_rate"] = false_negative_rate
    run["true_negative_rate"] = true_negative_rate
    run["negative_predictive_value"] = negative_predictive_value
    run["false_discovery_rate"] = false_discovery_rate
    run["recall_score"] = recall
    run["precision_score"] = precision
    run["accuracy"] = accuracy
    run["f1_score"] = f1
    run["f2_score"] = f2
    run["cross_score_mean"] = scores.mean()

    for i, val in enumerate(scores):
        run[f"cross_scores_{i}"] = val

    return run
