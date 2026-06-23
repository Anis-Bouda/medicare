# Projet de prédiction de l'hypertension

Branche de travail de Kenza contenant :

- la création et l'import de la base PostgreSQL ;
- la préparation commune des données ;
- l'analyse exploratoire ;
- le modèle Random Forest et ses résultats.

## Données

Placer `hypertension_dataset.csv` à la racine du projet. Le dataset n'est pas versionné dans Git.

## Préparation commune

```powershell
uv run --with pandas --with scikit-learn python data_preparation.py
```

## Analyse exploratoire

```powershell
uv run --with pandas --with matplotlib python exploratory_analysis.py
```

## Random Forest

```powershell
uv run --with pandas --with scikit-learn --with matplotlib --with joblib python random_forest_hypertension.py
```

Le modèle `.joblib` est généré localement dans `outputs` et n'est pas versionné en raison de sa taille.
