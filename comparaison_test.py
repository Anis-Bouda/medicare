import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from pretraitement import preparer_donnees
from majority_baseline import MajorityBaselineMaison
from arbre_maison import ArbreDecisionMaison

import matplotlib.pyplot as plt


# ===============================
# 1. Récupération des données
# ===============================

X_train_np, X_dev_np, X_test_np, y_train_np, y_dev_np, y_test_np, preprocessor = preparer_donnees()


# ===============================
# 2. Fonction d'évaluation
# ===============================

def evaluer_modele(nom_modele, y_true, y_pred):
    return {
        "modele": nom_modele,
        "accuracy": accuracy_score(y_true, y_pred),

        "precision_high": precision_score(y_true, y_pred, pos_label=1, zero_division=0),
        "recall_high": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "f1_high": f1_score(y_true, y_pred, pos_label=1, zero_division=0),

        "precision_low": precision_score(y_true, y_pred, pos_label=0, zero_division=0),
        "recall_low": recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        "f1_low": f1_score(y_true, y_pred, pos_label=0, zero_division=0)
    }


resultats = []


# ===============================
# 3. Modèle 1 : Majority Baseline
# ===============================

majority_model = MajorityBaselineMaison()
majority_model.fit(y_train_np)

y_test_pred_majority = majority_model.predict(X_test_np)

resultats.append(
    evaluer_modele(
        "Majority Baseline",
        y_test_np,
        y_test_pred_majority
    )
)

print("\n===============================")
print("Majority Baseline - Test")
print("===============================")
print(confusion_matrix(y_test_np, y_test_pred_majority))
print(classification_report(y_test_np, y_test_pred_majority, zero_division=0))


# ===============================
# 4. Modèle 2 : Arbre maison
# ===============================

arbre_maison = ArbreDecisionMaison(
    max_depth=20,
    min_samples_split=25
)

arbre_maison.fit(X_train_np, y_train_np)

y_test_pred_maison = arbre_maison.predict(X_test_np)

resultats.append(
    evaluer_modele(
        "Arbre de décision maison",
        y_test_np,
        y_test_pred_maison
    )
)

print("\n===============================")
print("Arbre maison - Test")
print("===============================")
print(confusion_matrix(y_test_np, y_test_pred_maison))
print(classification_report(y_test_np, y_test_pred_maison, zero_division=0))


# ===============================
# 5. Modèle 3 : Arbre sklearn
# ===============================

arbre_sklearn = DecisionTreeClassifier(
    criterion="gini",
    splitter="best",
    max_depth = 20,
    min_samples_split = 5,
    random_state=1
)

arbre_sklearn.fit(X_train_np, y_train_np)

y_test_pred_sklearn = arbre_sklearn.predict(X_test_np)

resultats.append(
    evaluer_modele(
        "Arbre de décision sklearn",
        y_test_np,
        y_test_pred_sklearn
    )
)

print("\n===============================")
print("Arbre sklearn - Test")
print("===============================")
print(confusion_matrix(y_test_np, y_test_pred_sklearn))
print(classification_report(y_test_np, y_test_pred_sklearn, zero_division=0))


# ===============================
# 6. Sauvegarde des résultats
# ===============================

df_resultats = pd.DataFrame(resultats)

print("\n===============================")
print("Comparaison finale sur Dtest")
print("===============================")
print(df_resultats)

df_resultats.to_csv("comparaison_modeles_test.csv", index=False)

# ===============================
# 7. Graphe de comparaison des modèles
# ===============================

# Métriques à comparer
metriques = [
    "accuracy",
    "precision_high",
    "recall_high",
    "f1_high",
    "precision_low",
    "recall_low",
    "f1_low"
]

plt.figure(figsize=(12, 6))

for i in range(len(df_resultats)):
    plt.plot(
        metriques,
        df_resultats.loc[i, metriques],
        marker="o",
        label=df_resultats.loc[i, "modele"]
    )

plt.title("Comparaison des performances des trois modèles sur l'ensemble de test")
plt.xlabel("Métriques")
plt.ylabel("Score")
plt.ylim(0, 1)
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("comparaison_modeles_courbe.png", dpi=300)
plt.show()