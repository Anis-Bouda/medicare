import numpy as np
import pandas as pd 
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# on importe les fonction de sklearn
# train_test_split sert a separer les donnees en train dev et test
# StandardScaler sert a normaliser les variables numerique
# OneHotEncoder sert a transformer les variables categorielle en 0 et 1
# ColumnTransformer permet dappliquer chaque traitement sur les bonne colonnes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# =========================
# chargement du dataset
# =========================

# on lit le fichier csv avec pandas
data = pd.read_csv("hypertension_dataset.csv")

# pandas est construit sur la base de numpy
# la fonction shape retourne les dimensions de la table
print(data.shape)

# pour voir les colonnes on peut faire
print(data.columns)

# si on veut analyser les donnees on utilise describe
# ca affiche les statistiques de base pour chaque colonne numerique
# exemple count mean std min max 25 50 75
print(data.describe())

# on remarque que il ne manque pas de donnees car la valeur count
# de toutes les colonnes est 174982

# si jamais il manque des donnees on peut les remplir avec fillna
# par exemple avec l age moyen mais ici on ne le fait pas
# data.fillna(data["Age"].mean())

# ici je prefere supprimer les lignes avec des valeurs manquantes
# axis 0 veut dire quon supprime des lignes
data = data.dropna(axis=0)

# on verifie si la taille a change
print(data.shape)

# informations generales sur le dataset
print(data.info())

# verification des valeurs manquantes
print("Valeurs manquantes :")
print(data.isnull().sum())

# verification des doublons
print("Nombre de doublons :", data.duplicated().sum())

# =========================
# separation de X et y
# =========================

# X contient toutes les variables explicatives
# donc toutes les colonnes sauf Hypertension
X = data.drop(columns=["Hypertension"])

# y contient seulement la variable cible
# donc ici cest la colonne Hypertension
y = data["Hypertension"]

# ici on encode la variable cible
# Low devient 0
# High devient 1
y = y.map({
    "Low": 0,
    "High": 1
})

# on verifie les dimensions pour etre sur que la separation est correcte
print("Dimensions de X :", X.shape)
print("Dimensions de y :", y.shape)

# afficher les cinq premieres lignes de X et y
print("Apercu de X :")
print(X.head())

print("Apercu de y :")
print(y.head())

# voir combien on a de 0 et de 1
print("Repartition de y :")
print(y.value_counts())


# =========================
# separation des colonnes numerique et categorielle
# =========================

# ici je separe les variables numerique et categorielle
# les variables numerique seront normalisees
# les variables categorielle seront codees avec OneHotEncoder

colonnes_numeriques = [
    "Age",
    "BMI",
    "Cholesterol",
    "Systolic_BP",
    "Diastolic_BP",
    "Alcohol_Intake",
    "Stress_Level",
    "Salt_Intake",
    "Sleep_Duration",
    "Heart_Rate",
    "LDL",
    "HDL",
    "Triglycerides",
    "Glucose"
]

colonnes_categorielles = [
    "Country",
    "Smoking_Status",
    "Physical_Activity_Level",
    "Family_History",
    "Diabetes",
    "Gender",
    "Education_Level",
    "Employment_Status"
]


# verification pour etre sur que je nai pas oublie une colonne
toutes_les_colonnes = set(X.columns)
colonnes_selectionnees = set(colonnes_numeriques + colonnes_categorielles)

print("Colonnes oubliees :", toutes_les_colonnes - colonnes_selectionnees)
print("Colonnes en trop :", colonnes_selectionnees - toutes_les_colonnes)


# =========================
# ancienne methode manuelle gardee en commentaire
# =========================

# normalisation manuelle des variables numeriques
# X_num_scaled = X[colonnes_numeriques].copy()

# for col in colonnes_numeriques:
#     moyenne = X_num_scaled[col].mean()
#     ecart_type = X_num_scaled[col].std()

#     if ecart_type != 0:
#         X_num_scaled[col] = (X_num_scaled[col] - moyenne) / ecart_type
#     else:
#         X_num_scaled[col] = 0

# print(X_num_scaled.head())
# print(X_num_scaled.describe())


# codage manuel des variables categorielle
# X_cat_encoded = pd.DataFrame(index=X.index)

