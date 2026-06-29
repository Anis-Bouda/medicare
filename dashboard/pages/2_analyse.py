import streamlit as st
from donnees import charger_donnees
import plotly.express as px
import pandas as pd
from style import appliquer_style, entete, verifier_role

appliquer_style()
#tous le monde peut y acceder 
verifier_role(["patient", "dev", "medecin"])   
entete("📊 Analyse", "Exploration des données")
df = charger_donnees()
#crer des onglets clicable en haut de page 
tab1, tab2, tab3, tab4 = st.tabs(["Repartition", "Pays", "Âge", "Facteurs"])
#on va recuperer chaqeu onglets pour aficher ce que il ya dedant 
with tab1:
    st.subheader("Repartition du risque (High / Low)")

    fig = px.pie(
        df,
        names="hypertension",
        hole=0.6,
        color="hypertension",
        color_discrete_map={"High": "#E76F73", "Low": "#032A6E"},
    )
    #quand on survole avec la sourie on a une bulle qui s'affiche 
    fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>",
)
    #envoie le graph a stimlit 
    st.plotly_chart(fig, use_container_width=True, key="general_view")
with tab2:
    st.subheader("Analyse par pays")

    #un menu pour choisir le pays 
    pays = st.selectbox(
        "Choisis un pays",
        #une case tous les pays et les pays individuel ordone 
        ["Tous les pays"] + sorted(df["country"].unique()),
    )

    #on filtre les données selon le choix
    data = df if pays == "Tous les pays" else df[df["country"] == pays]

    #chiffres clés du pays choisi
    c1, c2, c3 = st.columns(3)
    c1.metric("Patients", f"{len(data):,}".replace(",", " "))
    c2.metric("Risque elev", f"{(data['hypertension'] == 'High').mean() * 100:.1f}%")
    c3.metric("Risque faible", f"{(data['hypertension'] == 'Low').mean() * 100:.1f}%")

    #un donut avec ula proportion de high et low
    fig2 = px.pie(
        data, names="hypertension", hole=0.6,
        color="hypertension",
        color_discrete_map={"High": "#E76F73", "Low": "#5AA9C9"},
    )
    fig2.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>",
    )
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True, key="pays_indi")   

    # pour tous les pays on clacule le pourcentage un taux high 
    taux = (
        df.groupby("country")["hypertension"]
          .apply(lambda s: (s == "High").mean() * 100)
          .reset_index(name="taux")
          .sort_values("taux")
    )
    #on affiche pour chaque pays une barre
    fig2 = px.bar(
        taux,
        x="taux",
        y="country",
        orientation="h",
        color_discrete_sequence=["#E76F73"],
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="% de risque eleve",
        yaxis_title="pays",
        height=550,
    )


    st.plotly_chart(fig2, use_container_width=True, key="pays_globale")


    # carte du monde 
    st.markdown(" Vue generale")

    taux_pays = (
        df.groupby("country")["hypertension"]
          .apply(lambda s: (s == "High").mean() * 100)
          .reset_index(name="taux")
    )

    carte = px.choropleth(
        taux_pays,
        locations="country",
        locationmode="country names",
        color="taux",
        color_continuous_scale="Reds",
        hover_name="country",
    )
    carte.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=450,
    )
    st.plotly_chart(carte, use_container_width=True, key="carte_pays")

with tab3:
    st.subheader("Risque eleve par tranche d'age")

    #on decoupe l'age en tranches
    tranches = pd.cut(
        df["age"],
        #les borne des tranches d'age
        bins=[18, 30, 40, 50, 60, 70, 90],
        #les labels des cases
        labels=["18-29", "30-39", "40-49", "50-59", "60-69", "70+"],
        right=False,
    )

    # pour chaque trancheon calcule pourcentage de high"
    taux_age = (
        df.assign(tranche=tranches)
          .groupby("tranche", observed=True)["hypertension"]
          .apply(lambda s: (s == "High").mean() * 100)
          .reset_index(name="taux")
    )

    #on crer le graphique  
    fig_age = px.bar(
        taux_age, x="tranche", y="taux",
        color_discrete_sequence=["#22015B"], text="taux",
    )
    fig_age.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_age.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Tranche d'age", yaxis_title="% de risque elevé",
        yaxis_range=[65, 78], height=450,
    )
    st.plotly_chart(fig_age, use_container_width=True, key="barres_age")


    st.divider()
    st.subheader("Explorer une tranche d'age")

    #menu avce les tranches d'age
    choix_age = st.selectbox(
        "Choisis une tranche d'age",
        ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"],
    )

    #on garde seulement les patients de cette tranche
    data_age = df.assign(tranche=tranches)
    data_age = data_age[data_age["tranche"] == choix_age]

    #chiffres cles de la tranche
    c1, c2 = st.columns(2)
    c1.metric("Patients", f"{len(data_age):,}".replace(",", " "))
    c2.metric("Risque eleve", f"{(data_age['hypertension'] == 'High').mean() * 100:.1f}%")

    #donut High et Low pour cette tranche dage
    donut_age = px.pie(
        data_age, names="hypertension", hole=0.6,
        color="hypertension",
        color_discrete_map={"High": "#E76F73", "Low": "#001BA2"},
    )
    donut_age.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>",
    )
    donut_age.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(donut_age, use_container_width=True, key="donut_age")

with tab4:
    st.subheader("Facteurs médicaux et mode de vie")

    # menu : on choisit la variable à comparer
    variables = {
        "IMC": "bmi",
        "Cholestérol": "cholesterol",
        "Pression systolique": "systolic_bp",
        "Pression diastolique": "diastolic_bp",
        "Glucose": "glucose",
        "Fréquence cardiaque": "heart_rate",
        "Consommation d'alcool": "alcohol_intake",
        "Niveau de stress": "stress_level",
        "Durée de sommeil": "sleep_duration",
        "Consommation de sel": "salt_intake",
    }
    choix = st.selectbox("Choisis un facteur", list(variables.keys()))
    colonne = variables[choix]

    # forme de graphique au choix
    forme = st.radio("Forme du graphique",
                     ["Boîtes (boxplot)", "Densité", "Histogramme"],
                     horizontal=True)

    if forme == "Boîtes (boxplot)":
        fig = px.box(df, x="hypertension", y=colonne, color="hypertension",
                     color_discrete_map={"High": "#E76F73", "Low": "#5AA9C9"})
    elif forme == "Histogramme":
        fig = px.histogram(df, x=colonne, color="hypertension", barmode="overlay",
                           nbins=40, color_discrete_map={"High": "#E76F73", "Low": "#5AA9C9"})
    else:  # Densité
        fig = px.violin(df, x="hypertension", y=colonne, color="hypertension",
                        box=True, color_discrete_map={"High": "#E76F73", "Low": "#5AA9C9"})

    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="", showlegend=False, height=450)
    st.plotly_chart(fig, use_container_width=True, key="facteurs")

    st.caption("Astuce : compare les groupes High et Low — ils se superposent "
               "presque parfaitement, signe que ce facteur ne distingue pas les classes.")