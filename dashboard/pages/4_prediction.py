import os, glob, joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import streamlit as st
import xgboost
from donnees import charger_donnees
from style import appliquer_style, entete, verifier_role
import sys
import modeles_maison

# on met les classes maison a la page pour quelle puisse les charger pour les modeles fait a la main 
sys.modules["__main__"].ArbreDecisionMaison = modeles_maison.ArbreDecisionMaison
sys.modules["__main__"].LogisticRegressionFromScratch = modeles_maison.LogisticRegressionFromScratch
sys.modules["__main__"].Node = modeles_maison.Node
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


# fonction qui donne la proba pour nimporte quel modele meme les maison
def proba_modele(modele, X):
    # si cest une liste darbre xgboost maison on lemballe dans un wrapper
    if isinstance(modele, list):
        modele = modeles_maison.XGBoostMaisonWrapper(modele, lr=0.1)
    return float(modele.predict_proba(X)[0, 1])

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
    # tous les modeles  sklearn xgboost ET les maison sauf le random forest car il utilise un pipe line donc on lui mmet un cas a part 
    for chemin in sorted(glob.glob("artefacts/modeles/*.pkl")):
        nom = os.path.splitext(os.path.basename(chemin))[0]
        # le random forest est un pipeline qui veut du brut on le fait a part juste apres
        if "Random Forest" in nom:
            continue
        try:
            modele = joblib.load(chemin)
            # marche pour tous meme les maison
            p = proba_modele(modele, X)
            resultats.append((nom, p))
        except Exception as e:
            st.caption(f" {nom} non chargé ({type(e).__name__})")

    # le random forest est un pipeline il veut les donne brutes avec les colonne en majuscule
    noms_maj = {
        "age": "Age", "bmi": "BMI", "cholesterol": "Cholesterol",
        "systolic_bp": "Systolic_BP", "diastolic_bp": "Diastolic_BP",
        "alcohol_intake": "Alcohol_Intake", "stress_level": "Stress_Level",
        "salt_intake": "Salt_Intake", "sleep_duration": "Sleep_Duration",
        "heart_rate": "Heart_Rate", "ldl": "LDL", "hdl": "HDL",
        "triglycerides": "Triglycerides", "glucose": "Glucose",
        "country": "Country", "smoking_status": "Smoking_Status",
        "physical_activity_level": "Physical_Activity_Level",
        "family_history": "Family_History", "diabetes": "Diabetes",
        "gender": "Gender", "education_level": "Education_Level",
        "employment_status": "Employment_Status",
    }
    df_brut = pd.DataFrame([{noms_maj[k]: v for k, v in saisie.items()}])

    chemin_rf = "artefacts/modeles/Random Forest.pkl"
    if os.path.exists(chemin_rf):
        try:
            rf = joblib.load(chemin_rf)
            # on prend la proba de la classe High
            i_high = list(rf.classes_).index("High")
            p_rf = float(rf.predict_proba(df_brut)[0, i_high])
            resultats.append(("Random Forest", p_rf))
        except Exception as e:
            st.caption(f" Random Forest non chargé ({type(e).__name__})")

    # le random forest ameliore  pareil mais il a son preprocessor a lui et  des variable en plus
    chemins_rfa = [
        "artefacts/modeles/random_forest_version_amelioree_model.joblib",
        "outputs/random_forest_version_amelioree/random_forest_version_amelioree_model.joblib",
    ]
    chemin_rfa = next((c for c in chemins_rfa if os.path.exists(c)), None)
    if chemin_rfa:
        try:
            from random_forest_version_amelioree import MedicalFeatureEngineer
            bundle = joblib.load(chemin_rfa)   # cest un dico avec preprocessor + classifier
            # il rajoute ses variable derive puis encode avec son propre preprocessor
            df_feat = MedicalFeatureEngineer().transform(df_brut)
            X_rfa = bundle["preprocessor"].transform(df_feat)
            i_high = list(bundle["classifier"].classes_).index("High")
            p_rfa = float(bundle["classifier"].predict_proba(X_rfa)[0, i_high])
            resultats.append(("Random Forest amélioré", p_rfa))
        except Exception as e:
            st.caption(f" Random Forest amélioré non chargé ({type(e).__name__})")

    st.subheader("Résultats de la prédiction")

    # on trie par proba decroissante
    res = sorted(resultats, key=lambda r: r[1], reverse=True)

    # on affiche par range de 4 quand jai affiche tous les modeles cetait trop clle 
    for i in range(0, len(res), 4):
        rangee = res[i:i+4]
        colonnes = st.columns(4)
        for col, (nom, proba) in zip(colonnes, rangee):
            high = proba >= 0.5
            couleur = "#E76F73" if high else "#5AA9C9"
            classe = "High" if high else "Low"
            with col:
                # le nom du modele
                st.markdown(f"""
                <div style="background:#1b3a4b; color:white; text-align:center;
                            padding:10px 4px; border-radius:8px 8px 0 0;
                            font-weight:700; font-size:13px; min-height:48px;
                            display:flex; align-items:center; justify-content:center;
                            margin:6px 4px 0 4px;">
                    {nom}
                </div>""", unsafe_allow_html=True)
                # le % et la classe
                st.markdown(f"""
                <div style="background:{couleur}; color:white; text-align:center;
                            padding:14px 4px; border-radius:0 0 8px 8px;
                            margin:0 4px 12px 4px;">
                    <div style="font-size:20px; font-weight:700;">{proba*100:.1f}%</div>
                    <div style="font-size:13px;">({classe})</div>
                </div>""", unsafe_allow_html=True)