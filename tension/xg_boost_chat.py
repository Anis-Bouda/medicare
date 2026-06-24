import pandas as pd
import psycopg2
import numpy as np
import joblib
import matplotlib.pyplot as plt
import xgboost as xgb

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    StratifiedKFold
)

from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder
)

from sklearn.compose import ColumnTransformer

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


conn = psycopg2.connect(
    host="localhost",
    dbname="tension",
    user="hell",
    password="*****"
)

df = pd.read_sql("SELECT * FROM tension", conn)
conn.close()

print(f"\nNombre de lignes : {len(df):,}")


df = df.drop_duplicates()
df = df.dropna()

df["hypertension"] = (
    df["hypertension"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df["hypertension"] = df["hypertension"].map({
    "low": 0,
    "high": 1
})

df = df.dropna(subset=["hypertension"])

print("\nRépartition des classes")
print(df["hypertension"].value_counts())


print("\nColonnes :")
print(df.columns.tolist())

print("\nTypes :")
print(df.dtypes)

print("\nMoyennes numériques par classe :")
print(
    df.groupby("hypertension")
      .mean(numeric_only=True)
      .round(2)
)


X = df.drop("hypertension", axis=1)
y = df["hypertension"]


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

print("\nTaille des jeux")
print(f"Train : {len(X_train):,}")
print(f"Dev   : {len(X_dev):,}")
print(f"Test  : {len(X_test):,}")


num_cols = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

cat_cols = X.select_dtypes(
    include=["object"]
).columns.tolist()

print("\nVariables numériques :", len(num_cols))
print("Variables catégorielles :", len(cat_cols))

preprocess = ColumnTransformer(
    transformers=[
        (
            "num",
            StandardScaler(),
            num_cols
        ),
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            cat_cols
        )
    ]
)

X_train_proc = preprocess.fit_transform(X_train)
X_dev_proc = preprocess.transform(X_dev)
X_test_proc = preprocess.transform(X_test)

print("\nShape train :", X_train_proc.shape)


base_model = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="auc",

    n_estimators=1000,
    learning_rate=0.03,

    max_depth=6,
    min_child_weight=3,

    subsample=0.8,
    colsample_bytree=0.8,

    reg_alpha=0.1,
    reg_lambda=1.0,

    random_state=42,
    n_jobs=-1,

    early_stopping_rounds=50
)

print("\n==============================")
print("ENTRAINEMENT INITIAL")
print("==============================")

base_model.fit(
    X_train_proc,
    y_train,
    eval_set=[(X_dev_proc, y_dev)],
    verbose=50
)

print(
    "\nBest iteration :",
    base_model.best_iteration
)


print("\n==============================")
print("GRID SEARCH")
print("==============================")

param_grid = {
    "max_depth": [4, 6],
    "learning_rate": [0.03, 0.10],
    "min_child_weight": [1, 3],
    "subsample": [0.8],
    "colsample_bytree": [0.8]
}

grid_model = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="auc",
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)

grid_search = GridSearchCV(
    estimator=grid_model,
    param_grid=param_grid,
    scoring="roc_auc",
    cv=cv,
    verbose=2,
    n_jobs=-1
)

grid_search.fit(
    X_train_proc,
    y_train
)

print("\nMeilleurs paramètres :")
print(grid_search.best_params_)

print("\nMeilleure AUC CV :")
print(grid_search.best_score_)

best_model = grid_search.best_estimator_


print("\n==============================")
print("EVALUATION TEST")
print("==============================")

y_pred = best_model.predict(X_test_proc)

y_prob = best_model.predict_proba(
    X_test_proc
)[:, 1]

accuracy = accuracy_score(
    y_test,
    y_pred
)

auc = roc_auc_score(
    y_test,
    y_prob
)

print(f"\nAccuracy : {accuracy:.4f}")
print(f"AUC      : {auc:.4f}")

print("\nClassification report")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Low", "High"]
    )
)

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion matrix")
print(cm)

feature_names_num = num_cols

feature_names_cat = []

if len(cat_cols) > 0:
    feature_names_cat = (
        preprocess
        .named_transformers_["cat"]
        .get_feature_names_out(cat_cols)
        .tolist()
    )

all_features = (
    feature_names_num +
    feature_names_cat
)

importances = best_model.feature_importances_

fi_df = pd.DataFrame({
    "feature": all_features,
    "importance": importances
})

fi_df = fi_df.sort_values(
    "importance",
    ascending=False
)

print("\nTOP 20 FEATURES")
print(fi_df.head(20))


fig, axes = plt.subplots(
    1,
    2,
    figsize=(15, 6)
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Low", "High"]
)

disp.plot(
    ax=axes[0],
    colorbar=False
)

axes[0].set_title(
    "Confusion Matrix"
)

top15 = (
    fi_df.head(15)
    .sort_values("importance")
)

axes[1].barh(
    top15["feature"],
    top15["importance"]
)

axes[1].set_title(
    "Top 15 Features"
)

plt.tight_layout()
plt.savefig(
    "xgboost_resultats.png",
    dpi=300
)

plt.show()

joblib.dump(
    best_model,
    "xgboost_hypertension.pkl"
)

joblib.dump(
    preprocess,
    "preprocessor.pkl"
)

print("\nFichiers sauvegardés :")
print("- xgboost_hypertension.pkl")
print("- preprocessor.pkl")
print("- xgboost_resultats.png")
