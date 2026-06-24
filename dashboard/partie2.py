import numpy as np
import pandas as pd 

data=pd.read_csv('hypertension_dataset.csv')
#pandas est construit sur la base de numpy
#la fonction shape retourne les dimensions de la table
print(data.shape)
#pour voir les colonne on peut faire:
print(data.columns)
#pour voir les premiers lignes de la table "je crois khemssa timenza il n'a pas mentionné combien exactement dans la vidéo"
#par exemple pour vois si notre
#print(data.head())
#si y a des colonnes qui nous interessent pas on fait
#pour les lignes on fait axis=0 not sure
#data = data.drop(['Country','Age'],axis=1)
#print(data.head())
# si on veut analyser les données on va utiliser describe
# qui va nous afficher les statistiques de base pour 
# chacune de nos colonnes numériques exemple : la moyenne d'age
# on aura un tableau : count, mean, std, min, max ,25%,50ù,75%
print(data.describe())
#on remarque qu'il nous manque pas de données la valeurs
#de count de toutes les colonnes est : 174982
#si jamais il nous manque des données on peut remplir
#les cases vides par des valeurs par defaut qu'on peut choisir
#avec fillna(la valeur qu'on veut)
#dans cette exemple j'ai choisi de remplir les cases vides par
#l'age moyen mais pour notre dataset nous on en a pas besoin
## data.fillna(data['Age'].mean())
#comme cela va corrompre notre dataset, vaut mieux ne pas
#le faire vaut mieux supprimer les lignes ou il nous manque des 
#données vaut mieux perdre quelques données que corrompre la 
# réalité des choses , axis=0 car on va eleminer des lignes
data = data.dropna(axis=0)
print(data.shape)
#pas de changement ce qui confirme que notre dataset est propre

# informations generales
print(data.info())

# verification des valeurs manquantes
print("Valeurs manquantes :")
print(data.isnull().sum())

# verification des doublons
print("Nombre de doublons :", data.duplicated().sum())

#separation de X "features" et la varible cible y "label" comme indique dans la video
#tel que X contiendra toutes les autres variable entrees :
#X=[Country,Age,BMI,Cholesterol,Systolic_BP,Diastolic_BP,
# Smoking_Status,Alcohol_Intake,Physical_Activity_Level,
# Family_History,Diabetes,Stress_Level,Salt_Intake,
# Sleep_Duration,Heart_Rate,LDL,HDL,Triglycerides,Glucose,
# Gender,Education_Level,Employment_Status]
#et y que la cible de l'hypertension
#y=[Hypertension]
X=data.drop(columns=["Hypertension"])
y=data["Hypertension"]

#encoder la variable hypertension par 1 ou 0
y = y.map({
    "Low": 0,
    "High": 1
})

#verifier les dimensions pour etre sur que la separation a
#ete effectue correctement et que la variable hyper a ete code
#pour x on doit avoir 174982 et 22
#pour y 174982 et une seule colonne 
print("Dimensions de X :", X.shape)
print("Dimensions de y :", y.shape)
#afficher les cinq premiers lignes des deux 
print("Aperçu de X :")
print(X.head())
print("Aperçu de y :")
print(y.head())
print("Répartition de y :")
print(y.value_counts())

#separons les variable cat et num pour ensuite les coder ou les
#normaliser
colonnes_numeriques = ["Age","BMI","Cholesterol","Systolic_BP","Diastolic_BP","Alcohol_Intake","Stress_Level","Salt_Intake","Sleep_Duration","Heart_Rate","LDL","HDL","Triglycerides","Glucose"]
colonnes_categorielles = ["Country","Smoking_Status","Physical_Activity_Level","Family_History","Diabetes","Gender","Education_Level","Employment_Status"]

#verifier que je n'ai rien oublié
#toutes_les_colonnes = set(X.columns)
#colonnes_selectionnees = set(colonnes_numeriques + colonnes_categorielles)