# for col in colonnes_categorielles:
#     valeurs_uniques = X[col].unique()
    
#     for valeur in valeurs_uniques:
#         nom_nouvelle_colonne = col + "_" + str(valeur)
#         X_cat_encoded[nom_nouvelle_colonne] = (X[col] == valeur).astype(int)

# print("Apercu des variables categorielle encodees manuellement :")
# print(X_cat_encoded.head())

# print("Nombre de colonnes creees :", X_cat_encoded.shape[1])
# print(X_cat_encoded.columns.tolist())


# =========================
# train dev test split
# =========================

# ici on separe les donnees en 3 parties
# train va servir plus tard a entrainer le modele
# dev va servir a comparer les modeles et faire des choix
# test va servir a la fin pour evaluer le meilleur modele
# on ne touche pas au test avant la fin

# premiere separation
# on garde 70 pourcent des donnees pour le train
# et 30 pourcent dans une variable temporaire
# cette variable temporaire va contenir dev et test ensemble

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# deuxieme separation
# on coupe les 30 pourcent restant en deux
# donc on aura 15 pourcent pour dev
# et 15 pourcent pour test

X_dev, X_test, y_dev, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

# stratify permet de garder presque la meme repartition de high et low
# dans train dev et test
# comme notre dataset nest pas totalement equilibre cest important

# random_state permet davoir toujours la meme separation
# comme ca si on relance le code on retrouve les meme resultats

print("Dimensions avant pretraitement :")
print("X_train :", X_train.shape)
print("X_dev :", X_dev.shape)
print("X_test :", X_test.shape)

print("y_train :", y_train.shape)
print("y_dev :", y_dev.shape)
print("y_test :", y_test.shape)

print("Repartition de y_train :")
print(y_train.value_counts(normalize=True) * 100)

print("Repartition de y_dev :")
print(y_dev.value_counts(normalize=True) * 100)

print("Repartition de y_test :")
print(y_test.value_counts(normalize=True) * 100)


# =========================
# pretraitement avec sklearn
# =========================

# ici on cree le preprocesseur
# il va faire deux traitements differents
# pour les colonnes numerique il va appliquer StandardScaler
# pour les colonnes categorielle il va appliquer OneHotEncoder

# StandardScaler normalise les colonnes numerique
# il transforme les valeurs avec la moyenne et l ecart type

# OneHotEncoder transforme les colonnes texte en colonnes 0 et 1
# par exemple Gender Female devient une colonne Gender_Female

# ColumnTransformer applique chaque traitement sur les bonnes colonnes
# StandardScaler seulement sur les colonnes numerique
# OneHotEncoder seulement sur les colonnes categorielle

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles)
    ]
)

# si dans dev ou test il trouve une categorie qui nexiste pas dans train
# il ne va pas creer une nouvelle colonne
# car les colonnes doivent rester les meme que celles du train
# grace a handle_unknown ignore il va juste ignorer cette categorie
# comme ca le code ne plante pas

# meme si on a pas encore fait le modele le preprocesseur apprend aussi des info
# StandardScaler apprend la moyenne et l ecart type des colonnes numerique
# OneHotEncoder apprend les categories presentes dans les colonnes categorielle

# pour eviter que dev et test influencent cette etape
# on apprend le pretraitement seulement sur le train avec fit_transform
# ensuite on applique les meme regles sur dev et test avec transform

X_train_prepared = preprocessor.fit_transform(X_train)
X_dev_prepared = preprocessor.transform(X_dev)
X_test_prepared = preprocessor.transform(X_test)


# =========================
# verification apres pretraitement
# =========================

print("Dimensions apres pretraitement :")
print("X_train_prepared :", X_train_prepared.shape)
print("X_dev_prepared :", X_dev_prepared.shape)
print("X_test_prepared :", X_test_prepared.shape)

# recuperer les noms des colonnes apres transformation
noms_colonnes = preprocessor.get_feature_names_out()

print("Nombre de colonnes apres transformation :", len(noms_colonnes))

print("Noms des colonnes apres transformation :")
for col in noms_colonnes:
    print(col)


# =========================
# conversion optionnelle en dataframe
# =========================

