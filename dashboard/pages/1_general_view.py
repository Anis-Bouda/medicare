import streamlit as st
from sklearn.model_selection import train_test_split
from donnees import charger_donnees
from style import appliquer_style, entete, verifier_role

appliquer_style()
verifier_role(["patient", "dev", "medecin"])
entete("📋 Vue générale", "Aperçu du dataset et des paquets train / dev / test")

@st.cache_data
def charger_et_decouper():
    df = charger_donnees()
    df_train, df_temp = train_test_split(
        df, test_size=0.30, random_state=42, stratify=df["hypertension"])
    df_dev, df_test = train_test_split(
        df_temp, test_size=0.50, random_state=42, stratify=df_temp["hypertension"])
    return df, df_train, df_dev, df_test

df, df_train, df_dev, df_test = charger_et_decouper()

# un tab qui rapelle la repartition entre d train , dev , test. 
st.subheader("Composition des paquets")
recap = []
for nom, sous in [("Toutes les données", df), ("Train (70%)", df_train),
                  ("Dev (15%)", df_dev), ("Test (15%)", df_test)]:
    recap.append({
        "Paquet": nom,
        "Patients": len(sous),
        "% du total": f"{len(sous)/len(df)*100:.0f}%",
        "% High": f"{(sous['hypertension']=='High').mean()*100:.1f}%",
    })
st.dataframe(recap, use_container_width=True, hide_index=True)
st.caption("Le % High reste ~72% dans chaque paquet : la stratification a bien "
           "conservé les proportions.")

st.divider()

# case a choix pour voir quel data voir 
choix = st.radio("Quel paquet veux-tu voir ?",
                 ["Toutes les données", "Train", "Dev", "Test"], horizontal=True)

paquets = {"Toutes les données": df, "Train": df_train, "Dev": df_dev, "Test": df_test}
data = paquets[choix]

# les data 
c1, c2, c3, c4 = st.columns(4)
c1.metric("Patients", f"{len(data):,}".replace(",", " "))
c2.metric("Variables", data.shape[1])
c3.metric("Risque élevé", f"{(data['hypertension']=='High').mean()*100:.1f}%")
c4.metric("Pays", data["country"].nunique())

# affichage du tab
st.subheader(f"Aperçu — {choix}")
st.dataframe(data, use_container_width=True, hide_index=True)