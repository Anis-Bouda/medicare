# pretraitement.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


def preparer_donnees():
    # =========================
    # chargement du dataset
    # =========================
    data = pd.read_csv("hypertension_dataset.csv")

    # suppression des valeurs manquantes
    data = data.dropna(axis=0)

    # =========================
    # separation X et y
    # =========================
    X = data.drop(columns=["Hypertension"])
    y = data["Hypertension"]

    # encodage de la cible
    y = y.map({
        "Low": 0,
        "High": 1
    })

    # =========================
    # colonnes numeriques et categorielles
    # =========================
    colonnes_numeriques = [
        "Age",
        "BMI",
        "Cholesterol",
        "Systolic_BP",
        "Diastolic_BP",
        "Alcohol_Intake",
        "Stress_Level",
        "Salt_Intake",
        "Sleep_Duration",
        "Heart_Rate",
        "LDL",
        "HDL",
        "Triglycerides",
        "Glucose"
    ]

    colonnes_categorielles = [
        "Country",
        "Smoking_Status",
        "Physical_Activity_Level",
        "Family_History",
        "Diabetes",
        "Gender",
        "Education_Level",
        "Employment_Status"
    ]

    # =========================
    # train / dev / test
    # =========================
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y
    )

    X_dev, X_test, y_dev, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
        stratify=y_temp
    )

    # =========================
    # pretraitement
    # =========================
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), colonnes_numeriques),
            ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles)
        ]
    )

    X_train_prepared = preprocessor.fit_transform(X_train)
    X_dev_prepared = preprocessor.transform(X_dev)
    X_test_prepared = preprocessor.transform(X_test)

    # =========================
    # conversion en numpy
    # =========================
    X_train_np = X_train_prepared.toarray() if hasattr(X_train_prepared, "toarray") else X_train_prepared
    X_dev_np = X_dev_prepared.toarray() if hasattr(X_dev_prepared, "toarray") else X_dev_prepared
    X_test_np = X_test_prepared.toarray() if hasattr(X_test_prepared, "toarray") else X_test_prepared

    y_train_np = y_train.values
    y_dev_np = y_dev.values
    y_test_np = y_test.values

    return (
        X_train_np,
        X_dev_np,
        X_test_np,
        y_train_np,
        y_dev_np,
        y_test_np,
        preprocessor
    )