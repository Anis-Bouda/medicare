from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Chemins du dataset et du dossier qui recevra les résultats de l'EDA.
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "hypertension_dataset.csv"
EDA_DIR = BASE_DIR / "outputs" / "eda"
TARGET = "Hypertension"


def save_current_figure(filename: str) -> None:
    """Enregistre proprement la figure courante puis libère la mémoire."""
    plt.tight_layout()
    plt.savefig(EDA_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()


def risk_rate_by_group(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calcule le nombre d'individus et le taux de classe High par groupe."""
    result = (
        df.groupby(column, observed=True)["High_Risk"]
        .agg(total="size", high_cases="sum", high_rate="mean")
        .reset_index()
    )
    result["high_rate_percent"] = result["high_rate"] * 100
    return result


def analyze_target_distribution(df: pd.DataFrame) -> None:
    """Étudie la répartition globale des classes High et Low."""
    distribution = df[TARGET].value_counts().rename_axis("class").reset_index(name="count")
    distribution["percentage"] = distribution["count"] / len(df) * 100
    distribution.to_csv(EDA_DIR / "target_distribution.csv", index=False)

    plt.figure(figsize=(6, 4))
    bars = plt.bar(distribution["class"], distribution["count"], color=["#c9483d", "#2f6f8f"])
    plt.title("Répartition globale du risque d'hypertension")
    plt.xlabel("Classe")
    plt.ylabel("Nombre d'individus")
    for bar, percentage in zip(bars, distribution["percentage"]):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{percentage:.1f}%", ha="center", va="bottom")
    save_current_figure("01_target_distribution.png")

    print("\nRépartition High / Low:")
    print(distribution.to_string(index=False))


def analyze_country(df: pd.DataFrame) -> None:
    """Compare le taux de risque High entre les pays."""
    country = risk_rate_by_group(df, "Country").sort_values("high_rate_percent")
    country.to_csv(EDA_DIR / "risk_by_country.csv", index=False)

    plt.figure(figsize=(9, 6))
    plt.barh(country["Country"], country["high_rate_percent"], color="#3f7d66")
    plt.title("Taux de risque High selon le pays")
    plt.xlabel("Taux de risque High (%)")
    plt.ylabel("Pays")
    save_current_figure("02_risk_by_country.png")


def analyze_age_groups(df: pd.DataFrame) -> None:
    """Analyse le risque d'hypertension par tranches d'âge."""
    age_bins = [17, 29, 39, 49, 59, 69, 79, 89]
    age_labels = ["18-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89"]
    df["Age_Group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels)

    age = risk_rate_by_group(df, "Age_Group")
    age.to_csv(EDA_DIR / "risk_by_age_group.csv", index=False)

    plt.figure(figsize=(8, 4))
    plt.plot(age["Age_Group"].astype(str), age["high_rate_percent"], marker="o", color="#9b4f69")
    plt.title("Taux de risque High selon la tranche d'âge")
    plt.xlabel("Tranche d'âge")
    plt.ylabel("Taux de risque High (%)")
    plt.grid(axis="y", alpha=0.25)
    save_current_figure("03_risk_by_age_group.png")


def analyze_medical_variables(df: pd.DataFrame) -> None:
    """Compare les principales variables médicales entre High et Low."""
    medical_columns = ["BMI", "Cholesterol", "Systolic_BP", "Diastolic_BP"]
    medical_summary = df.groupby(TARGET)[medical_columns].agg(["mean", "median", "std"])
    medical_summary.to_csv(EDA_DIR / "medical_variables_summary.csv")

    titles = ["IMC", "Cholestérol", "Pression systolique", "Pression diastolique"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for axis, column, title in zip(axes.flat, medical_columns, titles):
        values = [df.loc[df[TARGET] == label, column] for label in ["High", "Low"]]
        boxes = axis.boxplot(values, tick_labels=["High", "Low"], patch_artist=True, showfliers=False)
        boxes["boxes"][0].set_facecolor("#c9483d")
        boxes["boxes"][1].set_facecolor("#2f6f8f")
        axis.set_title(title)
        axis.set_xlabel("Classe")
    fig.suptitle("Variables médicales selon le risque d'hypertension")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(EDA_DIR / "04_medical_variables.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def analyze_lifestyle_variables(df: pd.DataFrame) -> None:
    """Analyse les variables de mode de vie catégorielles et numériques."""
    categorical_columns = ["Physical_Activity_Level", "Smoking_Status"]
    categorical_titles = ["Activité physique", "Statut tabagique"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for axis, column, title in zip(axes, categorical_columns, categorical_titles):
        result = risk_rate_by_group(df, column)
        result.to_csv(EDA_DIR / f"risk_by_{column.lower()}.csv", index=False)
        axis.bar(result[column], result["high_rate_percent"], color="#6a7f3f")
        axis.set_title(title)
        axis.set_xlabel("")
        axis.set_ylabel("Taux de risque High (%)")
        axis.tick_params(axis="x", rotation=20)
    fig.suptitle("Risque d'hypertension et habitudes de vie")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(EDA_DIR / "05_lifestyle_categories.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Création de tranches pour rendre les variables numériques comparables.
    df["Alcohol_Group"] = pd.cut(
        df["Alcohol_Intake"],
        bins=[-0.1, 5, 10, 15, 20, 25, 30],
        labels=["0-5", "5.1-10", "10.1-15", "15.1-20", "20.1-25", "25.1-30"],
    )
    df["Sleep_Group"] = pd.cut(
        df["Sleep_Duration"],
        bins=[3.9, 5, 6, 7, 8, 9, 10],
        labels=["4-5", "5.1-6", "6.1-7", "7.1-8", "8.1-9", "9.1-10"],
    )
    df["Salt_Group"] = pd.cut(
        df["Salt_Intake"],
        bins=[1.9, 4, 6, 8, 10, 12, 15],
        labels=["2-4", "4.1-6", "6.1-8", "8.1-10", "10.1-12", "12.1-15"],
    )

    numeric_groups = ["Alcohol_Group", "Stress_Level", "Sleep_Group", "Salt_Group"]
    numeric_titles = ["Alcool", "Niveau de stress", "Durée de sommeil", "Consommation de sel"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for axis, column, title in zip(axes.flat, numeric_groups, numeric_titles):
        result = risk_rate_by_group(df, column)
        result.to_csv(EDA_DIR / f"risk_by_{column.lower()}.csv", index=False)
        axis.plot(result[column].astype(str), result["high_rate_percent"], marker="o", color="#805d93")
        axis.set_title(title)
        axis.set_ylabel("Taux High (%)")
        axis.tick_params(axis="x", rotation=30)
        axis.grid(axis="y", alpha=0.25)
    fig.suptitle("Risque d'hypertension selon les variables de mode de vie")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(EDA_DIR / "06_lifestyle_numeric.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    df["High_Risk"] = (df[TARGET] == "High").astype(int)

    print(f"Dataset chargé : {len(df)} lignes et {df.shape[1] - 1} colonnes d'origine.")
    analyze_target_distribution(df)
    analyze_country(df)
    analyze_age_groups(df)
    analyze_medical_variables(df)
    analyze_lifestyle_variables(df)
    print(f"\nAnalyse exploratoire terminée. Résultats : {EDA_DIR}")


if __name__ == "__main__":
    main()
