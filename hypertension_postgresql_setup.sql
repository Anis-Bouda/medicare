CREATE DATABASE hypertension_db;

-- Connexion a la base qui vient d'etre creee.
\connect hypertension_db

DROP TABLE IF EXISTS patients_hypertension;

CREATE TABLE patients_hypertension (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    bmi NUMERIC(4,1) NOT NULL,
    cholesterol INT NOT NULL,
    systolic_bp INT NOT NULL,
    diastolic_bp INT NOT NULL,
    smoking_status VARCHAR(50) NOT NULL,
    alcohol_intake NUMERIC(4,1) NOT NULL,
    physical_activity_level VARCHAR(50) NOT NULL,
    family_history VARCHAR(10) NOT NULL,
    diabetes VARCHAR(10) NOT NULL,
    stress_level INT NOT NULL,
    salt_intake NUMERIC(4,1) NOT NULL,
    sleep_duration NUMERIC(3,1) NOT NULL,
    heart_rate INT NOT NULL,
    ldl INT NOT NULL,
    hdl INT NOT NULL,
    triglycerides INT NOT NULL,
    glucose INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    education_level VARCHAR(50) NOT NULL,
    employment_status VARCHAR(50) NOT NULL,
    hypertension VARCHAR(10) NOT NULL
);

-- Importation du fichier CSV dans la table avec un chemin relatif.
-- Lancer psql depuis le dossier contenant ce script et hypertension_dataset.csv.
\copy patients_hypertension(country, age, bmi, cholesterol, systolic_bp, diastolic_bp, smoking_status, alcohol_intake, physical_activity_level, family_history, diabetes, stress_level, salt_intake, sleep_duration, heart_rate, ldl, hdl, triglycerides, glucose, gender, education_level, employment_status, hypertension) FROM 'hypertension_dataset.csv' WITH (FORMAT csv, HEADER true);

-- Requetes simples de verification.
SELECT COUNT(*) AS total_rows
FROM patients_hypertension;

SELECT hypertension, COUNT(*) AS count
FROM patients_hypertension
GROUP BY hypertension
ORDER BY hypertension;

SELECT
    COUNT(*) FILTER (WHERE country IS NULL) AS missing_country,
    COUNT(*) FILTER (WHERE age IS NULL) AS missing_age,
    COUNT(*) FILTER (WHERE bmi IS NULL) AS missing_bmi,
    COUNT(*) FILTER (WHERE hypertension IS NULL) AS missing_hypertension
FROM patients_hypertension;

SELECT country, COUNT(*) AS count
FROM patients_hypertension
GROUP BY country
ORDER BY count DESC
LIMIT 10;

SELECT
    MIN(age) AS min_age,
    MAX(age) AS max_age,
    ROUND(AVG(age), 2) AS avg_age,
    MIN(bmi) AS min_bmi,
    MAX(bmi) AS max_bmi,
    ROUND(AVG(bmi), 2) AS avg_bmi
FROM patients_hypertension;
