import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text

#il faudra changer et merttre ceux de votre bdd
UTILISATEUR = "boudaanis"
HOTE = "localhost"
PORT = "5432"
NOM_BDD = "hypertension_db"

URL = f"postgresql+psycopg2://{UTILISATEUR}@{HOTE}:{PORT}/{NOM_BDD}"



# creer la base si elle existe pas
def creer_base_si_absente():
    # on se connecte a postgres pour pouvoir creer notre base
    conn = psycopg2.connect(dbname="postgres", user=UTILISATEUR, host=HOTE, port=PORT)
    conn.autocommit = True   # obligatoire pour creer une base
    cur = conn.cursor()
    # est ce que la base existe deja
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (NOM_BDD,))
    existe = cur.fetchone()
    if existe:
        print(f"ok la base '{NOM_BDD}' existe deja")
    else:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(NOM_BDD)))
        print(f"base '{NOM_BDD}' creee")
    cur.close()
    conn.close()



#creer les table et les collone si elles manque

def creer_tables():
    engine = create_engine(URL)

    sql_tables = """
    -- la table des utilisateur (pour la connexion)
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id SERIAL PRIMARY KEY,
        identifiant VARCHAR(50) UNIQUE NOT NULL,
        nom VARCHAR(100) NOT NULL,
        mot_de_passe VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'patient',
        cree_le TIMESTAMP DEFAULT NOW()
    );

    -- si la table existe deja mais sans les nouvelle collone on les ajoute
    ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS email VARCHAR(120);
    ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS statut VARCHAR(20) DEFAULT 'patient';
    ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS code_dev VARCHAR(20);
    ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS justificatif_fichier VARCHAR(255);

    -- la table des demande davis (entre le patient et le medecin)
    CREATE TABLE IF NOT EXISTS demandes_avis (
        id SERIAL PRIMARY KEY,
        patient_id INTEGER REFERENCES utilisateurs(id),
        patient_nom VARCHAR(100),
        message TEXT,
        fichier VARCHAR(255),
        reponse TEXT,
        medecin_nom VARCHAR(100),
        statut VARCHAR(20) DEFAULT 'en_attente',
        cree_le TIMESTAMP DEFAULT NOW()
    );

    -- la table qui garde les prediction faite par les user
    -- elle stocke tous : les donne du patient + le resultat
    CREATE TABLE IF NOT EXISTS donnees_utilisateurs (
        id SERIAL PRIMARY KEY,
        utilisateur_id INTEGER REFERENCES utilisateurs(id),
        age INTEGER,
        bmi DOUBLE PRECISION,
        cholesterol INTEGER,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        alcohol_intake DOUBLE PRECISION,
        stress_level INTEGER,
        salt_intake DOUBLE PRECISION,
        sleep_duration DOUBLE PRECISION,
        heart_rate INTEGER,
        ldl INTEGER,
        hdl INTEGER,
        triglycerides INTEGER,
        glucose INTEGER,
        -- le profil (les 8 categoriel)
        country VARCHAR(100),
        smoking_status VARCHAR(50),
        physical_activity_level VARCHAR(50),
        family_history VARCHAR(10),
        diabetes VARCHAR(10),
        gender VARCHAR(20),
        education_level VARCHAR(50),
        employment_status VARCHAR(50),
        -- le resultat
        prediction VARCHAR(10),
        probabilite DOUBLE PRECISION,
        saisi_le TIMESTAMP DEFAULT NOW()
    );

    -- si la table avait pas toutes les collone on les rajoute
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS alcohol_intake DOUBLE PRECISION;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS stress_level INTEGER;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS salt_intake DOUBLE PRECISION;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS sleep_duration DOUBLE PRECISION;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS heart_rate INTEGER;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS ldl INTEGER;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS hdl INTEGER;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS triglycerides INTEGER;
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS country VARCHAR(100);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS smoking_status VARCHAR(50);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS physical_activity_level VARCHAR(50);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS family_history VARCHAR(10);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS diabetes VARCHAR(10);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS education_level VARCHAR(50);
    ALTER TABLE donnees_utilisateurs ADD COLUMN IF NOT EXISTS employment_status VARCHAR(50);
    """

    with engine.begin() as conn:
        # on coupe le gros texte sql en plusieur instruction et on les lance une par une
        for instruction in sql_tables.strip().split(";"):
            if instruction.strip():
                conn.execute(text(instruction))
    print("ok les table et les collone sont verifiees / creees")

    # petit recap pour voir les table qui sont la
    with engine.connect() as conn:
        tables = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' ORDER BY table_name
        """)).fetchall()
        print("\nles table dans la base :")
        for t in tables:
            print("  -", t[0])



# verifier que le datset des patient est bien la
def verifier_patients():
    engine = create_engine(URL)
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'patients_hypertension'
            )
        """)).fetchone()
    if r[0]:
        #la table existe on compte les ligne
        with engine.connect() as conn:
            n = conn.execute(text("SELECT COUNT(*) FROM patients_hypertension")).fetchone()
        print(f"\nok la table patients_hypertension est la ({n[0]} ligne)")
    else:
        # elle existe pas il faut importer le csv
        print("\n/!\\ attention la table patients_hypertension existe pas.")
        print("    il faut limporter depuis le csv (le dataset des 174982 patient).")


if __name__ == "__main__":
    print("=== initialisation de la base medicare ===\n")
    creer_base_si_absente()
    creer_tables()
    verifier_patients()
    print("\n=== termine ===")