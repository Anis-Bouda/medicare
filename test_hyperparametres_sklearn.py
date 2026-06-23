import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    balanced_accuracy_score
)

from pretraitement import preparer_donnees


X_train_np, X_dev_np, X_test_np, y_train_np, y_dev_np, y_test_np, preprocessor = preparer_donnees()

parametres = []

#criteres = ["gini"]
max_depths = [20, 30, 40, 50]
splitter="best",
min_samples_splits = [2, 5, 10]
min_samples_leafs = [1, 2, 5, 10]
ccp_alphas = 0.0,
#max_features_list = ["sqrt"]
#class_weights = ["balanced"]
criteres = ["gini"]
#max_depths = [10, 20, 30, 40]
#min_samples_splits = [10, 25, 50]
#min_samples_leafs = [1, 5, 10]
#ccp_alphas = [0.0, 0.0001]
random_state=1,
max_features_list = None,
class_weights = None,

total = (
    len(criteres)
    * len(max_depths)
    * len(min_samples_splits)
    * len(min_samples_leafs)
    * len(max_features_list)
    * len(class_weights)
    * len(ccp_alphas)
)

compteur = 0


for critere in criteres:
    for max_depth in max_depths:
        for min_samples_split in min_samples_splits:
            for min_samples_leaf in min_samples_leafs:
                for max_features in max_features_list:
                    for class_weight in class_weights:
                        for ccp_alpha in ccp_alphas:

                            compteur += 1
                            print(f"Test {compteur}/{total}")

                            modele = DecisionTreeClassifier(
                                criterion=critere,
                                splitter="best",
                                max_depth=max_depth,
                                min_samples_split=min_samples_split,
                                min_samples_leaf=min_samples_leaf,
                                max_features=max_features,
                                class_weight=class_weight,
                                ccp_alpha=ccp_alpha,
                                random_state=1
                            )

                            modele.fit(X_train_np, y_train_np)
                            y_pred = modele.predict(X_dev_np)

                            accuracy = accuracy_score(y_dev_np, y_pred)
                            balanced_acc = balanced_accuracy_score(y_dev_np, y_pred)

                            recall_high = recall_score(y_dev_np, y_pred, pos_label=1, zero_division=0)
                            recall_low = recall_score(y_dev_np, y_pred, pos_label=0, zero_division=0)

                            f1_high = f1_score(y_dev_np, y_pred, pos_label=1, zero_division=0)
                            f1_low = f1_score(y_dev_np, y_pred, pos_label=0, zero_division=0)

                            parametres.append({
                                "criterion": critere,
                                "max_depth": max_depth,
                                "min_samples_split": min_samples_split,
                                "min_samples_leaf": min_samples_leaf,
                                "max_features": max_features,
                                "class_weight": class_weight,
                                "ccp_alpha": ccp_alpha,
                                "accuracy": accuracy,
                                "balanced_accuracy": balanced_acc,
                                "recall_high": recall_high,
                                "recall_low": recall_low,
                                "f1_high": f1_high,
                                "f1_low": f1_low
                            })
                            
resultats = pd.DataFrame(parametres)

# Sauvegarde tous les essais
resultats.to_csv("resultats_hyperparametres_sklearn.csv", index=False)

# On garde seulement les modèles qui reconnaissent un minimum les deux classes
resultats_filtrees = resultats[
    (resultats["recall_high"] >= 0.70) &
    (resultats["recall_low"] >= 0.20)
]

print("Meilleurs modèles sans filtre selon balanced_accuracy :")
print(
    resultats
    .sort_values(by="balanced_accuracy", ascending=False)
    .head(20)
)

print("\nMeilleurs modèles sans filtre selon accuracy :")
print(
    resultats
    .sort_values(by="accuracy", ascending=False)
    .head(20)
)

print("\nMeilleurs modèles sans filtre selon recall_low :")
print(
    resultats
    .sort_values(by="recall_low", ascending=False)
    .head(20)
)

print("Meilleure accuracy :", resultats["accuracy"].max())
print("Meilleure balanced_accuracy :", resultats["balanced_accuracy"].max())
print("Meilleur recall_high :", resultats["recall_high"].max())
print("Meilleur recall_low :", resultats["recall_low"].max())
print("Meilleur f1_low :", resultats["f1_low"].max())