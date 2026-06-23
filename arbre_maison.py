# arbre_maison.py
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from pretraitement import preparer_donnees


# recuperation des donnees preparees
X_train_np, X_dev_np, X_test_np, y_train_np, y_dev_np, y_test_np, preprocessor = preparer_donnees()

class ArbreDecisionMaison:
    def __init__(self, max_depth=20, min_samples_split=25):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.arbre = None

    # calcul de l'impurete gini
    def gini(self, y):
        classes, counts = np.unique(y, return_counts=True)
        proportions = counts / len(y)

        gini = 1
        for p in proportions:
            gini = gini - p**2

        return gini

    # classe majoritaire dans un groupe
    def classe_majoritaire(self, y):
        classes, counts = np.unique(y, return_counts=True)
        return classes[np.argmax(counts)]

    # separation des donnees selon une colonne et un seuil
    def split(self, X, y, colonne, seuil):
        indices_gauche = X[:, colonne] <= seuil
        indices_droite = X[:, colonne] > seuil

        X_gauche = X[indices_gauche]
        y_gauche = y[indices_gauche]

        X_droite = X[indices_droite]
        y_droite = y[indices_droite]

        return X_gauche, y_gauche, X_droite, y_droite

    # chercher la meilleure separation possible
    def meilleur_split(self, X, y):
        meilleur_gini = 1
        meilleure_colonne = None
        meilleur_seuil = None

        n_lignes, n_colonnes = X.shape

        for colonne in range(n_colonnes):
            valeurs_uniques = np.unique(X[:, colonne])

            # pour eviter que le code soit trop lent
            # on teste seulement quelques seuils
            if len(valeurs_uniques) > 10:
                seuils = np.percentile(valeurs_uniques, [10, 25, 50, 75, 90])
            else:
                seuils = valeurs_uniques

            for seuil in seuils:
                X_gauche, y_gauche, X_droite, y_droite = self.split(X, y, colonne, seuil)

                if len(y_gauche) == 0 or len(y_droite) == 0:
                    continue

                gini_gauche = self.gini(y_gauche)
                gini_droite = self.gini(y_droite)

                poids_gauche = len(y_gauche) / len(y)
                poids_droite = len(y_droite) / len(y)

                gini_total = poids_gauche * gini_gauche + poids_droite * gini_droite

                if gini_total < meilleur_gini:
                    meilleur_gini = gini_total
                    meilleure_colonne = colonne
                    meilleur_seuil = seuil

        return meilleure_colonne, meilleur_seuil

    # construction recursive de l'arbre
    def construire_arbre(self, X, y, profondeur):
        # condition d'arret 1 : profondeur maximale atteinte
        if profondeur >= self.max_depth:
            return self.classe_majoritaire(y)

        # condition d'arret 2 : pas assez de donnees pour continuer
        if len(y) < self.min_samples_split:
            return self.classe_majoritaire(y)

        # condition d'arret 3 : une seule classe restante
        if len(np.unique(y)) == 1:
            return y[0]

        colonne, seuil = self.meilleur_split(X, y)

        # si aucun split nest trouve
        if colonne is None:
            return self.classe_majoritaire(y)

        X_gauche, y_gauche, X_droite, y_droite = self.split(X, y, colonne, seuil)

        branche_gauche = self.construire_arbre(X_gauche, y_gauche, profondeur + 1)
        branche_droite = self.construire_arbre(X_droite, y_droite, profondeur + 1)

        noeud = {
            "colonne": colonne,
            "seuil": seuil,
            "gauche": branche_gauche,
            "droite": branche_droite
        }

        return noeud

    # entrainement du modele
    def fit(self, X, y):
        self.arbre = self.construire_arbre(X, y, profondeur=0)

    # prediction pour une seule ligne
    def predire_ligne(self, ligne, noeud):
        if not isinstance(noeud, dict):
            return noeud

        colonne = noeud["colonne"]
        seuil = noeud["seuil"]

        if ligne[colonne] <= seuil:
            return self.predire_ligne(ligne, noeud["gauche"])
        else:
            return self.predire_ligne(ligne, noeud["droite"])

    # prediction pour plusieurs lignes
    def predict(self, X):
        predictions = []

        for ligne in X:
            prediction = self.predire_ligne(ligne, self.arbre)
            predictions.append(prediction)

        return np.array(predictions)
    

# creation du modele
arbre_maison = ArbreDecisionMaison(
    max_depth=20,
    min_samples_split=25
)

# entrainement du modele
arbre_maison.fit(X_train_np, y_train_np)

# prediction sur dev
y_dev_pred = arbre_maison.predict(X_dev_np)

print("Predictions :")
print(y_dev_pred[:40])

print("Vraies valeurs :")
print(y_dev_np[:40])

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

#===============================
#   Sauvgarde des résultats pour les comparer plus-tard
#===============================
resultat = pd.DataFrame([{
    "modele": "Arbre de decision maison",
    "accuracy": accuracy_score(y_dev_np, y_dev_pred),
    "precision_high": precision_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "recall_high": recall_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "f1_high": f1_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
    "precision_low": precision_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
    "recall_low": recall_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
    "f1_low": f1_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0)
}])

resultat.to_csv("resultat_arbre_maison.csv", index=False)