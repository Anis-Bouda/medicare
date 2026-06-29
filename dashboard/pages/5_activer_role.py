import streamlit as st
from style import appliquer_style, entete
from auth import activer_role

# il faut être connecté
if "user" not in st.session_state:
    st.warning(" Connecte-toi d'abord depuis la page d'accueil.")
    st.stop()

appliquer_style()
entete(" Activer mon rôle", "Saisis le code reçu par email")

user = st.session_state["user"]

# si dejà dev ou medecine pas besoin on donne just eton role
if user["role"] in ("dev", "medecin"):
    st.success(f" Tu es déjà **{user['role']}** !")
    st.stop()

st.write("Tu as fait une demande de rôle dev ou médecin ? "
         "Saisis ici le code reçu par email après validation de l'admin.")

code = st.text_input("Code d'activation")

if st.button("Activer mon rôle", type="primary"):
    if not code:
        st.warning("Entre le code reçu par email.")
    else:
        #on verifie le code avec la fonction activer_role
        ok, msg = activer_role(user["identifiant"], code.strip())
        if ok:
            st.success(msg)
            st.balloons()
            
            nouveau_role = msg.replace("!", "").strip().split()[-1]
            st.session_state["user"]["role"] = nouveau_role
            st.info("Reconnecte-toi pour voir tes nouveaux accès.")
        else:
            st.error(msg)