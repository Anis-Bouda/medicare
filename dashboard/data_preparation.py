from pathlib import Path
from sqlalchemy import create_engine

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "hypertension_dataset.csv"
TARGET = "Hypertension"
RANDOM_STATE = 42

NUMERIC_COLUMNS = [
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
    "Glucose",
]

CATEGORICAL_COLUMNS = [
    "Country",
    "Smoking_Status",
    "Physical_Activity_Level",
    "Family_History",
    "Diabetes",
    "Gender",
    "Education_Level",
    "Employment_Status",
]

REQUIRED_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS + [TARGET]


def load_and_clean_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    #"""Charge le CSV, contrôle sa structure et supprime les doublons."""
    #df = pd.read_csv(data_path)
    #"""Charge depuis PostgreSQL (au lieu du CSV)."""
    engine = create_engine("postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db")
    df = pd.read_sql("SELECT * FROM patients_hypertension ORDER BY id", engine)
    df = df.drop(columns=["id"])
    # son code utilise des majuscules -> on renomme les colonnes
    df.columns = [c.title() if c != "bmi" else "BMI" for c in df.columns]
    df = df.rename(columns={"Bmi": "BMI", "Ldl": "LDL", "Hdl": "HDL",
                            "Systolic_Bp": "Systolic_BP", "Diastolic_Bp": "Diastolic_BP"})
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans le dataset : {missing_columns}")

    # On conserve uniquement les colonnes communes validées par le groupe.
    df = df[REQUIRED_COLUMNS].copy()

    # Conversion explicite des colonnes numériques pour détecter les erreurs de type.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")

    missing_values = df.isna().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        raise ValueError(f"Valeurs manquantes détectées :\n{missing_values}")

    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    target_values = set(df[TARGET].unique())
    if target_values != {"High", "Low"}:
        raise ValueError(f"Valeurs inattendues dans {TARGET} : {sorted(target_values)}")

    print(f"Lignes chargées              : {len(df) + duplicate_count}")
    print(f"Doublons supprimés           : {duplicate_count}")
    print(f"Valeurs manquantes           : {int(df.isna().sum().sum())}")
    print(f"Lignes après nettoyage       : {len(df)}")
    print(f"Variables numériques         : {len(NUMERIC_COLUMNS)}")
    print(f"Variables catégorielles      : {len(CATEGORICAL_COLUMNS)}")

    return df


#def split_data(df: pd.DataFrame) -> dict[str, pd.DataFrame | pd.Series]:
def split_data(df): 
    """Crée un découpage commun stratifié : 70 % train, 15 % dev, 15 % test."""
    x = df.drop(columns=[TARGET])
    y = df[TARGET]

    x_train, x_temp, y_train, y_temp = train_test_split(
        x,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    x_dev, x_test, y_dev, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    return {
        "X_train": x_train,
        "X_dev": x_dev,
        "X_test": x_test,
        "y_train": y_train,
        "y_dev": y_dev,
        "y_test": y_test,
    }


def build_preprocessor(scale_numeric: bool = False) -> ColumnTransformer:
    """Crée l'encodage commun et active la normalisation si le modèle en a besoin."""
    numeric_transformer = StandardScaler() if scale_numeric else "passthrough"

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
            ("numeric", numeric_transformer, NUMERIC_COLUMNS),
        ]
    )


#def prepare_common_data() -> tuple[dict[str, pd.DataFrame | pd.Series], ColumnTransformer]:
def prepare_common_data(): 
    #Retourne les trois jeux communs et le préprocesseur sans normalisation.
    df = load_and_clean_data()
    splits = split_data(df)
    preprocessor = build_preprocessor(scale_numeric=False)
    return splits, preprocessor


#def main() -> None:
def main(): 
    df = load_and_clean_data()
    splits = split_data(df)

    print("\nDécoupage commun :")
    print(f"Dtrain : {len(splits['X_train'])} lignes (70 %)")
    print(f"Ddev   : {len(splits['X_dev'])} lignes (15 %)")
    print(f"Dtest  : {len(splits['X_test'])} lignes (15 %)")

    # Démonstration de l'encodage sans fuite de données : apprentissage uniquement
    # sur Dtrain, puis transformation de Ddev et Dtest avec le même encodeur.
    preprocessor = build_preprocessor(scale_numeric=False)
    x_train_encoded = preprocessor.fit_transform(splits["X_train"])
    x_dev_encoded = preprocessor.transform(splits["X_dev"])
    x_test_encoded = preprocessor.transform(splits["X_test"])

    print("\nDimensions après encodage :")
    print(f"Dtrain : {x_train_encoded.shape}")
    print(f"Ddev   : {x_dev_encoded.shape}")
    print(f"Dtest  : {x_test_encoded.shape}")


if __name__ == "__main__":
    main()
