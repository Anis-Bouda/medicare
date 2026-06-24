import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASELINE = 0.7188
os.makedirs("figures", exist_ok=True)

if not os.path.exists("resultats/metrics.csv"):
    raise SystemExit("Aucun résultat : lance d'abord tes modèles.")

df = pd.read_csv("resultats/metrics.csv").sort_values("auc", ascending=False).reset_index(drop=True)

# affichage terminal pour verrifier les res 
print("\nComparaison des modees")
cols = ["modele", "accuracy", "precision", "rappel", "f1", "auc", "recall_low", "recall_high"]
print(df[cols].to_string(index=False))

# les graphique des scores 
fig, (a1, a2) = plt.subplots(1, 2, figsize=(max(10, 1.8 * len(df)), 5))
noms = df["modele"].tolist()

a1.bar(noms, df["accuracy"], color="#5AA9C9")
a1.axhline(BASELINE, color="black", ls="--", lw=1, label=f"baseline {BASELINE*100:.1f}%")
a1.set_ylim(0, 1); a1.set_ylabel("Accuracy"); a1.set_title("Accuracy", fontweight="bold")
a1.tick_params(axis="x", rotation=30); a1.legend()
for i, v in enumerate(df["accuracy"]):
    a1.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")

a2.bar(noms, df["auc"], color="#6a4c93")
a2.axhline(0.50, color="red", ls="--", lw=1, label="hasard (0.50)")
a2.set_ylim(0, 1); a2.set_ylabel("ROC-AUC"); a2.set_title("AUC", fontweight="bold")
a2.tick_params(axis="x", rotation=30); a2.legend()
for i, v in enumerate(df["auc"]):
    a2.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")

fig.suptitle("Comparaison des modèles — scores", fontsize=14, fontweight="bold")
fig.tight_layout(); fig.savefig("figures/comparaison_scores.png"); plt.close(fig)

#matrice de confusion
n = len(df)
ncols = min(3, n)
nrows = (n + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 4 * nrows))
axes = np.array(axes).reshape(-1)

for ax, (_, row) in zip(axes, df.iterrows()):
    cm = np.array([[row["low_low"], row["low_high"]],
                   [row["high_low"], row["high_high"]]])
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["préd. Low", "préd. High"], fontsize=9)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["vrai Low", "vrai High"], fontsize=9)
    for i in range(2):
        for j in range(2):
            couleur = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, f"{cm[i, j]:,}".replace(",", " "), ha="center", va="center",
                    fontsize=12, color=couleur, fontweight="bold")
    ax.set_title(f"{row['modele']}\nrecall Low={row['recall_low']:.2f} | "
                 f"High={row['recall_high']:.2f}", fontsize=10, fontweight="bold")

for ax in axes[n:]:
    ax.axis("off")

fig.suptitle("Détection des classes par modèle", fontsize=14, fontweight="bold")
fig.tight_layout(); fig.savefig("figures/grille_confusion.png"); plt.close(fig)

print("\nGraphiques enregistrés :")
print("  figures/comparaison_scores.png")
print("  figures/grille_confusion.png")