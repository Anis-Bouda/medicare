import pandas as pd
from sqlalchemy import create_engine

# 1. Connexion à votre base de données locale
# L'URL contient votre nom d'utilisateur (mehdib) et le nom de la base (hypertension_db)
print("Connexion à PostgreSQL en cours...")
engine = create_engine('postgresql+psycopg2://mehdib:Bourkeb2004@localhost/hypertension_db')

# 2. Exécution de la requête et chargement dans Pandas
query = "SELECT * FROM patients_hypertension;"
df = pd.read_sql(query, engine)
print(f"✅ Données chargées : {df.shape[0]} lignes et {df.shape[1]} colonnes.")

# 3. Nettoyage de base (suppression de l'ID qui ne sert pas à prédire)
if 'id' in df.columns:
    df = df.drop(columns=['id'])

# 4. Encodage de la variable cible
# On remplace le texte par des chiffres pour les algorithmes
df['hypertension'] = df['hypertension'].map({'High': 1, 'Low': 0})

# 5. Séparation des caractéristiques (X) et de la cible (y)
X = df.drop(columns=['hypertension'])
y = df['hypertension']

print(f"✅ Préparation réussie !")
print(f"Dimensions de X (données patients) : {X.shape}")
print(f"Dimensions de y (cible à prédire) : {y.shape}")
