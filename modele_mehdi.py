import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
import joblib

# ---------------------------------------------------------
# 1. Chargement et preparation des donnees (Train/Dev/Test)
# ---------------------------------------------------------

# TODO : METS TON VRAI MOT DE PASSE ICI AVANT DE LANCER LE SCRIPT
engine = create_engine('postgresql+psycopg2://mehdib:Bourkeb2004@localhost/hypertension_db')
data = pd.read_sql("SELECT * FROM patients_hypertension;", engine)

if 'id' in data.columns:
    data = data.drop(columns=['id'])

# Separation des features (X) et du label (y)
X = data.drop(columns=["hypertension"])
y = data["hypertension"].map({"Low": 0, "High": 1}).values 

colonnes_numeriques = ["age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp", "alcohol_intake", "stress_level", "salt_intake", "sleep_duration", "heart_rate", "ldl", "hdl", "triglycerides", "glucose"]
colonnes_categorielles = ["country", "smoking_status", "physical_activity_level", "family_history", "diabetes", "gender", "education_level", "employment_status"]

# sparse_output=False pour avoir une matrice NumPy classique
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), colonnes_numeriques),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), colonnes_categorielles)
    ]
)

# Separation en 3 parties (70% Train, 15% Dev, 15% Test)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
X_dev, X_test, y_dev, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

X_train_prep = preprocessor.fit_transform(X_train)
X_dev_prep = preprocessor.transform(X_dev)
X_test_prep = preprocessor.transform(X_test)


# ---------------------------------------------------------
# 2. Implementation de la Regression Logistique (From Scratch)
# ---------------------------------------------------------

class LogisticRegressionFromScratch:
    def __init__(self, lr=0.1, epochs=1000, l2=0.0):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.w = None
        self.b = 0.0
        
        # Le seuil de decision (optimise plus tard)
        self.threshold = 0.5 
        
        # Variables pour sauvegarder le meilleur modele (TP3 Section 10.3)
        self.best_epoch = None
        self.best_w = None
        self.best_b = None
        self.best_threshold = 0.5

    def sigmoid(self, z):
        # Evite les erreurs d'overflow avec l'exponentielle
        z = np.clip(z, -250, 250)
        return 1.0 / (1.0 + np.exp(-z))

    def predict_proba(self, X):
        z = np.dot(X, self.w) + self.b
        return self.sigmoid(z)

    def predict(self, X):
        # 💡 On utilise le seuil OPTIMAL trouve au lieu du 0.5 classique
        return (self.predict_proba(X) >= self.threshold).astype(int)

    def compute_loss(self, X, y):
        p = self.predict_proba(X)
        p = np.clip(p, 1e-12, 1.0 - 1e-12)
        
        # Binary cross-entropy + penalite L2
        bce = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
        l2_penalty = (self.l2 / 2) * np.sum(self.w ** 2)
        return bce + l2_penalty

    def fit(self, X_train, y_train, X_dev=None, y_dev=None):
        N, d = X_train.shape
        self.w = np.zeros(d)
        self.b = 0.0
        
        best_dev_f1 = -1
        best_dev_loss = float('inf')

        for epoch in range(self.epochs):
            # 1. Probabilites et erreurs classiques
            p = self.predict_proba(X_train)
            err = p - y_train
            
            # 2. Gradients naturels (sans bidouiller les poids)
            dw = (1 / N) * np.dot(X_train.T, err) + (self.l2 * self.w)
            db = (1 / N) * np.sum(err)

            # 3. Mise a jour
            self.w -= self.lr * dw
            self.b -= self.lr * db

            # 4. Selection sur D_dev et RECHERCHE DU MEILLEUR SEUIL (Threshold Tuning)
            if X_dev is not None and y_dev is not None:
                p_dev = self.predict_proba(X_dev)
                
                meilleur_t_local = 0.5
                meilleur_f1_local = -1
                
                # L'algorithme teste plein de seuils pour contrer le desequilibre des donnees
                for t in np.arange(0.60, 0.80, 0.01):
                    dev_pred_test = (p_dev >= t).astype(int)
                    f1_test = f1_score(y_dev, dev_pred_test, average='macro', zero_division=0)
                    if f1_test > meilleur_f1_local:
                        meilleur_f1_local = f1_test
                        meilleur_t_local = t
                        
                self.threshold = meilleur_t_local
                dev_loss_val = self.compute_loss(X_dev, y_dev)
                
                # Sauvegarde du meilleur checkpoint
                if meilleur_f1_local > best_dev_f1 or (meilleur_f1_local == best_dev_f1 and dev_loss_val < best_dev_loss):
                    best_dev_f1 = meilleur_f1_local
                    best_dev_loss = dev_loss_val
                    self.best_epoch = epoch
                    self.best_w = self.w.copy()
                    self.best_b = self.b
                    self.best_threshold = meilleur_t_local

            # Affichage de suivi
            if epoch % 100 == 0 or epoch == self.epochs - 1:
                train_loss = self.compute_loss(X_train, y_train)
                msg = f"Epoch {epoch:4d}/{self.epochs} | Train Loss: {train_loss:.4f}"
                if X_dev is not None:
                    msg += f" | Dev Macro-F1: {meilleur_f1_local:.4f} (Seuil idéal: {meilleur_t_local:.2f})"
                print(msg)

        if self.best_w is not None:
            self.w = self.best_w
            self.b = self.best_b
            self.threshold = self.best_threshold
            print(f"\n=> Fin de l'entrainement. Meilleur modele restaure (Epoch {self.best_epoch})")
            print(f"=> Dev Macro-F1: {best_dev_f1:.4f} avec un Seuil de coupure optimise a {self.threshold:.2f}")


# ---------------------------------------------------------
# 3. Execution et evaluation finale sur D_test
# ---------------------------------------------------------

print("\nLancement du Batch Gradient Descent (From Scratch avec Threshold Tuning)...")
model = LogisticRegressionFromScratch(lr=0.5, epochs=1000, l2=0.0001)

model.fit(X_train_prep, y_train, X_dev_prep, y_dev)

print("\nEvaluation finale sur D_test :")
y_pred_test = model.predict(X_test_prep)

print(f"Test Accuracy : {accuracy_score(y_test, y_pred_test):.4f}")
print(f"Test Macro-F1 : {f1_score(y_test, y_pred_test, average='macro'):.4f}")
print("\nMatrice de confusion :")
print(confusion_matrix(y_test, y_pred_test))
print("\nRapport de classification :")
print(classification_report(y_test, y_pred_test, target_names=['Faible (Low)', 'Élevé (High)']))

# Sauvegarde pour le projet
joblib.dump(model, 'modele_lr_mehdi.pkl')
joblib.dump(preprocessor, 'preprocessor.pkl')
print("\nFichiers sauvegardes : modele_lr_mehdi.pkl et preprocessor.pkl")
