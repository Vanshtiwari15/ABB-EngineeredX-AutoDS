from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

from backend.services.model_candidates import (
    get_classification_models
)


def compare_models(
    X_train,
    X_test,
    y_train,
    y_test
):

    models = get_classification_models()

    best_model = None
    best_model_name = None
    best_score = 0

    all_results = {}

    for name, model in models.items():

        print(f"Training {name}")

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        f1 = f1_score(
            y_test,
            predictions,
            average="weighted"
        )

        precision = precision_score(
            y_test,
            predictions,
            average="weighted"
        )

        recall = recall_score(
            y_test,
            predictions,
            average="weighted"
        )

        all_results[name] = {
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4)
        }

        if accuracy > best_score:
            best_score = accuracy
            best_model = model
            best_model_name = name

    return {
        "best_model": best_model,
        "best_model_name": best_model_name,
        "best_score": best_score,
        "all_results": all_results
    }