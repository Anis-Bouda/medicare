import bcrypt
from sqlalchemy import create_engine, text

URL = "postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db"
engine = create_engine(URL)


def inscrire(identifiant, nom, mot_de_passe, role="patient"):
    #Cree un nouveau compte. Renvoie true avec mssag eou false  et msg
    # chiffremen du mdps
    hash_mdp = bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO utilisateurs (identifiant, nom, mot_de_passe, role)
                VALUES (:id, :nom, :mdp, :role)
            """), {"id": identifiant, "nom": nom, "mdp": hash_mdp, "role": role})
        return True, "Compte créé avec succès !"
    except Exception:
        return False, "Cet identifiant existe déjà."


def connecter(identifiant, mot_de_passe):
    #verification que les ididentifiant revoie soit true ou false
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, nom, mot_de_passe, role FROM utilisateurs
            WHERE identifiant = :id
        """), {"id": identifiant}).fetchone()

    if result is None:
        return False, "Identifiant inconnu."

    user_id, nom, hash_mdp, role = result
    # on compare mdps saisi avec le mpsds hashe
    if bcrypt.checkpw(mot_de_passe.encode(), hash_mdp.encode()):
        return True, {"id": user_id, "nom": nom, "role": role, "identifiant": identifiant}
    else:
        return False, "Mot de passe incorrect."