import streamlit as st
from donnees import charger_donnees

st.set_page_config(page_title="Medicare - Hypertension", layout="wide")

# un entete
st.title(" Medicare — Prédiction du risque d'hypertension")
st.markdown("#### Analyse de 174 982 patients et comparaison de 6 modèles de Machine Learning")

st.markdown("""
Ce dashboard explore un jeu de données médicales pour prédire le risque
d'hypertension (**High** ou **Low**) et comparer plusieurs modèles de
classification.
""")

st.divider()

# donnes importante
df = charger_donnees()
st.subheader("Le dataset en un coup d'œil")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Patients", f"{len(df):,}".replace(",", " "))
c2.metric("Variables", df.shape[1] - 1)
c3.metric("Pays", df["country"].nunique())
c4.metric("Risque élevé", f"{(df['hypertension']=='High').mean()*100:.1f}%")

st.divider()

# explication bref des page
st.subheader("Comment naviguer")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Vue générale** — aperçu du dataset et des paquets train/dev/test
    ** Analyse** — graphiques : répartition, pays, âge, facteurs
    """)
with col2:
    st.markdown("""
    ** Modèles** — comparaison des performances des 6 modèles
    ** Prédiction** — estimer le risque d'un individu
    """)

st.divider()


# navigateur 
st.sidebar.header("Navigation")
st.sidebar.write("Utilise le menu pour explorer les pages.")
st.sidebar.markdown("---")
st.sidebar.info("Projet de prédiction de l'hypertension")