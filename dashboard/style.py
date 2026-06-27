
import streamlit as st
# les couleur que jutilise  dans le dashbord
VIOLET = "#8b5cf6"
INDIGO = "#6366f1"
VIOLET_CLAIR = "#a78bfa"
FOND = "#0a0a12"
CARTE = "#13131f"
TEXTE = "#e6e6f0"
GRIS = "#7c7f9e"
HIGH = "#f43f5e"   
LOW = "#22d3ee"   

#fonction pour changer le style utiliser tousau long des pages  
def appliquer_style():
    #fonction pour metrre le css dans chaque page 
    st.markdown(f"""
    <style>
    /* pour les cercle violet  */
    .stApp {{
        background:
            radial-gradient(circle at 15% 0%, rgba(139,92,246,0.10), transparent 35%),
            radial-gradient(circle at 90% 20%, rgba(99,102,241,0.08), transparent 30%),
            {FOND};
    }}
    .block-container {{ padding-top: 2.5rem; max-width: 1200px; }}

    /* pour les titre */
    h1, h2, h3 {{ color: {TEXTE}; letter-spacing: -0.5px; }}

    
    div[data-testid="stMetric"] {{
        background: linear-gradient(160deg, {CARTE}, #1a1a2e);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    div[data-testid="stMetric"]::before {{
        content:''; display:block; height:3px; margin:-18px -20px 14px -20px;
        border-radius:16px 16px 0 0;
        background: linear-gradient(90deg, {VIOLET}, {INDIGO});
    }}
    div[data-testid="stMetricValue"] {{ color: {TEXTE}; font-weight: 800; }}
    div[data-testid="stMetricLabel"] {{ color: {GRIS}; }}

    /* pour les bouton */
    .stButton > button {{
        background: linear-gradient(135deg, {VIOLET}, {INDIGO});
        color: white; border: none; border-radius: 11px; font-weight: 700;
        padding: 0.55rem 1rem; box-shadow: 0 6px 20px rgba(139,92,246,0.35);
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        box-shadow: 0 8px 28px rgba(139,92,246,0.55); transform: translateY(-1px);
    }}

    /* pour les  onglet */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {CARTE}; border-radius: 10px; padding: 8px 18px;
        color: {GRIS};
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {VIOLET}, {INDIGO}) !important;
        color: white !important;
    }}

    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background: {FOND} !important; border: 1px solid rgba(139,92,246,0.25) !important;
        border-radius: 10px !important; color: {TEXTE} !important;
    }}

    /* pour le menu a droite  */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d0d18, #0a0a12);
        border-right: 1px solid rgba(139,92,246,0.15);
    }}
    </style>
    """, unsafe_allow_html=True)

#changemn du style de entwte
def entete(titre, sous_titre=""):
    #pour afficher lentet avec le logo
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">
        <div style="width:50px; height:50px; border-radius:14px;
                    background:linear-gradient(135deg,{VIOLET},{INDIGO});
                    display:flex; align-items:center; justify-content:center;
                    font-size:26px; box-shadow:0 8px 28px rgba(139,92,246,0.5);">🧠</div>
        <div>
            <div style="font-size:26px; font-weight:800; color:{TEXTE};
                        letter-spacing:-0.5px;">{titre}</div>
            <div style="font-size:14px; color:{GRIS};">{sous_titre}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:1px; background:linear-gradient(90deg,"
                f"rgba(139,92,246,0.4),transparent); margin:14px 0 24px;'></div>",
                unsafe_allow_html=True)

#changement du style des indica
def carte_kpi(icone, valeur, label, sous_label=""):
    # les ptite carte avec les chiffre importantpour les pays les patient et tous 
    return f"""
    <div style="background:linear-gradient(160deg,{CARTE},#1a1a2e);
                border:1px solid rgba(139,92,246,0.18); border-radius:16px;
                padding:20px; position:relative; overflow:hidden; height:100%;">
        <div style="position:absolute; top:0; left:0; width:100%; height:3px;
                    background:linear-gradient(90deg,{VIOLET},{INDIGO});"></div>
        <div style="font-size:22px; margin-bottom:8px;">{icone}</div>
        <div style="font-size:30px; font-weight:800; color:{TEXTE};
                    letter-spacing:-1px; line-height:1;">{valeur}</div>
        <div style="font-size:13px; color:{GRIS}; margin-top:6px;">{label}</div>
        <div style="font-size:11px; color:{GRIS}; opacity:0.7;">{sous_label}</div>
    </div>
    """

#changement du style du navigateur 
def carte_nav(icone, titre, description):
    # les carte qui expliquent chaque page du menu
    return f"""
    <div style="background:linear-gradient(160deg,{CARTE},#1a1a2e);
                border:1px solid rgba(139,92,246,0.18); border-radius:14px;
                padding:18px 20px; height:100%; transition:all 0.2s;">
        <div style="font-size:16px; font-weight:700; color:{TEXTE};
                    margin-bottom:6px;">{icone} {titre}</div>
        <div style="font-size:13px; color:{GRIS}; line-height:1.5;">{description}</div>
    </div>
    """