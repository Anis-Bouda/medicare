# arbre_sklearn.py

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from preparation_commune import preparer_donnees
from outils_resultats import enregistrer_resultats
import os, joblib

# recuperation des donnees preparees
X_train_np, X_dev_np, X_test_np, y_train_np, y_dev_np, y_test_np, preprocessor = preparer_donnees()

# creation du modele
arbre_sklearn = DecisionTreeClassifier(
    criterion="gini",
    splitter="best",
    max_depth = 20,
    min_samples_split = 5,
    random_state=1
)

# entrainement
arbre_sklearn.fit(X_train_np, y_train_np)

# prediction
y_dev_pred = arbre_sklearn.predict(X_dev_np)

# evaluation
print("Accuracy :", accuracy_score(y_dev_np, y_dev_pred))
print("Precision High :", precision_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0))
print("Recall High :", recall_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0))
print("F1 High :", f1_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0))

print("Precision Low :", precision_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0))
print("Recall Low :", recall_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0))
print("F1 Low :", f1_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0))

print("Matrice de confusion :")
print(confusion_matrix(y_dev_np, y_dev_pred))

print("Rapport de classification :")
print(classification_report(y_dev_np, y_dev_pred, zero_division=0))

# sauvegarde pour comparaision

y_pred = arbre_sklearn.predict(X_test_np)
y_proba = arbre_sklearn.predict_proba(X_test_np)[:, 1]
enregistrer_resultats("Arbre sklearn", y_test_np, y_pred, y_proba)
os.makedirs("artefacts/modeles", exist_ok=True)
joblib.dump(arbre_sklearn, "artefacts/modeles/Arbre sklearn.pkl")