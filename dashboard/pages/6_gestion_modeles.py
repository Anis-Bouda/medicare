import os
import glob
import joblib
import streamlit as st
from style import appliquer_style, entete, verifier_role

# page reservr que au dev securiser avec la fonction verifier roles
appliquer_style()
verifier_role(["dev"])     
entete("🛠️ Gestion des modèles", "Espace développeur")

DOSSIER = "artefacts/modeles"
os.makedirs(DOSSIER, exist_ok=True)

# tous les modeles acctuels
st.subheader("Modèles actuellement disponibles")
fichiers = sorted(glob.glob(f"{DOSSIER}/*.pkl"))

if not fichiers:
    st.info("Aucun modèle dans le dossier pour l'instant.")
else:
    for chemin in fichiers:
        nom = os.path.basename(chemin)
        taille = os.path.getsize(chemin) / 1024 
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"**{nom}**")
        c2.caption(f"{taille:.0f} Ko")
        if c3.button("🗑️ Supprimer", key=f"del_{nom}"):
            os.remove(chemin)
            st.success(f"{nom} supprimé.")
            st.rerun()

st.divider()


#  pour ajouterjouter un nouveau modele deja entrainer 
st.subheader("Ajouter un nouveau modèle")

st.warning(
    "⚠️ Le modèle doit être un fichier `.pkl` (joblib) entraîné avec **le même "
    "préprocesseur** que les autres (52 colonnes, Low=0/High=1) et exposer "
    "`predict_proba`. Un modèle incompatible ne pourra pas faire de prédiction."
)

fichier = st.file_uploader("Choisis un fichier .pkl", type=["pkl"])

if fichier is not None:
    nom_modele = st.text_input("Nom du modèle (affiché dans la comparaison)",
                               value=fichier.name.replace(".pkl", ""))
    if st.button(" Ajouter ce modèle", type="primary"):
        chemin_dest = os.path.join(DOSSIER, f"{nom_modele}.pkl")
        # on enregistre le fichier
        with open(chemin_dest, "wb") as f:
            f.write(fichier.getbuffer())
        # on vérifie qu'il se charge et a predict_proba
        try:
            modele = joblib.load(chemin_dest)
            if hasattr(modele, "predict_proba"):
                st.success(f" '{nom_modele}' ajouté et compatible ! "
                           "Il apparaîtra dans la page Prédiction.")
            else:
                st.warning(f" '{nom_modele}' ajouté, mais il n'a pas `predict_proba` "
                           "— il pourrait ne pas marcher en prédiction.")
        except Exception as e:
            os.remove(chemin_dest)
            st.error(f" Modèle incompatible, non ajouté : {type(e).__name__}")