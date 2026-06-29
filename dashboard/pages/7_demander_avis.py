import os
import streamlit as st
from style import appliquer_style, entete, verifier_role
from avis import creer_demande, mes_demandes

appliquer_style()
# tout connecté peut demander un avis un medecin peut demnader lavis 'un aute et un dev peut demander lavis dun medecin 
verifier_role(["patient", "dev", "medecin"])   
entete("💬 Demander un avis médical", "Envoie tes informations à un médecin")

user = st.session_state["user"]

# le formulaire 
st.subheader("Nouvelle demande")
message = st.text_area("Décris ta situation / ta question",
                       placeholder="Ex : J'ai une tension élevée depuis quelques jours...")
fichier = st.file_uploader("Joindre un fichier (optionnel)",
                           type=["pdf", "png", "jpg", "jpeg"])

if st.button("📤 Envoyer ma demande", type="primary"):
    if not message:
        st.warning("Écris au moins un message.")
    else:
        chemin = ""
        if fichier is not None:
            os.makedirs("avis_fichiers", exist_ok=True)
            chemin = f"avis_fichiers/{user['identifiant']}_{fichier.name}"
            with open(chemin, "wb") as f:
                f.write(fichier.getbuffer())
        creer_demande(user["id"], user["nom"], message, chemin)
        st.success("✅ Demande envoyée ! Un médecin te répondra bientôt.")

st.divider()

# les donne et la reponse du med
st.subheader("Mes demandes")
demandes = mes_demandes(user["id"])
if not demandes:
    st.info("Tu n'as pas encore fait de demande.")
else:
    for d in demandes:
        with st.container(border=True):
            st.markdown(f"**Ma question :** {d['message']}")
            if d["statut"] == "repondu":
                st.success(f"**Réponse du Dr {d['medecin']} :** {d['reponse']}")
            else:
                st.caption("⏳ En attente de réponse...")