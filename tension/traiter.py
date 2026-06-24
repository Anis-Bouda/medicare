import pandas as pd
import psycopg2
from sklearn.preprocessing import LabelEncoder

conn = psycopg2.connect(
    host="localhost",
    dbname="tension",
    user="hell",
    password="*******"
)

df = pd.read_sql("SELECT * FROM tension", conn)

print("Valeurs manquantes :")
print(df.isnull().sum())

print("\nDoublons :", df.duplicated().sum())

df = df.drop_duplicates()
df = df.dropna()
df.to_csv("tension_clean.csv", index=False)

categorical_columns = [
    "country",
    "smoking_status",
    "physical_activity_level",
    "family_history",
    "diabetes",
    "gender",
    "education_level",
    "employment_status"
]

encoder = LabelEncoder()

for col in categorical_columns:
    df[col] = encoder.fit_transform(df[col])

df["hypertension"] = df["hypertension"].map({
    "Low": 0,
    "High": 1
})

X = df.drop("hypertension", axis=1)
y = df["hypertension"]

print("\nShape X :", X.shape)
print("Shape y :", y.shape)

conn.close()