# cette partie nest pas obligatoire pour entrainer un modele
# mais ca permet de voir les donnees apres pretraitement comme un tableau pandas

X_train_prepared_df = pd.DataFrame(
    X_train_prepared.toarray() if hasattr(X_train_prepared, "toarray") else X_train_prepared,
    columns=noms_colonnes,
    index=X_train.index
)

X_dev_prepared_df = pd.DataFrame(
    X_dev_prepared.toarray() if hasattr(X_dev_prepared, "toarray") else X_dev_prepared,
    columns=noms_colonnes,
    index=X_dev.index
)

X_test_prepared_df = pd.DataFrame(
    X_test_prepared.toarray() if hasattr(X_test_prepared, "toarray") else X_test_prepared,
    columns=noms_colonnes,
    index=X_test.index
)

print("Apercu de X_train apres pretraitement :")
print(X_train_prepared_df.head())


# =========================
# verification finale
# =========================

# on verifie quil ny a pas de valeurs manquantes apres le pretraitement
print("Valeurs manquantes dans X_train_prepared :", X_train_prepared_df.isnull().sum().sum())
print("Valeurs manquantes dans X_dev_prepared :", X_dev_prepared_df.isnull().sum().sum())
print("Valeurs manquantes dans X_test_prepared :", X_test_prepared_df.isnull().sum().sum())

# on verifie que train dev et test ont le meme nombre de colonnes
print("Meme nombre de colonnes dans train dev test :")
print(X_train_prepared.shape[1] == X_dev_prepared.shape[1] == X_test_prepared.shape[1])

# =========================
# conversion en numpy
# =========================

X_train_np = X_train_prepared.toarray() if hasattr(X_train_prepared, "toarray") else X_train_prepared
X_dev_np = X_dev_prepared.toarray() if hasattr(X_dev_prepared, "toarray") else X_dev_prepared
X_test_np = X_test_prepared.toarray() if hasattr(X_test_prepared, "toarray") else X_test_prepared

y_train_np = y_train.values
y_dev_np = y_dev.values
y_test_np = y_test.values

# =========================
# arbre de decision avec sklearn
# =========================

# creation du modele
#arbre_sklearn = DecisionTreeClassifier(
#    criterion="gini",
#    max_depth=20,
#    min_samples_split=25,
#    random_state=42
#)

# entrainement sur le train
#arbre_sklearn.fit(X_train_np, y_train_np)

# prediction sur dev
#y_dev_pred = arbre_sklearn.predict(X_dev_np)

#print("Predictions :")
#print(y_dev_pred[:40])

#print("Vraies valeurs :")
#print(y_dev_np[:40])

#print("Accuracy :", accuracy_score(y_dev_np, y_dev_pred))
#print("Precision High :", precision_score(y_dev_np, y_dev_pred, pos_label=1))
#print("Recall High :", recall_score(y_dev_np, y_dev_pred, pos_label=1))
#print("F1 High :", f1_score(y_dev_np, y_dev_pred, pos_label=1))

#print("Precision Low :", precision_score(y_dev_np, y_dev_pred, pos_label=0))
#print("Recall Low :", recall_score(y_dev_np, y_dev_pred, pos_label=0))
#print("F1 Low :", f1_score(y_dev_np, y_dev_pred, pos_label=0))

#print("Matrice de confusion :")
#print(confusion_matrix(y_dev_np, y_dev_pred))

#print("Rapport de classification :")
#print(classification_report(y_dev_np, y_dev_pred))

#criteres = ["gini", "entropy", "log_loss"]
criteres =["gini"]

for critere in criteres:
    print("=" * 50)
    print("Critere :", critere)

