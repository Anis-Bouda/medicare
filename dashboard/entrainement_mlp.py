import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import os, joblib
import numpy as np
import logging
from donnees import charger_donnees
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import torch.optim as optim
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from outils_resultats import enregistrer_resultats
import itertools
from sklearn.metrics import accuracy_score, roc_auc_score

logging.getLogger("streamlit").setLevel(logging.ERROR)

# on recup les données depuis Postgresql
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

# on utilise un preprocesseur 
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

# on converti en tenseur de la bib pytorch 
Xtr = torch.tensor(X_train_prepared.astype("float32"))
ytr = torch.tensor(y_train.values.astype("float32"))
Xdv = torch.tensor(X_dev_prepared.astype("float32"))
ydv = torch.tensor(y_dev.values.astype("float32"))
Xte = torch.tensor(X_test_prepared.astype("float32"))
yte = torch.tensor(y_test.values.astype("float32"))

# on découpe le train en mini-lots de 256
train_loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=256, shuffle=True)

# -on fait une couche cache 
class MLP(nn.Module):
    def __init__(self, d, m):
        super().__init__()
        self.lin1 = nn.Linear(d, m)     # entrée (d=52) -> couche cachée (m)
        self.lin2 = nn.Linear(m, 1)     # couche cachée -> 1 sortie

    def forward(self, x):
        z = self.lin1(x)
        h = torch.relu(z)               # activation ReLU
        s = self.lin2(h).squeeze(-1)    # le logit (pas de sigmoïde ici)
        return s

d = Xtr.shape[1]          
#32 neurone cache 
model = MLP(d, m=32)      
print(model)


# la mesure d'erreur
criterion = nn.BCEWithLogitsLoss()                    
# on ajuste les poids
optimizer = optim.SGD(model.parameters(), lr=0.05,    
                      momentum=0.9, weight_decay=1e-4)

# apprentissage 
for epoch in range(50):                               
    model.train()
    for xb, yb in train_loader:                     
        #remet les gradients à zéro  
        optimizer.zero_grad()                   
         #le réseau prédit      
        logits = model(xb)                       
        # mesure l'erreur    
        loss = criterion(logits, yb)               
        #la loss
        loss.backward()                              
         #ajuste les poids
        optimizer.step()                              
    print(f"époque {epoch+1}/50 — erreur = {loss.item():.4f}")
    
 #eval du model pour tran et dev lun pour la comaraision avec les autre model et dev pour choisir les hyperparametre    
model.eval()
with torch.no_grad():
    proba_dev  = torch.sigmoid(model(Xdv)).numpy()
    proba_test = torch.sigmoid(model(Xte)).numpy()

pred_dev  = (proba_dev  >= 0.5).astype(int)
pred_test = (proba_test >= 0.5).astype(int)

print(" DEV ")
print("Accuracy :", accuracy_score(y_dev, pred_dev))
print("ROC-AUC  :", roc_auc_score(y_dev, proba_dev))

print("TEST ")
print("Accuracy :", accuracy_score(y_test, pred_test))
print("ROC-AUC  :", roc_auc_score(y_test, proba_test))

print(classification_report(y_test, pred_test, target_names=["Low", "High"]))

print(confusion_matrix(y_test, pred_test))

enregistrer_resultats("MLP", y_test, pred_test, proba_test)



# test pour chpoisir es meilleur hyperparametres je teste mais bon la on a toujr le meme res 
grille_m  = [16, 32, 64]
grille_lr = [0.01, 0.05, 0.1]

print(f"\n{'m':>4} {'lr':>6} {'acc_dev':>9} {'auc_dev':>9}")
resultats = []
for m, lr in itertools.product(grille_m, grille_lr):
    torch.manual_seed(42)
    mdl  = MLP(d, m)
    crit = nn.BCEWithLogitsLoss()
    opt  = optim.SGD(mdl.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
    for _ in range(20):                      
        mdl.train()
        for xb, yb in train_loader:
            opt.zero_grad(); crit(mdl(xb), yb).backward(); opt.step()
    mdl.eval()
    with torch.no_grad():
        p = torch.sigmoid(mdl(Xdv)).numpy()
    pr  = (p >= 0.5).astype(int)
    acc = accuracy_score(y_dev, pr); auc = roc_auc_score(y_dev, p)
    resultats.append((m, lr, acc, auc))
    print(f"{m:>4} {lr:>6} {acc:>9.4f} {auc:>9.4f}")
#rouver la meilleur accuracy 
best = max(resultats, key=lambda r: r[2])    
print(f"\nMeilleure combinaison (dev) : m={best[0]}, lr={best[1]} "
      f"-> acc={best[2]:.4f}, auc={best[3]:.4f}")

# sauvegarde des artefacts pour prediction et comparaision

os.makedirs("artefacts/modeles", exist_ok=True)
joblib.dump(preprocessor, "artefacts/preprocessor.pkl")
torch.save(model.state_dict(), "artefacts/mlp.pth")
joblib.dump({"d": d, "m": 32}, "artefacts/mlp_config.pkl")
print("Artefacts MLP sauvegardés dans artefacts/")