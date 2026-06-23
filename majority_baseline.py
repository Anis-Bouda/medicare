# majority_baseline.py

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from pretraitement import preparer_donnees


class MajorityBaselineMaison:
    def __init__(self):
        self.classe_majoritaire = None

    def fit(self, y):
        classes, counts = np.unique(y, return_counts=True)
        indice_max = np.argmax(counts)
        self.classe_majoritaire = classes[indice_max]

        print("Classes :", classes)
        print("Effectifs :", counts)
        print("Classe majoritaire apprise :", self.classe_majoritaire)

    def predict(self, X):
        n_lignes = X.shape[0]
        predictions = np.full(
            shape=n_lignes,
            fill_value=self.classe_majoritaire
        )
        return predictions


# recuperation des donnees preparees
X_train_np, X_dev_np, X_test_np, y_train_np, y_dev_np, y_test_np, preprocessor = preparer_donnees()

# creation et entrainement du modele
majority_model = MajorityBaselineMaison()
majority_model.fit(y_train_np)

# prediction sur dev
y_dev_pred = majority_model.predict(X_dev_np)

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

# sauvegarde
resultat = pd.DataFrame([{
    "modele": "Majority Baseline maison",
    "accuracy": accuracy_score(y_dev_np, y_dev_pred),
    "precision_high": precision_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "recall_high": recall_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "f1_high": f1_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "precision_low": precision_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
    "recall_low": recall_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
    "f1_low": f1_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0)
}])

resultat.to_csv("resultat_majority_baseline.csv", index=False)