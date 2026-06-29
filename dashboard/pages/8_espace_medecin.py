import os
import streamlit as st
from style import appliquer_style, entete, verifier_role
from avis import demandes_en_attente, repondre

appliquer_style()
#si cest medecin on affiche 
verifier_role(["medecin"])  
entete("👨‍⚕️ Espace médecin", "Répondre aux demandes des patients")

user = st.session_state["user"]

demandes = demandes_en_attente()
if not demandes:
    st.info("Aucune demande en attente.")
else:
    st.subheader(f"{len(demandes)} demande(s) en attente")
    for d in demandes:
        with st.container(border=True):
            st.markdown(f"### Patient : {d['patient_nom']}")
            st.markdown(f"**Question :** {d['message']}")
            # le fichier joint 
            if d["fichier"] and os.path.exists(d["fichier"]):
                with open(d["fichier"], "rb") as f:
                    st.download_button("📎 Voir le fichier joint", f,
                        file_name=os.path.basename(d["fichier"]), key=f"dl_{d['id']}")
            # zone de reponse
            reponse = st.text_area("Ta réponse", key=f"rep_{d['id']}")
            if st.button(" Envoyer la réponse", key=f"btn_{d['id']}"):
                if reponse:
                    repondre(d["id"], reponse, user["nom"])
                    st.success("Réponse envoyée au patient !")
                    st.rerun()
                else:
                    st.warning("Écris une réponse.")