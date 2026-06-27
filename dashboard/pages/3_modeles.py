import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import plotly.graph_objects as go
from style import appliquer_style, entete

if "user" not in st.session_state:
    # pas connecte écran de login    
    st.warning(" Connecte-toi d'abord depuis la page d'accueil.")
    st.stop()  

appliquer_style()                     
entete("📊 Analyse", "Exploration des données")  
st.title("Comparaison des modèles")

FICHIER = "resultats/metrics.csv"

# on lit le fichier metrics cest la ou il ya les resultat
if not os.path.exists(FICHIER):
    st.warning("Aucun résultat trouvé. Lance d'abord tes modèles puis recharge la page.")
    st.stop()

df = pd.read_csv(FICHIER).sort_values("auc", ascending=False)
#unn tab de comparaision 
st.subheader("Tableau comparatif")
st.dataframe(df, use_container_width=True, hide_index=True)

# accuracy + AUC côte à côte
st.subheader("Scores")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(df, x="modele", y="accuracy", color_discrete_sequence=["#5AA9C9"])
    fig.add_hline(y=0.7188, line_dash="dash", annotation_text="baseline 71.9%")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      yaxis_range=[0, 1], title="Accuracy")
    st.plotly_chart(fig, use_container_width=True, key="acc")

with c2:
    fig = px.bar(df, x="modele", y="auc", color_discrete_sequence=["#6a4c93"])
    fig.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="hasard 0.50")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      yaxis_range=[0, 1], title="AUC")
    st.plotly_chart(fig, use_container_width=True, key="auc")

# la detections  des classe recall Low et high
st.subheader("Détection des classes (recall par classe)")
fig = go.Figure()
fig.add_bar(name="recall Low", x=df["modele"], y=df["recall_low"], marker_color="#5AA9C9")
fig.add_bar(name="recall High", x=df["modele"], y=df["recall_high"], marker_color="#E76F73")
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                  barmode="group", yaxis_range=[0, 1])
st.plotly_chart(fig, use_container_width=True, key="recall")

# F1-score moyen macro pour chqu model
st.subheader("F1-score moyen (moyenne des 2 classes)")
fig = px.bar(df, x="modele", y="f1", color_discrete_sequence=["#5AA9C9"])
fig.add_hline(y=0.5, line_dash="dash", line_color="red",
              annotation_text="hasard (0.50)")
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                  yaxis_range=[0, 1], xaxis_title="", yaxis_title="F1 macro")
fig.update_xaxes(tickangle=-30)
st.plotly_chart(fig, use_container_width=True, key="f1")

# Précision moyenne  pour chaque modele
st.subheader("Précision moyenne (moyenne des 2 classes)")
fig = px.bar(df, x="modele", y="precision", color_discrete_sequence=["#6a4c93"])
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                  yaxis_range=[0, 1], xaxis_title="", yaxis_title="Précision macro")
fig.update_xaxes(tickangle=-30)
st.plotly_chart(fig, use_container_width=True, key="precision")

# LES MATRICE DE CONFUSIONNNNN
st.subheader("Matrices de confusion (TP / FP / FN / TN)")

choix_modele = st.selectbox("Choisis un modèle", df["modele"].tolist())
row = df[df["modele"] == choix_modele].iloc[0]

TN, FP = int(row["low_low"]), int(row["low_high"])
FN, TP = int(row["high_low"]), int(row["high_high"])

valeurs = [[TP, FN],
           [FP, TN]]
sigles  = [["TP<br>Vrai Positif", "FN<br>Faux Négatif"],
           ["FP<br>Faux Positif", "TN<br>Vrai Négatif"]]
couleurs = [["#2e7d32", "#c62828"],
            ["#c62828", "#2e7d32"]]

fig = go.Figure()
for i in range(2):
    for j in range(2):
        fig.add_shape(type="rect", x0=j, y0=1-i, x1=j+1, y1=2-i,
                      fillcolor=couleurs[i][j], opacity=0.18, line_color=couleurs[i][j])
        fig.add_annotation(x=j+0.5, y=2-i-0.25, text=f"<b>{sigles[i][j]}</b>",
                           showarrow=False, font=dict(size=14, color=couleurs[i][j]))
        fig.add_annotation(x=j+0.5, y=2-i-0.65, text=f"<b>{valeurs[i][j]:,}</b>".replace(",", " "),
                           showarrow=False, font=dict(size=20, color="white"))

fig.update_xaxes(showticklabels=True, tickvals=[0.5, 1.5],
                 ticktext=["ŷ = 1 (High)", "ŷ = 0 (Low)"], side="top", range=[0, 2])
fig.update_yaxes(showticklabels=True, tickvals=[1.5, 0.5],
                 ticktext=["y = 1 (High)", "y = 0 (Low)"], range=[0, 2])
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)", height=420,
                  title=f"Matrice de confusion — {choix_modele}")
st.plotly_chart(fig, use_container_width=True, key="cm_prof")