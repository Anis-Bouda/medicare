import pandas as pd
import psycopg2
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

conn = psycopg2.connect(
    host="localhost",
    dbname="tension",
    user="hell",
    password="gojo357159"
)

df = pd.read_sql("SELECT * FROM tension", conn)
conn.close()

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
y = df["hypertension"].values

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

X_dev, X_test, y_dev, y_test = train_test_split(
    X_temp,
    y_temp,
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

X_train_np = preprocess.fit_transform(X_train)
X_dev_np = preprocess.transform(X_dev)
X_test_np = preprocess.transform(X_test)

if hasattr(X_train_np, "toarray"):
    X_train_np = X_train_np.toarray()
    X_dev_np = X_dev_np.toarray()
    X_test_np = X_test_np.toarray()


def sigmoid(x):
    x = np.clip(x, -20, 20)
    return 1 / (1 + np.exp(-x))


def gradient(y, p):
    return p - y


def hessian(p):
    return p * (1 - p)


eps = 1e-15
base_score = np.log((np.mean(y_train) + eps) / (1 - np.mean(y_train) + eps))


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
        G = np.sum(g)
        H = np.sum(h)
        return Node(value=leaf_weight(G, H, lambda_))

    feature, threshold = best_split(X, g, h, lambda_)

    if feature is None:
        G = np.sum(g)
        H = np.sum(h)
        return Node(value=leaf_weight(G, H, lambda_))

    left_mask = X[:, feature] <= threshold
    right_mask = ~left_mask

    if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
        G = np.sum(g)
        H = np.sum(h)
        return Node(value=leaf_weight(G, H, lambda_))

    left_node = build_tree(X[left_mask], g[left_mask], h[left_mask], depth+1, max_depth, lambda_)
    right_node = build_tree(X[right_mask], g[right_mask], h[right_mask], depth+1, max_depth, lambda_)

    return Node(feature, threshold, left_node, right_node)


def predict_tree(node, x):
    if node.value is not None:
        return node.value

    if x[node.feature] <= node.threshold:
        return predict_tree(node.left, x)
    else:
        return predict_tree(node.right, x)


def predict_xgboost(X, trees, lr=0.1):
    pred = np.zeros(len(X))

    for tree in trees:
        update = np.array([predict_tree(tree, x) for x in X])
        pred += lr * update

    return sigmoid(pred)


def train_xgboost(X, y, n_estimators=10, lr=0.1, max_depth=3, lambda_=1.0):
    pred = np.full(len(y), base_score)
    trees = []

    for _ in range(n_estimators):
        p = sigmoid(pred)

        g = p - y
        h = p * (1 - p)

        tree = build_tree(X, g, h, max_depth=max_depth, lambda_=lambda_)
        trees.append(tree)

        update = np.array([predict_tree(tree, x) for x in X])

        pred += lr * update

    return trees
trees = train_xgboost(X_train_np, y_train)
y_proba = predict_xgboost(X_test_np, trees)
y_pred = (y_proba >= 0.5).astype(int)
accuracy = np.mean(y_pred == y_test)
print("Accuracy:", accuracy)
def confusion_matrix_manual(y_true, y_pred):
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))

    return np.array([[tn, fp],
                     [fn, tp]])

cm = confusion_matrix_manual(y_test, y_pred)
print(cm)