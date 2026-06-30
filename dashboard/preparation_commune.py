import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
#connexiion a la base 
URL = "postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db"

NUM = ["age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp",
       "alcohol_intake", "stress_level", "salt_intake", "sleep_duration",
       "heart_rate", "ldl", "hdl", "triglycerides", "glucose"]
CAT = ["country", "smoking_status", "physical_activity_level", "family_history",
       "diabetes", "gender", "education_level", "employment_status"]

#fonction preparer donne 
def preparer_donnees(numpy_out=True):
    #elle revoie les X et Y train dev et test et le preprocesseur 
    #elle fait un tri par id pour que lordre des donne soi identique pour tous les modeles 
    #elle decoupe les donne selon les meme proportions et elle encode high en 1 et low en 0 
    #pour que on puisse vraimen comparer entre les modeles il faut que tous soit le meme 
    
    engine = create_engine(URL)
    df = pd.read_sql("SELECT * FROM patients_hypertension ORDER BY id", engine)

    y = (df["hypertension"] == "High").astype(int)
    X = df.drop(columns=["hypertension", "id"])

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y)
    X_dev, X_test, y_dev, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
    ])

    X_train_p = preprocessor.fit_transform(X_train)
    X_dev_p   = preprocessor.transform(X_dev)
    X_test_p  = preprocessor.transform(X_test)

    if numpy_out:
        return (np.asarray(X_train_p), np.asarray(X_dev_p), np.asarray(X_test_p),
                y_train.values, y_dev.values, y_test.values, preprocessor)
    return X_train_p, X_dev_p, X_test_p, y_train, y_dev, y_test, preprocessor