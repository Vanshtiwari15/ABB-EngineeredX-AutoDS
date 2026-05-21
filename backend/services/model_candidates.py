from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


def get_classification_models():

    return {
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42
        ),

        "logistic_regression": LogisticRegression(
            max_iter=1000
        ),

        "xgboost": XGBClassifier(
            eval_metric="logloss",
            random_state=42
        )
    }