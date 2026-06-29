import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# ==========================================
# ÉTAPE 2 : CONNEXION ET PRÉPARATION
# ==========================================

print("1. Connexion à PostgreSQL...")

engine = create_engine('postgresql+psycopg2://mehdib:Bourkeb2004@localhost/hypertension_db')
data = pd.read_sql("SELECT * FROM patients_hypertension;", engine)

print(f"✅ Données chargées : {data.shape[0]} lignes et {data.shape[1]} colonnes.")

# Nettoyage de base (suppression de l'id)
if 'id' in data.columns:
    data = data.drop(columns=['id'])

print("\n2. Séparation et encodage (Méthode du groupe)...")
# Séparation X et y
X = data.drop(columns=["hypertension"])
y = data["hypertension"].map({"Low": 0, "High": 1})

# Définition des colonnes
colonnes_numeriques = ["age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp", "alcohol_intake", "stress_level", "salt_intake", "sleep_duration", "heart_rate", "ldl", "hdl", "triglycerides", "glucose"]
colonnes_categorielles = ["country", "smoking_status", "physical_activity_level", "family_history", "diabetes", "gender", "education_level", "employment_status"]

# Création du préprocesseur (Standardisation + OneHotEncoding)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles)
    ]
)

print("\n3. Découpage des jeux de données (Train/Dev/Test)...")
# 1ère séparation : 70% Train, 30% Temp
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
# 2ème séparation : 15% Dev, 15% Test
X_dev, X_test, y_dev, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

# Application du préprocesseur (Apprentissage uniquement sur Train !)
X_train_prepared = preprocessor.fit_transform(X_train)
X_dev_prepared = preprocessor.transform(X_dev)
X_test_prepared = preprocessor.transform(X_test)

print("✅ Préparation terminée !")
print(f"Dimensions X_train_prepared : {X_train_prepared.shape}")
print(f"Dimensions X_dev_prepared   : {X_dev_prepared.shape}")
print(f"Dimensions X_test_prepared  : {X_test_prepared.shape}")