#max : plus la valeur est petite plus l'arbre sera simple
#plus la valeur est grande plus l'arbre sera complexe => surentrainement
#min : plus la valeur est petite plus l'arbre sera complexe => surentrainement
#plus la valeur est grande plus l'arbre sera simple
    #arbre_sklearn = DecisionTreeClassifier(
    #    criterion=critere,
    #    splitter="best",
    #    min_samples_leaf=2,
    #    min_weight_fraction_leaf=,
    #    max_features=,
    #    max_leaf_nodes=,
    #    min_impurity_decrease=0.5,
    #    class_weight="balanced",
    #    ccp_alpha=,
    #    max_depth=10,
    #    min_samples_split=5,
    #    random_state=1
    #)

    #arbre_sklearn.fit(X_train_np, y_train_np)
    #y_dev_pred = arbre_sklearn.predict(X_dev_np)

    #print("Accuracy :", accuracy_score(y_dev_np, y_dev_pred))
    #print("Recall High :", recall_score(y_dev_np, y_dev_pred, pos_label=1))
    #print("Recall Low :", recall_score(y_dev_np, y_dev_pred, pos_label=0))
    #print("F1 High :", f1_score(y_dev_np, y_dev_pred, pos_label=1))
    #print("F1 Low :", f1_score(y_dev_np, y_dev_pred, pos_label=0))
    #print("Matrice de confusion :")
    #print(confusion_matrix(y_dev_np, y_dev_pred))
    #print(arbre_sklearn.feature_importances_)
    #print(arbre_sklearn.tree_)
    
#===============================
#   Sauvgarde des résultats pour les comparer plus-tard
#===============================
#resultat = pd.DataFrame([{
#    "modele": "Arbre de decision sklearn",
#    "accuracy": accuracy_score(y_dev_np, y_dev_pred),
#    "precision_high": precision_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
#    "recall_high": recall_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
#    "f1_high": f1_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
#    "precision_low": precision_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
#    "recall_low": recall_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
#    "f1_low": f1_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0)
#}])

#resultat.to_csv("resultat_arbre_sklearn.csv", index=False)

criteres = ["gini", "entropy"]
min_samples_leafs = [1, 2, 5, 10]
min_weight_fraction_leafs = [0.0 , 0.3 , 0.5 , 0.8 , 1]
max_features_list = [None, "sqrt", "log2"]
max_leaf_nodes_list = [None, 10, 20, 50, 100]
min_impurity_decreases = [0.0, 0.001, 0.01]
ccp_alphas = [0.0, 0.001, 0.01]
max_depths = [5, 10, 15, 20, None]
min_samples_splits = [2, 5, 10, 25, 50]
class_weights = [None, "balanced"]

resultats = []

for critere in criteres:
    for leaf in min_samples_leafs:
        for weight_fraction in min_weight_fraction_leafs:
            for max_feat in max_features_list:
                for max_leaf in max_leaf_nodes_list:
                    for impurity in min_impurity_decreases:
                        for alpha in ccp_alphas:
                            for depth in max_depths:
                                for split in min_samples_splits:
                                    for class_w in class_weights:

                                        arbre_sklearn = DecisionTreeClassifier(
                                            criterion=critere,
                                            splitter="best",
                                            min_samples_leaf=leaf,
                                            min_weight_fraction_leaf=weight_fraction,
                                            max_features=max_feat,
                                            max_leaf_nodes=max_leaf,
                                            min_impurity_decrease=impurity,
                                            class_weight=class_w,
                                            ccp_alpha=alpha,
                                            max_depth=depth,
                                            min_samples_split=split,
                                            random_state=1
                                        )

                                        arbre_sklearn.fit(X_train_np, y_train_np)
                                        y_dev_pred = arbre_sklearn.predict(X_dev_np)

                                        resultats.append({
                                            "criterion": critere,
                                            "min_samples_leaf": leaf,
                                            "min_weight_fraction_leaf": weight_fraction,
                                            "max_features": max_feat,
                                            "max_leaf_nodes": max_leaf,
                                            "min_impurity_decrease": impurity,
                                            "class_weight": class_w,
                                            "ccp_alpha": alpha,
                                            "max_depth": depth,
                                            "min_samples_split": split,
                                            "accuracy": accuracy_score(y_dev_np, y_dev_pred),
                                            "recall_high": recall_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
                                            "recall_low": recall_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0),
                                            "f1_high": f1_score(y_dev_np, y_dev_pred, pos_label=1, zero_division=0),
                                            "f1_low": f1_score(y_dev_np, y_dev_pred, pos_label=0, zero_division=0)
                                        })

resultats_df = pd.DataFrame(resultats)

print(resultats_df.sort_values(by="f1_low", ascending=False).head(10))

resultats_df.to_csv("comparaison_parametres_arbre.csv", index=False)

