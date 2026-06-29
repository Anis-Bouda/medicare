import streamlit as st
from auth import inscrire, connecter
from donnees import charger_donnees
from style import appliquer_style, carte_kpi, carte_nav ,entete
from auth import lister_demandes, valider_role, refuser_role
from email_utils import envoyer_email
import os

st.set_page_config(page_title="Medicare - Hypertension", layout="wide",
                   initial_sidebar_state="collapsed")


# css du dashbord 

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
/* carte de login */
.login-card {
    max-width: 430px; margin: 1rem auto;
    background: linear-gradient(160deg,#161A23 0%,#1b2230 100%);
    border: 1px solid rgba(90,169,201,0.25); border-radius: 20px;
    padding: 2.2rem 2.4rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.login-logo {
    width: 64px; height: 64px; margin: 0 auto 1rem;
    background: linear-gradient(135deg,#5AA9C9,#4A90A8); border-radius: 18px;
    display:flex; align-items:center; justify-content:center; font-size: 32px;
    box-shadow: 0 8px 24px rgba(90,169,201,0.35);
}
.login-title { text-align:center; font-size:26px; font-weight:700; color:#E6E6E6; }
.login-sub { text-align:center; color:#8b95a5; font-size:14px; margin-bottom:1.5rem; }
.login-foot { text-align:center; color:#6b7585; font-size:12px; margin-top:1rem; }
/* bouton large */
.stButton > button {
    width:100%; border-radius:11px; font-weight:700;
    background: linear-gradient(135deg,#5AA9C9,#4A90A8); color:#0E1117; border:none;
    padding: 0.6rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================== #
#   PAGE DE CONNEXION (si pas connecté)
# ============================================================== #

def page_login():
    
    # --- CSS : cacher le menu + fond plein écran ---
    st.markdown("""
    <style>
    /* cacher COMPLÈTEMENT la barre latérale et son bouton */
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="collapsedControl"] { display: none !important; }
    button[kind="header"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }

    /* fond animé plein écran */
    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(139,92,246,0.18), transparent 40%),
            radial-gradient(circle at 80% 60%, rgba(99,102,241,0.15), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(168,85,247,0.12), transparent 50%),
            #07070d;
        background-size: 200% 200%;
        animation: bouge 18s ease infinite;
    }
    @keyframes bouge {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    /* carte de login en glassmorphism */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20,20,32,0.6) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(139,92,246,0.3) !important;
        border-radius: 18px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(139,92,246,0.1);
    }
    /* le bouton en violet (force) */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
        color: white !important; border: none !important;
        box-shadow: 0 6px 20px rgba(139,92,246,0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # affichage graphique et logo
    gauche, milieu, droite = st.columns([1, 1.3, 1])
    with milieu:
        st.markdown('<div class="login-logo">🩺</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Medicare</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Plateforme de prédiction du risque d\'hypertension</div>',
                    unsafe_allow_html=True)
        # on retourne le formulaire
        with st.container(border=True):     
            onglet_co, onglet_in = st.tabs([" Connexion", " Inscription"])
            with onglet_co:
                identifiant = st.text_input("Identifiant", key="co_id")
                mdp = st.text_input("Mot de passe", type="password", key="co_mdp")
                if st.button("Se connecter", key="btn_co", use_container_width=True):
                    ok, res = connecter(identifiant, mdp)
                    if ok:
                        st.session_state["user"] = res
                        st.rerun()
                    else:
                        st.error(res)
            with onglet_in:
                new_id = st.text_input("Choisis un identifiant", key="in_id")
                new_nom = st.text_input("Ton nom", key="in_nom")
                new_mdp = st.text_input("Mot de passe", type="password", key="in_mdp")
                role_demande = st.selectbox("Type de compte",
                    ["patient", "dev", "medecin"], key="in_role")

                # emial et justificatif si cets un dev ou med
                new_email = ""
                fichier_just = None
                if role_demande in ("dev", "medecin"):
                    st.caption("Pour une demande dev/médecin, un email et un justificatif "
                               "sont requis. Tu recevras ton code d'activation par email.")
                    new_email = st.text_input("Ton email (pour recevoir le code)", key="in_email")
                    fichier_just = st.file_uploader("Justificatif (PDF ou image)",
                        type=["pdf", "png", "jpg", "jpeg"], key="in_file")

                if st.button("Créer mon compte", key="btn_in", use_container_width=True):
                    if not new_id or not new_mdp or not new_nom:
                        st.warning("Remplis tous les champs.")
                    elif role_demande in ("dev", "medecin") and not new_email:
                        st.warning("L'email est obligatoire pour recevoir ton code.")
                    elif role_demande in ("dev", "medecin") and fichier_just is None:
                        st.warning("Le justificatif est obligatoire.")
                    else:
                        chemin = ""
                        if fichier_just is not None:
                            os.makedirs("justificatifs", exist_ok=True)
                            chemin = f"justificatifs/{new_id}_{fichier_just.name}"
                            with open(chemin, "wb") as f:
                                f.write(fichier_just.getbuffer())
                        demande = "" if role_demande == "patient" else role_demande
                        ok, msg = inscrire(new_id, new_nom, new_mdp, new_email, demande, chemin)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
        #petit msg en bas de la cnx 
        st.markdown('<div class="login-foot">🔒 Connexion sécurisée · mots de passe chiffrés</div>',
                    unsafe_allow_html=True)


#   si on arrive a se connecter on lance le dashbord 
def page_dashboard():
    user = st.session_state["user"]    

    # bouton retour seulement pour l'admin
    if user["role"] == "admin":
        if st.button("🛡️ Retour console admin"):
            st.session_state["admin_mode"] = "admin"
            st.rerun()

    # reafficher le menu de gauche
    st.markdown("""<style>
    section[data-testid="stSidebar"] { display: block !important; }
    </style>""", unsafe_allow_html=True)

    appliquer_style()
    

    # entete du haut 
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("## 🧠 Medicare")
        st.caption(f"Bienvenue **{user['nom']}**")
    with c2:
        st.write("")
        if st.button("Se déconnecter", use_container_width=True):
            del st.session_state["user"]
            st.rerun()

    # les roles avec une couleur et un emoji pour chaque rols
    roles_aff = {"admin": ("🛡️ ADMIN", "#f43f5e"),
                 "dev": ("🛠️ DÉVELOPPEUR", "#8b5cf6"),
                 "medecin": ("👨‍⚕️ MÉDECIN", "#22c55e"),
                 "patient": ("👤 PATIENT", "#22d3ee")}
    role_txt, couleur_role = roles_aff.get(user["role"], ("👤 PATIENT", "#22d3ee"))
    st.markdown(f"""
    <div style="display:inline-block; background:rgba(139,92,246,0.15);
                border:1px solid {couleur_role}; color:{couleur_role};
                padding:5px 16px; border-radius:20px; font-size:13px;
                font-weight:700; margin-bottom:20px;">{role_txt}</div>
    """, unsafe_allow_html=True)

    # affichage des donne importantes
    df = charger_donnees()
    n_patients = f"{len(df):,}".replace(",", " ")
    n_var = df.shape[1] - 1
    n_pays = df["country"].nunique()
    taux = f"{(df['hypertension']=='High').mean()*100:.1f}%"
    
    #collone avec le emoji representatif (jai pas trouver mieux)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(carte_kpi("👥", n_patients, "Patients analysés", "dans la base"), unsafe_allow_html=True)
    c2.markdown(carte_kpi("🧬", str(n_var), "Variables", "caractéristiques"), unsafe_allow_html=True)
    c3.markdown(carte_kpi("🌍", str(n_pays), "Pays", "représentés"), unsafe_allow_html=True)
    c4.markdown(carte_kpi("⚠️", taux, "Risque élevé", "des patients"), unsafe_allow_html=True)

    st.markdown("###  ")
    st.markdown("####  Navigation")

    # navifateur pour cahque fonctionalite 
    n1, n2 = st.columns(2)
    n1.markdown(carte_nav("📊","Analyse", "Graphiques : répartition, pays, âge, facteurs de risque"), unsafe_allow_html=True)
    n2.markdown(carte_nav(" 🤖","Modèles", "Comparaison des performances des 9 modèles"), unsafe_allow_html=True)
    st.write("")
    n3, n4 = st.columns(2)
    n3.markdown(carte_nav("🔮","Prédiction", "Estimer le risque d'un patient individuel"), unsafe_allow_html=True)
    n4.markdown(carte_nav( "📋","Vue générale", "Aperçu du dataset et des paquets train/dev/test"), unsafe_allow_html=True)

    # petit affichage si luser est un dev ou medecin 
    if user["role"] == "dev":
        st.markdown("###  ")
        st.info("🛠️ **Espace développeur** — accès à la gestion des modèles (menu de gauche).")
    elif user["role"] == "medecin":
        st.markdown("###  ")
        st.info("👨‍⚕️ **Espace médecin** — répondre aux demandes des patients (menu de gauche).")
        
def page_admin():
   
    # on cache le menu de gauche : l'admin a son interface dédiée
    st.markdown("""<style>section[data-testid="stSidebar"]{display:none!important;}</style>""",
                unsafe_allow_html=True)
    appliquer_style()

    user = st.session_state["user"]
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        entete("🛡️ Console Admin", f"Connecté : {user['nom']}")
    with c2:
        st.write("")
        if st.button("Déconnexion"):
            del st.session_state["user"]
            st.rerun()
    with c3:
        st.write("")
        if st.button("voir dashbord ", use_container_width=True):
            st.session_state["admin_mode"] = "dashboard"  
            st.rerun()

    demandes = lister_demandes()
    if not demandes:
        st.info("Aucune demande en attente pour le moment.")
    else:
        st.subheader(f"{len(demandes)} demande(s) en attente")
        for d in demandes:
            with st.container(border=True):
                st.markdown(f"### {d['nom']} (`{d['identifiant']}`) — veut être **{d['role_demande']}**")
                st.caption(f"📧 {d['email']}")
                # le justificatif (téléchargeable)
                if d["fichier"] and os.path.exists(d["fichier"]):
                    with open(d["fichier"], "rb") as f:
                        st.download_button("📎 Voir le justificatif", f,
                            file_name=os.path.basename(d["fichier"]), key=f"dl_{d['id']}")
                else:
                    st.caption("⚠️ Pas de justificatif fourni")
                # boutons valider / refuser
                col1, col2 = st.columns(2)
                if col1.button(" Valider", key=f"v_{d['id']}", use_container_width=True):
                    code, email, nom, role = valider_role(d["id"])
                    ok, msg = envoyer_email(email, f"Medicare - Validation {role}",
                        f"Bonjour {nom},\n\nTa demande de role {role} a été acceptée !\n"
                        f"Ton code d'activation : {code}\n\n"
                        f"Connecte-toi et saisis ce code dans 'Activer mon role'.\n\nL'équipe Medicare")
                    if ok:
                        st.success(f" {nom} validé ({role}) ! Code envoyé par email.")
                    else:
                        st.warning(f"Validé mais email non envoyé : {msg}. Code : {code}")
                    st.rerun()
                if col2.button(" Refuser", key=f"r_{d['id']}", use_container_width=True):
                    refuser_role(d["id"])
                    st.info(f"Demande de {d['nom']} refusée.")
                    st.rerun()

# redirection vers les pages selon les roles 

if "user" not in st.session_state:
    page_login()
elif st.session_state["user"]["role"] == "admin" and st.session_state.get("admin_mode") != "dashboard":
    page_admin()           # console admin par défaut
else:
    #quand un des user appuiss sur dashbord 
    page_dashboard()       