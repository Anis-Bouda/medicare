import pandas as pd
import psycopg2
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sqlalchemy import create_engine
from outils_resultats import enregistrer_resultats
import os, joblib

#conn = psycopg2.connect(
#    host="localhost",
#    dbname="tension",
#    user="hell",
#    password="*****"
#)

#df = pd.read_sql("SELECT * FROM tension", conn)
#conn.close()

engine = create_engine("postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db")
df = pd.read_sql("SELECT * FROM patients_hypertension ORDER BY id", engine)
if "id" in df.columns:
    df = df.drop(columns=["id"])

df = df.drop_duplicates()
df = df.dropna()

df["hypertension"] = (
    df["hypertension"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({"low": 0, "high": 1})
)

df = df.dropna(subset=["hypertension"])
df["hypertension"] = df["hypertension"].astype(int)

X = df.drop("hypertension", axis=1)
y = df["hypertension"].values.astype(np.float64)

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

X_train = preprocess.fit_transform(X_train)
X_test = preprocess.transform(X_test)

if hasattr(X_train, "toarray"):
    X_train = X_train.toarray()
    X_test = X_test.toarray()


def sigmoid(x):
    x = np.clip(x, -50, 50)
    return 1 / (1 + np.exp(-x))


class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value


def leaf_weight(G, H, lambda_):
    return -G / (H + lambda_)


def gain(G, H, GL, HL, GR, HR, lambda_):
    return (
        (GL**2 / (HL + lambda_)) +
        (GR**2 / (HR + lambda_)) -
        (G**2 / (H + lambda_))
    )


def best_split(X, g, h, lambda_=1.0):
    best_gain = -np.inf
    best_feature = None
    best_threshold = None

    G = np.sum(g)
    H = np.sum(h)

    n_samples, n_features = X.shape

    for feature in range(n_features):
        thresholds = np.unique(X[:, feature])

        for t in thresholds:
            left = X[:, feature] <= t
            right = ~left

            if np.sum(left) == 0 or np.sum(right) == 0:
                continue

            GL = np.sum(g[left])
            HL = np.sum(h[left])

            GR = np.sum(g[right])
            HR = np.sum(h[right])

            score = gain(G, H, GL, HL, GR, HR, lambda_)

            if score > best_gain:
                best_gain = score
                best_feature = feature
                best_threshold = t

    return best_feature, best_threshold


def build_tree(X, g, h, depth=0, max_depth=3, lambda_=1.0):
    if depth >= max_depth or len(g) < 2:
        return Node(value=leaf_weight(np.sum(g), np.sum(h), lambda_))

    feature, threshold = best_split(X, g, h, lambda_)

    if feature is None:
        return Node(value=leaf_weight(np.sum(g), np.sum(h), lambda_))

    left = X[:, feature] <= threshold
    right = ~left

    if np.sum(left) == 0 or np.sum(right) == 0:
        return Node(value=leaf_weight(np.sum(g), np.sum(h), lambda_))

    left_node = build_tree(X[left], g[left], h[left], depth+1, max_depth, lambda_)
    right_node = build_tree(X[right], g[right], h[right], depth+1, max_depth, lambda_)

    return Node(feature, threshold, left_node, right_node)


def predict_tree(node, x):
    if node.value is not None:
        return node.value

    if x[node.feature] <= node.threshold:
        return predict_tree(node.left, x)
    return predict_tree(node.right, x)


def predict_xgboost(X, trees, lr=0.1):
    pred = np.zeros(len(X))

    for tree in trees:
        pred += lr * np.array([predict_tree(tree, x) for x in X])

    return sigmoid(pred)


def train_xgboost(X, y, n_estimators=10, lr=0.1, max_depth=3, lambda_=1.0):
    pred = np.zeros(len(y))
    trees = []

    pos = np.sum(y == 0)
    neg = np.sum(y == 1)
    scale_pos_weight = pos / neg

    for _ in range(n_estimators):
        p = sigmoid(pred)

        g = p - y
        h = p * (1 - p)

        weights = np.where(y == 1, scale_pos_weight, 1.0)

        g *= weights
        h *= weights

        tree = build_tree(X, g, h, max_depth=max_depth, lambda_=lambda_)
        trees.append(tree)

        update = np.array([predict_tree(tree, x) for x in X])
        pred += lr * update

    return trees


trees = train_xgboost(X_train, y_train)

y_proba = predict_xgboost(X_test, trees)

threshold = 0.5
y_pred = (y_proba >= threshold).astype(int)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_proba))

# ajoue fait pour comparer avec les autres modeles 
enregistrer_resultats("XGBoost final", y_test, y_pred, y_proba)
os.makedirs("artefacts/modeles", exist_ok=True)
joblib.dump(trees, "artefacts/modeles/XGBoost final.pkl")