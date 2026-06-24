import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

@st.cache_data
def charger_donnees():
    # on se connecte à PostgreSQL
    engine = create_engine(
        "postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db"
    )
    # on lit toute la table
    df = pd.read_sql("SELECT * FROM patients_hypertension", engine)
    return df