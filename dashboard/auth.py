import bcrypt
import secrets
import string
from sqlalchemy import create_engine, text

# connexion a la base
URL = "postgresql+psycopg2://boudaanis@localhost:5432/hypertension_db"
engine = create_engine(URL)


def inscrire(identifiant, nom, mot_de_passe, email="", role_demande="", justificatif_fichier=""):
    # cree un nouveau compte avec els roles role_demande =patient dev ou medecin
    # si role_demande est rempli le statut devient <role>_demande (en attente)
    # justificatif_fichier = le chemin du fichier uploade
    # chiffremen du mdps
    hash_mdp = bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()
    statut = f"{role_demande}_demande" if role_demande else "patient"
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO utilisateurs (identifiant, nom, mot_de_passe, role, email, statut, justificatif_fichier)
                VALUES (:id, :nom, :mdp, 'patient', :email, :statut, :just)
            """), {"id": identifiant, "nom": nom, "mdp": hash_mdp,
                   "email": email, "statut": statut, "just": justificatif_fichier})
        if role_demande:
            return True, f"Compte créé ! Ta demande de role {role_demande} est en attente."
        return True, "Compte créé avec succès !"
    except Exception:
        return False, "Cet identifiant existe déjà."


def connecter(identifiant, mot_de_passe):
    # verification que les identifiant revoie soit true ou false
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT id, nom, mot_de_passe, role, statut FROM utilisateurs
            WHERE identifiant = :id
        """), {"id": identifiant}).fetchone()
    if r is None:
        return False, "Identifiant inconnu."
    uid, nom, hash_mdp, role, statut = r
    # on compare le mdps saisi avec le mdps hashe
    if bcrypt.checkpw(mot_de_passe.encode(), hash_mdp.encode()):
        return True, {"id": uid, "nom": nom, "role": role,
                      "statut": statut, "identifiant": identifiant}
    return False, "Mot de passe incorrect."


def lister_demandes():
    # toutes les demandes en attente dev ou medecin pour que ladmin les voye
    # on prend le justificatif et le role demande
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, identifiant, nom, email, justificatif_fichier, statut FROM utilisateurs
            WHERE statut LIKE '%_demande' ORDER BY cree_le
        """)).fetchall()
    return [{"id": r[0], "identifiant": r[1], "nom": r[2], "email": r[3],
             "fichier": r[4], "role_demande": r[5].replace("_demande", "")} for r in rows]


def valider_role(user_id):
    # ladmin valide  on genere un code de 8 caractere
    # le statuttt passe a >>>>_valide et on renvoie le code lemail le nom et le role
    code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    with engine.begin() as conn:
        r = conn.execute(text("SELECT statut, email, nom FROM utilisateurs WHERE id=:id"),
                         {"id": user_id}).fetchone()
        # dev ou medecin
        role = r[0].replace("_demande", "")   
        conn.execute(text("""
            UPDATE utilisateurs SET statut=:s, code_dev=:c WHERE id=:id
        """), {"s": f"{role}_valide", "c": code, "id": user_id})
    return code, r[1], r[2], role


def refuser_role(user_id):
    # ladmin refuse  luser redevient patient
    with engine.begin() as conn:
        conn.execute(text("UPDATE utilisateurs SET statut='patient' WHERE id=:id"),
                     {"id": user_id})


def activer_role(identifiant, code):
    # luser saisit le code recu par mai si cest bon il prend son nouveau role
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT code_dev, statut FROM utilisateurs WHERE identifiant=:id AND statut LIKE '%_valide'
        """), {"id": identifiant}).fetchone()
    if r is None:
        return False, "Aucune validation en attente pour ce compte."
    if r[0] == code:
        # dev ou medecin
        role = r[1].replace("_valide", "")    
        with engine.begin() as conn:
            conn.execute(text("UPDATE utilisateurs SET role=:r, statut=:r WHERE identifiant=:id"),
                         {"r": role, "id": identifiant})
        return True, f"Felicitation tu es maintenant {role} !"
    return False, "Code incorrect."