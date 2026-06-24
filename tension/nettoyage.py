import pandas as pd
import psycopg2

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
import joblib


conn = psycopg2.connect(
    host="localhost",
    dbname="tension",
    user="hell",
    password="********"
)

df = pd.read_sql("SELECT * FROM tension", conn)
conn.close()

df = df.drop_duplicates()
df = df.dropna()

df["hypertension"] = df["hypertension"].str.lower().map({
    "low": 0,
    "high": 1
})

X = df.drop("hypertension", axis=1)
y = df["hypertension"]

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

X_dev, X_test, y_dev, y_test = train_test_split(
    X_temp, y_temp,
    test_size=0.5,
    random_state=42,
    stratify=y_temp
)

num_cols = X.select_dtypes(include=["int64", "float64"]).columns
cat_cols = X.select_dtypes(include=["object"]).columns

preprocess = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
])

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
}

best_model = None
best_score = 0

for name, model in models.items():

    clf = Pipeline([
        ("preprocess", preprocess),
        ("model", model)
    ])

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_dev)

    score = accuracy_score(y_dev, y_pred)

    print(name)
    print(score)

    if score > best_score:
        best_score = score
        best_model = clf

y_test_pred = best_model.predict(X_test)

print(best_score)
print(accuracy_score(y_test, y_test_pred))
print(roc_auc_score(y_test, y_test_pred))
print(confusion_matrix(y_test, y_test_pred))
print(classification_report(y_test, y_test_pred))

joblib.dump(best_model, "hypertension_model.pkl")
