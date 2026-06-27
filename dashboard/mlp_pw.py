import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import logging
from donnees import charger_donnees
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import torch.optim as optim
from sklearn.metrics import accuracy_score, roc_auc_score

from outils_resultats import enregistrer_resultats
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import os, joblib
logging.getLogger("streamlit").setLevel(logging.ERROR)

# on récup3re les données depuis Postgresql
df = charger_donnees()

print("Lignes, colonnes :", df.shape)
print(df["hypertension"].value_counts())

y = (df["hypertension"] == "High").astype(int)
X = df.drop(columns=["hypertension", "id"])

# on decoupe nos donnes 
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_dev, X_test, y_dev, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

#on pose nos collones
colonnes_numeriques = [
    "age", "bmi", "cholesterol", "systolic_bp", "diastolic_bp",
    "alcohol_intake", "stress_level", "salt_intake", "sleep_duration",
    "heart_rate", "ldl", "hdl", "triglycerides", "glucose",
]
colonnes_categorielles = [
    "country", "smoking_status", "physical_activity_level",
    "family_history", "diabetes", "gender", "education_level",
    "employment_status",
]

# 
preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), colonnes_numeriques),
    ("cat", OneHotEncoder(handle_unknown="ignore"), colonnes_categorielles),
])


X_train_prepared = preprocessor.fit_transform(X_train)
X_dev_prepared   = preprocessor.transform(X_dev)
X_test_prepared  = preprocessor.transform(X_test)

print("train :", X_train_prepared.shape,
      "| dev :", X_dev_prepared.shape,
      "| test :", X_test_prepared.shape)

Xtr = torch.tensor(X_train_prepared.astype("float32"))
ytr = torch.tensor(y_train.values.astype("float32"))
Xdv = torch.tensor(X_dev_prepared.astype("float32"))
ydv = torch.tensor(y_dev.values.astype("float32"))
Xte = torch.tensor(X_test_prepared.astype("float32"))
yte = torch.tensor(y_test.values.astype("float32"))

# on découpe le train
train_loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=256, shuffle=True)

# couche chache du reseau 
class MLP(nn.Module):
    def __init__(self, d, m):
        super().__init__()
        #entre 52 
        self.lin1 = nn.Linear(d, m)     
        self.lin2 = nn.Linear(m, 1)     
    def forward(self, x):
        z = self.lin1(x)
        # on active relu
        h = torch.relu(z)               
        #le ligit pas le sig
        s = self.lin2(h).squeeze(-1)    
        return s

d = Xtr.shape[1]          
#32 neurone cache 
model = MLP(d, m=32)      
print(model)


# on calcule un poids pour reequilibrer les classes
n_high = (y_train == 1).sum()
n_low  = (y_train == 0).sum()
poids = torch.tensor([n_low / n_high], dtype=torch.float32)

criterion = nn.BCEWithLogitsLoss(pos_weight=poids)   
#on ajuste les poids
optimizer = optim.SGD(model.parameters(), lr=0.05,    
                      momentum=0.9, weight_decay=1e-4)

# la boucle d'apprentissage
for epoch in range(50):                              
    model.train()
    for xb, yb in train_loader:                    
        optimizer.zero_grad()                      
        logits = model(xb)                         
        loss = criterion(logits, yb)               
        loss.backward()                             
        optimizer.step()                              
    print(f"époque {epoch+1}/50 — erreur = {loss.item():.4f}")
    
    

model.eval()
with torch.no_grad():
    proba_dev  = torch.sigmoid(model(Xdv)).numpy()    
    proba_test = torch.sigmoid(model(Xte)).numpy()    
#pour le dev
pred_dev  = (proba_dev  >= 0.5).astype(int)
#pour le test 
pred_test = (proba_test >= 0.5).astype(int)

print("--- DEV (pour régler les hyperparamètres) ---")
print("Accuracy :", accuracy_score(y_dev, pred_dev))
print("ROC-AUC  :", roc_auc_score(y_dev, proba_dev))

print("--- TEST (pour la comparaison finale) ---")
print("Accuracy :", accuracy_score(y_test, pred_test))
print("ROC-AUC  :", roc_auc_score(y_test, proba_test))
print("Accuracy :", accuracy_score(y_test, pred_test))
print("ROC-AUC  :", roc_auc_score(y_test, proba_test))

print(classification_report(y_test, pred_test, target_names=["Low", "High"]))

print(confusion_matrix(y_test, pred_test))


enregistrer_resultats("MLP (pos_weight)", y_test, pred_test, proba_test)

#on sauvgardes les res pour les poredictions 
os.makedirs("artefacts", exist_ok=True)
torch.save(model.state_dict(), "artefacts/mlp_pw.pth")
joblib.dump({"d": d, "m": 32}, "artefacts/mlp_pw_config.pkl")
print("MLP pos_weight sauvegardé")