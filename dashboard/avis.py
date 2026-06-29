from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db")


def creer_demande(patient_id, patient_nom, message, fichier=""):
    # le patient cree une demande davis
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO demandes_avis (patient_id, patient_nom, message, fichier)
            VALUES (:pid, :nom, :msg, :fic)
        """), {"pid": patient_id, "nom": patient_nom, "msg": message, "fic": fichier})


def mes_demandes(patient_id):
    # les demandes dun patient pour voir les reponses
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT message, reponse, medecin_nom, statut, cree_le FROM demandes_avis
            WHERE patient_id = :pid ORDER BY cree_le DESC
        """), {"pid": patient_id}).fetchall()
    return [{"message": r[0], "reponse": r[1], "medecin": r[2],
             "statut": r[3], "date": r[4]} for r in rows]


def demandes_en_attente():
    # toutes les demandes pas encore repondues pour le medecin
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, patient_nom, message, fichier, cree_le FROM demandes_avis
            WHERE statut = 'en_attente' ORDER BY cree_le
        """)).fetchall()
    return [{"id": r[0], "patient_nom": r[1], "message": r[2],
             "fichier": r[3], "date": r[4]} for r in rows]


def repondre(demande_id, reponse, medecin_nom):
    # le medecin repond a une demande
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE demandes_avis SET reponse=:rep, medecin_nom=:med, statut='repondu'
            WHERE id=:id
        """), {"rep": reponse, "med": medecin_nom, "id": demande_id})