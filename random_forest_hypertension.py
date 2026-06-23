from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from data_preparation import RANDOM_STATE, build_preprocessor, load_and_clean_data, split_data


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

# Configurations comparées uniquement sur Ddev.
# La sélection utilise le macro F1 afin de donner le même poids à High et Low.
PARAMETER_CANDIDATES = [
    {"max_depth": 8, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"max_depth": 12, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"max_depth": 20, "min_samples_leaf": 2, "max_features": "sqrt"},
    {"max_depth": None, "min_samples_leaf": 5, "max_features": "sqrt"},
    {"max_depth": 16, "min_samples_leaf": 5, "max_features": 0.7},
]


def calculate_metrics(y_true, y_pred, high_probability) -> dict[str, float]:
    """Calcule des métriques adaptées à une classification déséquilibrée."""
    y_binary = (y_true == "High").astype(int)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision_high": precision_score(y_true, y_pred, pos_label="High", zero_division=0),
        "recall_high": recall_score(y_true, y_pred, pos_label="High", zero_division=0),
        "f1_high": f1_score(y_true, y_pred, pos_label="High", zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "roc_auc": roc_auc_score(y_binary, high_probability),
    }


def print_metrics(title: str, metrics: dict[str, float]) -> None:
    print(f"\n{title}")
    for name, value in metrics.items():
        print(f"{name:18s}: {value:.4f}")


def make_classifier(parameters: dict, n_estimators: int) -> RandomForestClassifier:
    """Construit une forêt reproductible avec compensation du déséquilibre."""
    return RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        **parameters,
    )


def tune_on_dev(splits) -> tuple[dict, pd.DataFrame]:
    """Compare plusieurs configurations sur Ddev sans consulter Dtest."""
    preprocessor = build_preprocessor(scale_numeric=False)
    x_train_encoded = preprocessor.fit_transform(splits["X_train"])
    x_dev_encoded = preprocessor.transform(splits["X_dev"])

    results = []
    for index, parameters in enumerate(PARAMETER_CANDIDATES, start=1):
        print(f"\nConfiguration {index}/{len(PARAMETER_CANDIDATES)} : {parameters}")
        classifier = make_classifier(parameters, n_estimators=100)
        classifier.fit(x_train_encoded, splits["y_train"])

        predictions = classifier.predict(x_dev_encoded)
        high_index = list(classifier.classes_).index("High")
        probabilities = classifier.predict_proba(x_dev_encoded)[:, high_index]
        metrics = calculate_metrics(splits["y_dev"], predictions, probabilities)
        print_metrics("Résultats Ddev", metrics)
        results.append({"configuration": index, **parameters, **metrics})

    tuning_results = pd.DataFrame(results).sort_values("macro_f1", ascending=False)
    tuning_results.to_csv(OUTPUT_DIR / "random_forest_tuning.csv", index=False)

    best_index = int(tuning_results.iloc[0]["configuration"]) - 1
    best_parameters = PARAMETER_CANDIDATES[best_index]
    print(f"\nMeilleure configuration sur Ddev : {best_parameters}")
    return best_parameters, tuning_results


def save_feature_importance(model: Pipeline) -> None:
    """Sauvegarde et visualise les 20 variables les plus importantes."""
    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_
    importance = pd.DataFrame({"feature": feature_names, "importance": importances})
    importance = importance.sort_values("importance", ascending=False)
    importance.to_csv(OUTPUT_DIR / "random_forest_feature_importance.csv", index=False)

    top_features = importance.head(20).sort_values("importance")
    plt.figure(figsize=(9, 7))
    plt.barh(top_features["feature"], top_features["importance"], color="#3f7d66")
    plt.title("20 variables les plus importantes - Random Forest")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "random_forest_feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()


def train_final_model(splits, best_parameters: dict) -> Pipeline:
    """Réentraîne la meilleure configuration sur Dtrain + Ddev."""
    x_train_dev = pd.concat([splits["X_train"], splits["X_dev"]])
    y_train_dev = pd.concat([splits["y_train"], splits["y_dev"]])

    model = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(scale_numeric=False)),
            ("classifier", make_classifier(best_parameters, n_estimators=300)),
        ]
    )

    print("\nEntraînement final sur Dtrain + Ddev...")
    model.fit(x_train_dev, y_train_dev)

    test_predictions = model.predict(splits["X_test"])
    high_index = list(model.classes_).index("High")
    test_probabilities = model.predict_proba(splits["X_test"])[:, high_index]
    test_metrics = calculate_metrics(splits["y_test"], test_predictions, test_probabilities)
    test_report = classification_report(splits["y_test"], test_predictions, zero_division=0)

    print_metrics("Résultats finaux sur Dtest", test_metrics)
    print("\nRapport de classification sur Dtest:")
    print(test_report)

    with open(OUTPUT_DIR / "random_forest_metrics.txt", "w", encoding="utf-8") as file:
        file.write(f"Meilleurs paramètres : {best_parameters}\n\n")
        file.write("Résultats finaux sur Dtest\n")
        for name, value in test_metrics.items():
            file.write(f"{name}: {value:.4f}\n")
        file.write("\nRapport de classification Dtest\n")
        file.write(test_report)

    matrix = confusion_matrix(splits["y_test"], test_predictions, labels=["High", "Low"])
    display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=["High", "Low"])
    display.plot(cmap="Blues")
    plt.title("Matrice de confusion Dtest - Random Forest")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix_random_forest.png", dpi=150)
    plt.close()

    save_feature_importance(model)
    joblib.dump(model, OUTPUT_DIR / "random_forest_hypertension_model.joblib")
    return model


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    dataframe = load_and_clean_data()
    common_splits = split_data(dataframe)
    best_parameters, _ = tune_on_dev(common_splits)
    train_final_model(common_splits, best_parameters)
    print(f"\nRésultats sauvegardés dans : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
