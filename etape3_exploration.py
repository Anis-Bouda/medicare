import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os

# 1. Création d'un dossier pour sauvegarder les graphiques de l'équipe
os.makedirs("graphiques_projet", exist_ok=True)

# ==========================================
# ÉTAPE 3 : ANALYSE EXPLORATOIRE (EDA)
# ==========================================

print("1. Connexion à PostgreSQL pour l'analyse exploratoire...")

engine = create_engine('postgresql+psycopg2://mehdib:Bourkeb2004@localhost/hypertension_db')
df = pd.read_sql("SELECT * FROM patients_hypertension;", engine)

print("Connexion réussie ! Génération des graphiques en cours...\n")

# Configuration de base pour l'esthétique des graphiques
sns.set_theme(style="whitegrid")

# --- GRAPHIQUE 1 : Répartition globale High / Low ---
print("Génération du graphique 1/4 (Répartition des classes)...")
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='hypertension', hue='hypertension', palette=['#e74c3c', '#2ecc71'], legend=False)
plt.title('Répartition des classes (Hypertension)')
plt.savefig("graphiques_projet/1_repartition_classes.png")
plt.close()

# --- GRAPHIQUE 2 : Taux de risque par pays ---
print("Génération du graphique 2/4 (Risque par pays)...")
plt.figure(figsize=(12, 6))
df_pays = df.copy()
# On transforme la colonne en 1 (High) et 0 (Low) pour calculer la moyenne facilement
df_pays['is_high'] = (df_pays['hypertension'] == 'High').astype(int)
taux_pays = df_pays.groupby('country')['is_high'].mean().sort_values(ascending=False) * 100

sns.barplot(x=taux_pays.index, y=taux_pays.values, hue=taux_pays.index, palette="viridis", legend=False)
plt.xticks(rotation=45, ha='right')
plt.title('Taux de risque d\'hypertension élevé par pays (%)')
plt.ylabel('Pourcentage (%)')
plt.tight_layout()
plt.savefig("graphiques_projet/2_taux_par_pays.png")
plt.close()

# --- GRAPHIQUE 3 : Lien entre Âge et Hypertension ---
print("Génération du graphique 3/4 (Âge et Hypertension)...")
plt.figure(figsize=(8, 5))
# Création de tranches d'âge pour faciliter la lecture du graphique
df['age_group'] = pd.cut(df['age'], bins=[0, 30, 45, 60, 100], labels=['<30', '30-45', '45-60', '>60'])
sns.countplot(data=df, x='age_group', hue='hypertension', palette='muted')
plt.title('Hypertension selon les tranches d\'âge')
plt.savefig("graphiques_projet/3_age_hypertension.png")
plt.close()

# --- GRAPHIQUE 4 : Boxplot IMC (BMI) et Hypertension ---
print("Génération du graphique 4/4 (IMC et Hypertension)...")
plt.figure(figsize=(6, 5))
sns.boxplot(data=df, x='hypertension', y='bmi', hue='hypertension', palette='Set2', legend=False)
plt.title('Distribution de l\'IMC (BMI) selon l\'hypertension')
plt.savefig("graphiques_projet/4_imc_hypertension.png")
plt.close()

print("\n✅ Terminé ! Tous les graphiques sont sauvegardés dans le dossier 'graphiques_projet'.")
