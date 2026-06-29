import os, glob, joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import streamlit as st
import xgboost
from donnees import charger_donnees
from style import appliquer_style, entete, verifier_role

appliquer_style()
verifier_role(["patient", "dev", "medecin"])
entete(" Prédiction du risque d'hypertension")
st.caption("Saisis les infos d'un patient — les modèles donnent leur avis.")

class MLP(nn.Module):
    def __init__(self, d, m):
        super().__init__()
        self.lin1 = nn.Linear(d, m)
        self.lin2 = nn.Linear(m, 1)
    def forward(self, x):
        return self.lin2(torch.relu(self.lin1(x))).squeeze(-1)

if not os.path.exists("artefacts/preprocessor.pkl"):
    st.warning("Lance d'abord entrainement_mlp.py.")
    st.stop()

preprocessor = joblib.load("artefacts/preprocessor.pkl")
df = charger_donnees()

NUM = ["age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp",
       "alcohol_intake", "stress_level", "salt_intake", "sleep_duration",
       "heart_rate", "ldl", "hdl", "triglycerides", "glucose"]
CAT = ["country", "smoking_status", "physical_activity_level", "family_history",
       "diabetes", "gender", "education_level", "employment_status"]

st.subheader("Informations du patient")
#mednu deroulant 
with st.expander("📋 Données médicales", expanded=True):
    c1, c2, c3 = st.columns(3)
    saisie = {}
    med = ["age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp",
           "heart_rate", "ldl", "hdl", "triglycerides", "glucose"]
    for i, col in enumerate(med):
        with [c1, c2, c3][i % 3]:
            saisie[col] = st.number_input(col, value=float(df[col].median()))

with st.expander("🏃 Mode de vie", expanded=False):
    c1, c2 = st.columns(2)
    vie = ["alcohol_intake", "stress_level", "salt_intake", "sleep_duration"]
    for i, col in enumerate(vie):
        with [c1, c2][i % 2]:
            saisie[col] = st.number_input(col, value=float(df[col].median()), key=col)

with st.expander("👤 Profil", expanded=False):
    c1, c2 = st.columns(2)
    for i, col in enumerate(CAT):
        with [c1, c2][i % 2]:
            saisie[col] = st.selectbox(col, sorted(df[col].dropna().unique().tolist()))

def charger_mlp(poids, config):
    cfg = joblib.load(config)
    m = MLP(cfg["d"], cfg["m"])
    m.load_state_dict(torch.load(poids))
    m.eval()
    return m

#on fait la prediction 
if st.button("Prédire", type="primary"):
    X = np.asarray(preprocessor.transform(pd.DataFrame([saisie])), dtype="float32")
    resultats = []

    # MLP normal
    if os.path.exists("artefacts/mlp.pth"):
        m = charger_mlp("artefacts/mlp.pth", "artefacts/mlp_config.pkl")
        with torch.no_grad():
            p = float(torch.sigmoid(m(torch.tensor(X))).numpy()[0])
        resultats.append(("MLP", p))

    # MLP pos_weight
    if os.path.exists("artefacts/mlp_pw.pth"):
        m = charger_mlp("artefacts/mlp_pw.pth", "artefacts/mlp_pw_config.pkl")
        with torch.no_grad():
            p = float(torch.sigmoid(m(torch.tensor(X))).numpy()[0])
        resultats.append(("MLP (pos_weight)", p))

    # modèles sklearn standards et xgboost standard
    for chemin in sorted(glob.glob("artefacts/modeles/*.pkl")):
        nom = os.path.splitext(os.path.basename(chemin))[0]
        try:
            modele = joblib.load(chemin)
            p = float(modele.predict_proba(X)[0, 1])
            resultats.append((nom, p))
        except Exception:
            #il reste 4 modele a ajouter ceux fait a la main r
            pass   

    st.subheader("Résultats de la prédiction")


    # on trie par proba decroissante
    res = sorted(resultats, key=lambda r: r[1], reverse=True)

    # une colonne par modèle
    colonnes = st.columns(len(res))
    for col, (nom, proba) in zip(colonnes, res):
        high = proba >= 0.5
        couleur = "#E76F73" if high else "#5AA9C9"
        classe = "High" if high else "Low"
        with col:
            # on met le nom dumodel en 1er ligne 
            st.markdown(f"""
            <div style="background:#1b3a4b; color:white; text-align:center;
                        padding:10px 4px; border-radius:8px 8px 0 0;
                        font-weight:700; font-size:13px; min-height:48px;
                        display:flex; align-items:center; justify-content:center;">
                {nom}
            </div>""", unsafe_allow_html=True)
            #  le % et sa classe dans une case colore selon si la classe rouge ou bleu  sur la 2emme ligne 
            st.markdown(f"""
            <div style="background:{couleur}; color:white; text-align:center;
                        padding:14px 4px; border-radius:0 0 8px 8px;">
                <div style="font-size:20px; font-weight:700;">{proba*100:.1f}%</div>
                <div style="font-size:13px;">({classe})</div>
            </div>""", unsafe_allow_html=True)