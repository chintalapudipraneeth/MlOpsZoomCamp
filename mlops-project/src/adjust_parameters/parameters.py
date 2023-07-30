"""This module is to create parameters to train models and get the
best scores
"""


from hyperopt import hp
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

SPACES = [
    {
        "model": LogisticRegression,
        "warm_start": hp.choice("warm_start", [True, False]),
        "fit_intercept": hp.choice("fit_intercept", [True, False]),
        "tol": hp.uniform("tol", 0.00001, 0.0001),
        "C": hp.uniform("C", 0.05, 3),
        "solver": hp.choice("solver", ["newton-cg", "lbfgs", "liblinear"]),
        "max_iter": hp.choice("max_iter", range(100, 500)),
        "multi_class": "auto",
        "class_weight": "balanced",
        "n_jobs": hp.choice("n_jobs", [-1, -1]),
    },
    {
        "model": RandomForestClassifier,
        "n_estimators": hp.choice("n_estimators", range(100, 1000)),
        "criterion": hp.choice("criterion", ["gini", "entropy", "log_loss"]),
        "max_features": hp.choice("max_features", ["sqrt", "log2", None]),
        "bootstrap": hp.choice("bootstrap", [True, False]),
        "warm_start": hp.choice("warm_start", [True, False]),
        "n_jobs": hp.choice("n_jobs", [-1, -1]),
    },
    {
        "model": GaussianNB,
        "var_smoothing": hp.uniform("var_smoothing", 0.00001, 1),
    },
    {
        "model": KNeighborsClassifier,
        "n_neighbors": hp.choice("n_neighbors", [3, 5, 7]),
        "weights": hp.choice("weights", ["uniform", "distance"]),
        "algorithm": hp.choice(
            "algorithm", ["auto", "ball_tree", "kd_tree", "brute"]
        ),
        "p": hp.choice("p", [1, 2]),
        "n_jobs": hp.choice("n_jobs", [-1, -1]),
    },
    {
        "model": SVC,
        "C": hp.uniform("C", 0, 20),
        "kernel": hp.choice("kernel", ["linear", "sigmoid", "poly", "rbf"]),
        "gamma": hp.uniform("gamma", 0, 20),
        "max_iter": hp.choice("max_iter", range(100, 1000)),
        "probability": hp.choice("probability", [True, False]),
    },
    {
        "model": DecisionTreeClassifier,
        "criterion": hp.choice("criterion", ["gini", "entropy", "log_loss"]),
        "splitter": hp.choice("splitter", ["best", "random"]),
        "max_features": hp.choice("max_features", ["sqrt", "log2", None]),
        "ccp_alpha": hp.uniform("ccp_alpha", 0, 100),
    },
]