#print("Colonnes oubliées :", toutes_les_colonnes - colonnes_selectionnees)
#print("Colonnes en trop :", colonnes_selectionnees - toutes_les_colonnes)

#normalisations des variables numériques 
#X_num_scaled = X[colonnes_numeriques].copy()

#for col in colonnes_numeriques:
#    moyenne = X_num_scaled[col].mean()
#    ecart_type = X_num_scaled[col].std()

#    if ecart_type != 0:
#        X_num_scaled[col] = (X_num_scaled[col] - moyenne) / ecart_type
#    else:
#        X_num_scaled[col] = 0
        
#print(X_num_scaled.head())
#print(X_num_scaled.describe())
#codage des variables catégorielles
#X_cat_encoded = pd.DataFrame(index=X.index)

#for col in colonnes_categorielles:
#    valeurs_uniques = X[col].unique()
    
#    for valeur in valeurs_uniques:
#        nom_nouvelle_colonne = col + "_" + str(valeur)
#        X_cat_encoded[nom_nouvelle_colonne] = (X[col] == valeur).astype(int)

#print("Aperçu des variables catégorielles encodées manuellement :")
#print(X_cat_encoded.head())

#print("Nombre de colonnes créées :", X_cat_encoded.shape[1])
#print(X_cat_encoded.columns.tolist())

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

#pretraitement :
#StandardScaler pour les colonnes numeriques
#OneHotEncoder pour les colonnes categorielles

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles)
    ]
)
#X_prepared = preprocessor.fit_transform(X)
#print("Dimensions avant transformation :", X.shape)
#print("Dimensions après transformation :", X_prepared.shape)
#noms_colonnes = preprocessor.get_feature_names_out()

#print("Nombre de colonnes après transformation :", len(noms_colonnes))

#for col in noms_colonnes:
#    print(col)


# train/dev/test split
from sklearn.model_selection import train_test_split
#1er séparation :
#70% train
#30% temporaire, qui sera ensuite divisé en dev et test
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

#2eme séparation :
#X_temp = 30% du dataset
#on le coupe en deux : 15% dev et 15% test
X_dev, X_test, y_dev, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)


print("\nDimensions avant prétraitement :")
print("X_train :", X_train.shape)
print("X_dev :", X_dev.shape)
print("X_test :", X_test.shape)

print("\nRépartition de y_train :")
print(y_train.value_counts(normalize=True) * 100)

print("\nRépartition de y_dev :")
print(y_dev.value_counts(normalize=True) * 100)

print("\nRépartition de y_test :")
print(y_test.value_counts(normalize=True) * 100)

# important :
# fit_transform sur train seulement
# transform sur dev et test

#memme si nous n'avons pas encore entraîné de modèle, le préprocesseur
#doit lui aussi "apprendre" certaines informations à partir des données
#par exemple StandardScaler apprend la moyenne et l'écart-type des
#colonnes numériques et OneHotEncoder apprend les catégories présentes
#dans les colonnes catégorielles
#
#pour éviter que les données de dev et de test influencent cette étape
#on apprend le prétraitement uniquement sur X_train avec fit_transform()
#ensuite on applique exactement les mêmes règles à X_dev et X_test
#avec transform() sans réapprendre de nouvelles informations

X_train_prepared = preprocessor.fit_transform(X_train)
X_dev_prepared = preprocessor.transform(X_dev)
X_test_prepared = preprocessor.transform(X_test)
print("Dimensions apres pretraitement :")
print("X_train_prepared :", X_train_prepared.shape)
print("X_dev_prepared :", X_dev_prepared.shape)
print("X_test_prepared :", X_test_prepared.shape)

print("Meme nombre de colonnes train/dev/test :")
print(X_train_prepared.shape[1] == X_dev_prepared.shape[1] == X_test_prepared.shape[1])
noms_colonnes = preprocessor.get_feature_names_out()
print("Nombre de colonnes apres transformation :", len(noms_colonnes))