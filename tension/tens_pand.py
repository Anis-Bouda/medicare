import pandas as pd
import psycopg2

data = pd.read_csv("hypertension_dataset.csv")

data = data.rename(columns={
    "Country": "country",
    "Age": "age",
    "BMI": "bmi",
    "Cholesterol": "cholesterol",
    "Systolic_BP": "systolic_bp",
    "Diastolic_BP": "diastolic_bp",
    "Smoking_Status": "smoking_status",
    "Alcohol_Intake": "alcohol_intake",
    "Physical_Activity_Level": "physical_activity_level",
    "Family_History": "family_history",
    "Diabetes": "diabetes",
    "Stress_Level": "stress_level",
    "Salt_Intake": "salt_intake",
    "Sleep_Duration": "sleep_duration",
    "Heart_Rate": "heart_rate",
    "LDL": "ldl",
    "HDL": "hdl",
    "Triglycerides": "triglycerides",
    "Glucose": "glucose",
    "Gender": "gender",
    "Education_Level": "education_level",
    "Employment_Status": "employment_status",
    "Hypertension": "hypertension"
})

numeric_columns = [
    "age",
    "bmi",
    "cholesterol",
    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "glucose",
    "ldl",
    "hdl",
    "triglycerides",
    "alcohol_intake",
    "stress_level",
    "salt_intake",
    "sleep_duration"
]

for col in numeric_columns:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

data = data.dropna()

conn = psycopg2.connect(
    host="localhost",
    dbname="tension",
    user="hell",
    password="******"
)

cursor = conn.cursor()

columns = list(data.columns)

sql = f"""
INSERT INTO tension ({', '.join(columns)})
VALUES ({', '.join(['%s'] * len(columns))})
"""

data = [tuple(row) for row in data.itertuples(index=False, name=None)]

cursor.executemany(sql, data)
conn.commit()

print(f"Import terminé : {cursor.rowcount} lignes insérées.")

cursor.close()
conn.close()
