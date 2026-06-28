from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
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
from sklearn.preprocessing import OneHotEncoder

from data_preparation import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    RANDOM_STATE,
    load_and_clean_data,
    split_data,
)


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs" / "random_forest_version_amelioree"
FINAL_THRESHOLD = 0.50

ENGINEERED_NUMERIC_COLUMNS = NUMERIC_COLUMNS + [
    "Pulse_Pressure",
    "Mean_Arterial_Pressure",
    "Cholesterol_HDL_Ratio",
    "LDL_HDL_Ratio",
    "Triglycerides_HDL_Ratio",
    "BMI_Age_Interaction",
    "Medical_Risk_Score",
    "Lifestyle_Risk_Score",
]

PARAMETER_CANDIDATES = [
    {
        "max_depth": 14,
        "min_samples_leaf": 8,
        "max_features": "sqrt",
        "max_samples": 0.50,
        "class_weight": "balanced",
    },
    {
        "max_depth": 18,
        "min_samples_leaf": 12,
        "max_features": 0.7,
        "max_samples": 0.50,
        "class_weight": "balanced",
    },
    {
        "max_depth": 16,
        "min_samples_leaf": 15,
        "max_features": 0.5,
        "max_samples": 0.50,
        "class_weight": {"High": 1.0, "Low": 2.6},
    },
]


class MedicalFeatureEngineer(BaseEstimator, TransformerMixin):
    """Ajoute des variables derivees sans modifier le fichier CSV d'origine."""

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        df = x.copy()

        df["Pulse_Pressure"] = df["Systolic_BP"] - df["Diastolic_BP"]
        df["Mean_Arterial_Pressure"] = (
            df["Systolic_BP"] + 2 * df["Diastolic_BP"]
        ) / 3

        df["Cholesterol_HDL_Ratio"] = df["Cholesterol"] / df["HDL"].clip(lower=1)
        df["LDL_HDL_Ratio"] = df["LDL"] / df["HDL"].clip(lower=1)
        df["Triglycerides_HDL_Ratio"] = df["Triglycerides"] / df["HDL"].clip(lower=1)
        df["BMI_Age_Interaction"] = df["BMI"] * df["Age"]

        df["Medical_Risk_Score"] = (
            (df["Systolic_BP"] >= 140).astype(int)
            + (df["Diastolic_BP"] >= 90).astype(int)
            + (df["BMI"] >= 30).astype(int)
            + (df["Cholesterol"] >= 200).astype(int)
            + (df["LDL"] >= 130).astype(int)
            + (df["Glucose"] >= 126).astype(int)
        )

        df["Lifestyle_Risk_Score"] = (
            (df["Smoking_Status"].astype(str).str.lower() != "never").astype(int)
            + (df["Physical_Activity_Level"].astype(str).str.lower() == "low").astype(int)
            + (df["Alcohol_Intake"] > df["Alcohol_Intake"].median()).astype(int)
            + (df["Stress_Level"] >= 7).astype(int)
            + (df["Salt_Intake"] > df["Salt_Intake"].median()).astype(int)
            + (df["Sleep_Duration"] < 6).astype(int)
        )

        return df


def build_version_amelioree_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
            ("numeric", "passthrough", ENGINEERED_NUMERIC_COLUMNS),
        ]
    )


def calculate_metrics(y_true, y_pred, high_probability) -> dict[str, float]:
    y_binary = (y_true == "High").astype(int)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision_high": precision_score(y_true, y_pred, pos_label="High", zero_division=0),
        "recall_high": recall_score(y_true, y_pred, pos_label="High", zero_division=0),
        "f1_high": f1_score(y_true, y_pred, pos_label="High", zero_division=0),
        "precision_low": precision_score(y_true, y_pred, pos_label="Low", zero_division=0),
        "recall_low": recall_score(y_true, y_pred, pos_label="Low", zero_division=0),
        "f1_low": f1_score(y_true, y_pred, pos_label="Low", zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "roc_auc": roc_auc_score(y_binary, high_probability),
    }


def predict_with_threshold(classifier, x_encoded, threshold: float) -> tuple[np.ndarray, np.ndarray]:
    high_index = list(classifier.classes_).index("High")
    high_probability = classifier.predict_proba(x_encoded)[:, high_index]
    predictions = np.where(high_probability >= threshold, "High", "Low")
    return predictions, high_probability


def make_classifier(parameters: dict, n_estimators: int) -> RandomForestClassifier:
    classifier_parameters = parameters.copy()
    class_weight = classifier_parameters.pop("class_weight")
    max_samples = classifier_parameters.pop("max_samples")

    return RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        bootstrap=True,
        class_weight=class_weight,
        max_samples=max_samples,
        **classifier_parameters,
    )


