import os
import pandas as pd
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)

FICHIER = "resultats/metrics.csv"
#) cets low et 1 cest high
def enregistrer_resultats(nom, y_true, y_pred, y_proba):
    os.makedirs("resultats", exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])   
    rec_low  = cm[0, 0] / cm[0].sum() if cm[0].sum() else 0
    rec_high = cm[1, 1] / cm[1].sum() if cm[1].sum() else 0

    ligne = {
        "modele": nom,
        "accuracy":  round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "rappel":    round(recall_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "f1":        round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "auc":       round(roc_auc_score(y_true, y_proba), 4),
        "recall_low":  round(rec_low, 4),
        "recall_high": round(rec_high, 4),
        # les case de notre matrice de confusion 
        "low_low":   int(cm[0, 0]), "low_high":  int(cm[0, 1]),
        "high_low":  int(cm[1, 0]), "high_high": int(cm[1, 1]),
    }
    if os.path.exists(FICHIER):
        df = pd.read_csv(FICHIER)
        df = df[df["modele"] != nom]
        df = pd.concat([df, pd.DataFrame([ligne])], ignore_index=True)
    else:
        df = pd.DataFrame([ligne])
    df.to_csv(FICHIER, index=False)
    print(f"Résultats enregistrés : '{nom}'")