# MediCare — Prédiction du risque d'hypertension

Application complète de prédiction du risque d'hypertension (**High** / **Low**) à partir de données médicales, démographiques et liées au mode de vie. Le projet compare **dix modèles** de Machine Learning sur un même jeu de données, avec un dashboard interactif développé en Streamlit.

> Projet réalisé en groupe — Licence Informatique, Université Sorbonne Paris Nord (Groupe 9).
Membre :
Anis BOUDA 
Elina Imane HADJAM 
Syndia TOUTOU  
Kenza LOUNIS  
Mehdi BOURKEB  

> Il s'agit d'un outil pédagogique et indicatif, **pas** d'un outil de diagnostic médical.


---

## Aperçu

Le projet couvre toute la chaîne, du stockage des données à la prédiction :

- centralisation des données dans une base **PostgreSQL** (174 982 patients, 23 variables) ;
- préparation commune des données (découpage train / dev / test identique pour tous les modèles) ;
- entraînement et comparaison de **dix modèles** de Machine Learning ;
- dashboard **Streamlit** interactif : analyse, comparaison, prédiction, ajoue et suppression de modeles, avis d'un medecin  ;
- système d'**authentification à quatre rôles** (patient, développeur, médecin, administrateur).

**Résultat principal :** tous les modèles obtiennent une AUC proche de **0.50**, ce qui montre que le dataset contient peu de signal exploitable pour séparer les classes. C'est une conclusion assumée : un modèle avancé ne compense pas un dataset peu discriminant.

---

## Fonctionnalités

- **Analyse exploratoire** : répartition du risque, carte du monde par pays, tranches d'âge, facteurs médicaux (boxplot, histogramme, densité).
- **Comparaison des modèles** : tableau des métriques, accuracy, AUC, recall par classe, F1, matrices de confusion.
- **Prédiction individuelle** : saisie des données d'un patient, les dix modèles donnent leur avis en temps réel.
- **Authentification** : quatre rôles avec permissions différentes, mots de passe chiffrés (bcrypt), validation des rôles par email.
- **Avis médical** : un patient peut demander un avis, un médecin peut y répondre.

---

## Les modèles comparés

| Modèle | Type |
|---|---|
| MLP | Réseau de neurones (PyTorch) |
| MLP pos_weight | MLP avec pondération du déséquilibre |
| Arbre de décision (maison) | Codé à la main |
| Arbre de décision (sklearn) | Scikit-learn |
| Régression logistique | Codée à la main |
| Random Forest | Scikit-learn (Pipeline) |
| Random Forest amélioré | Avec variables dérivées |
| XGBoost | Librairie XGBoost |
| XGBoost final | Codé à la main |
| XGBoost maison | Codé à la main |

Tous les modèles sont évalués avec les **mêmes métriques** sur le **même jeu de test**, pour une comparaison équitable.

---

## Stack technique

- **Python 3.9**
- **PostgreSQL** — base de données
- **PyTorch** — réseau de neurones (MLP)
- **scikit-learn** — préparation des données, modèles classiques, métriques
- **XGBoost** — modèles de boosting
- **pandas / NumPy** — manipulation des données
- **Streamlit** — dashboard interactif
- **Plotly / Matplotlib** — graphiques
- **SQLAlchemy** — connexion à la base
- **bcrypt** — sécurité des mots de passe

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Anis-Bouda/medicare.git
cd medicare/dashboard
```

### 2. Installer les dépendances

```bash
pip install streamlit pandas numpy scikit-learn xgboost torch sqlalchemy psycopg2-binary plotly matplotlib bcrypt joblib
```

### 3. Préparer la base PostgreSQL

Assure-toi que PostgreSQL est installé et lancé. Le script d'initialisation crée la base et toutes les tables si elles n'existent pas :

```bash
python init_bdd.py
```

> il faut changer les donnes et  l'utilisateur PostgreSQL en haut de `init_bdd.py` 

### 4. Importer le dataset

Le dataset des patients doit être importé dans la table `patients_hypertension`. 

---

## Lancement

Depuis le dossier `dashboard/` :

```bash
streamlit run medicare.py
```

## Remarques

- Le **Random Forest.pkl**  n'est pas inclus dans le dépôt car trop grand pour git . Il peut être régénéré avec `python random_forest_hypertension.py`.
- Le fichier `email_utils.py` qui sert a envoyer les mails est fourni mais sans identifiants (mdps) pour des raisons de sécurité. 