def tune_model_and_threshold(splits):
    results = []
    thresholds = np.arange(0.40, 0.61, 0.02)

    feature_engineer = MedicalFeatureEngineer()
    x_train_features = feature_engineer.fit_transform(splits["X_train"])
    x_dev_features = feature_engineer.transform(splits["X_dev"])

    preprocessor = build_version_amelioree_preprocessor()
    x_train_encoded = preprocessor.fit_transform(x_train_features)
    x_dev_encoded = preprocessor.transform(x_dev_features)

    for index, parameters in enumerate(PARAMETER_CANDIDATES, start=1):
        print(f"\nConfiguration {index}/{len(PARAMETER_CANDIDATES)} : {parameters}")
        classifier = make_classifier(parameters, n_estimators=20)
        classifier.fit(x_train_encoded, splits["y_train"])

        for threshold in thresholds:
            predictions, probabilities = predict_with_threshold(
                classifier, x_dev_encoded, float(threshold)
            )
            metrics = calculate_metrics(splits["y_dev"], predictions, probabilities)
            results.append(
                {
                    "configuration": index,
                    "threshold": round(float(threshold), 2),
                    **parameters,
                    **metrics,
                }
            )

    tuning_results = pd.DataFrame(results).sort_values(
        ["macro_f1", "balanced_accuracy"], ascending=False
    )
    tuning_results.to_csv(OUTPUT_DIR / "tuning_version_amelioree.csv", index=False)

    best = tuning_results.iloc[0]
    best_parameters = PARAMETER_CANDIDATES[int(best["configuration"]) - 1]
    best_threshold = float(best["threshold"])

    print("\nMeilleure configuration sur Ddev :")
    print(best_parameters)
    print(f"Meilleur seuil High observe sur Ddev : {best_threshold:.2f}")
    print(f"Seuil final retenu par stabilite : {FINAL_THRESHOLD:.2f}")
    print(f"Macro F1 Ddev : {best['macro_f1']:.4f}")

    return best_parameters, FINAL_THRESHOLD, tuning_results


def save_feature_importance(preprocessor: ColumnTransformer, classifier: RandomForestClassifier) -> None:
    feature_names = preprocessor.get_feature_names_out()
    importances = classifier.feature_importances_
    importance = pd.DataFrame({"feature": feature_names, "importance": importances})
    importance = importance.sort_values("importance", ascending=False)
    importance.to_csv(OUTPUT_DIR / "feature_importance_version_amelioree.csv", index=False)

    top_features = importance.head(20).sort_values("importance")
    plt.figure(figsize=(9, 7))
    plt.barh(top_features["feature"], top_features["importance"], color="#326b8f")
    plt.title("20 variables les plus importantes - Random Forest version amelioree")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_version_amelioree.png", dpi=150, bbox_inches="tight")
    plt.close()


def train_final_model(splits, best_parameters: dict, best_threshold: float) -> None:
    x_train_dev = pd.concat([splits["X_train"], splits["X_dev"]])
    y_train_dev = pd.concat([splits["y_train"], splits["y_dev"]])

    feature_engineer = MedicalFeatureEngineer()
    x_train_dev_features = feature_engineer.fit_transform(x_train_dev)
    x_test_features = feature_engineer.transform(splits["X_test"])

    preprocessor = build_version_amelioree_preprocessor()
    x_train_dev_encoded = preprocessor.fit_transform(x_train_dev_features)
    x_test_encoded = preprocessor.transform(x_test_features)

    classifier = make_classifier(best_parameters, n_estimators=80)
    print("\nEntrainement final sur Dtrain + Ddev...")
    classifier.fit(x_train_dev_encoded, y_train_dev)

    test_predictions, test_probabilities = predict_with_threshold(
        classifier, x_test_encoded, best_threshold
    )
    test_metrics = calculate_metrics(
        splits["y_test"], test_predictions, test_probabilities
    )
    test_report = classification_report(
        splits["y_test"], test_predictions, labels=["High", "Low"], zero_division=0
    )

    print("\nResultats finaux sur Dtest")
    for name, value in test_metrics.items():
        print(f"{name:18s}: {value:.4f}")

    print("\nRapport de classification sur Dtest:")
    print(test_report)

    with open(OUTPUT_DIR / "metrics_version_amelioree.txt", "w", encoding="utf-8") as file:
        file.write(f"Meilleurs parametres : {best_parameters}\n")
        file.write(f"Seuil High selectionne : {best_threshold:.2f}\n\n")
        file.write("Resultats finaux sur Dtest\n")
        for name, value in test_metrics.items():
            file.write(f"{name}: {value:.4f}\n")
        file.write("\nRapport de classification Dtest\n")
        file.write(test_report)

    matrix = confusion_matrix(
        splits["y_test"], test_predictions, labels=["High", "Low"]
    )
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix, display_labels=["High", "Low"]
    )
    display.plot(cmap="Blues")
    plt.title("Matrice de confusion Dtest - Random Forest version amelioree")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix_version_amelioree.png", dpi=150)
    plt.close()

    save_feature_importance(preprocessor, classifier)
    joblib.dump(
        {
            "preprocessor": preprocessor,
            "classifier": classifier,
            "threshold": best_threshold,
            "parameters": best_parameters,
            "version": "Modele Random Forest version amelioree avec variables derivees.",
        },
        OUTPUT_DIR / "random_forest_version_amelioree_model.joblib",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dataframe = load_and_clean_data()
    splits = split_data(dataframe)
    best_parameters, best_threshold, _ = tune_model_and_threshold(splits)
    train_final_model(splits, best_parameters, best_threshold)
    print(f"\nResultats sauvegardes dans : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
