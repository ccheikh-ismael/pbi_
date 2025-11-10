# -*- coding: utf-8 -*-
# bankia_predict.py — Prédiction du volume de transactions (mois suivant)

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# -----------------------------
# 1) Chargement des données
# -----------------------------
XLSX = Path("Dataset_Bankia2025.xlsx")
CSV_CLIENTS = Path("Clients.csv")

if not XLSX.exists():
    raise FileNotFoundError(f"Introuvable: {XLSX.resolve()}")
if not CSV_CLIENTS.exists():
    raise FileNotFoundError(f"Introuvable: {CSV_CLIENTS.resolve()}")

xfile = pd.ExcelFile(XLSX)
required = {"Agences", "Produits_Bancaires", "Transactions", "Depenses"}
missing = set(xfile.sheet_names) ^ (set(xfile.sheet_names) & required)
# on vérifiera seulement la feuille Transactions pour ce script
transactions = pd.read_excel(xfile, "Transactions")
clients = pd.read_csv(CSV_CLIENTS, encoding="utf-8")

# Nettoyage minimal
for df in (transactions, clients):
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()


transactions["Date_Transaction"] = pd.to_datetime(transactions["Date_Transaction"], errors="coerce")
transactions["Montant"] = pd.to_numeric(transactions["Montant"], errors="coerce")

# -----------------------------
# 2) Agrégation Client x Mois
# -----------------------------
tx = transactions.dropna(subset=["ID_Client", "Date_Transaction"]).copy()
tx["YearMonth"] = tx["Date_Transaction"].dt.to_period("M").dt.to_timestamp()

# Compte mensuel par client
panel = (tx.groupby(["ID_Client", "YearMonth"])["ID_Transaction"]
           .count().reset_index(name="Tx_Month_Count"))

# Si données trop légères, on stoppe proprement
if panel.empty or panel["YearMonth"].nunique() < 3:
    print("Données mensuelles insuffisantes pour l'entraînement (moins de 3 mois distincts).")
    raise SystemExit(0)

# Features temporelles
panel = panel.sort_values(["ID_Client", "YearMonth"])
panel["Lag1"] = panel.groupby("ID_Client")["Tx_Month_Count"].shift(1)
panel["RollMean3"] = panel.groupby("ID_Client")["Tx_Month_Count"] \
                          .rolling(3).mean().reset_index(0, drop=True)

# Cible = valeur du mois courant
panel = panel.dropna(subset=["Lag1", "RollMean3"])
panel["Target"] = panel["Tx_Month_Count"]

# -----------------------------
# 3) Split temporel Train/Test
# -----------------------------
months_sorted = sorted(panel["YearMonth"].unique())
# On garde ~2 mois récents pour le test
if len(months_sorted) >= 4:
    split_date = months_sorted[-3]
else:
    split_date = months_sorted[max(1, len(months_sorted)-2)]

train = panel[panel["YearMonth"] < split_date]
test  = panel[panel["YearMonth"] >= split_date]

X_train = train[["Lag1", "RollMean3"]]
y_train = train["Target"]
X_test  = test[["Lag1", "RollMean3"]]
y_test  = test["Target"]

# Sécurité
if X_train.empty or X_test.empty:
    print("Jeu d'entraînement ou de test vide après split — vérifie la répartition temporelle.")
    raise SystemExit(0)

# -----------------------------
# 4) Modèle & évaluation
# -----------------------------
rf = RandomForestRegressor(n_estimators=300, random_state=42)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)
print(f"MAE: {mae:.3f} | R²: {r2:.3f}")

# Importance des variables (facultatif)
importances = pd.Series(rf.feature_importances_, index=["Lag1", "RollMean3"]).sort_values(ascending=False)
print("\nImportance des variables:")
print(importances)

# -----------------------------
# 5) Courbe Réel vs Prédit (agrégé)
# -----------------------------
agg_test = test.groupby("YearMonth")["Target"].sum().reset_index()
agg_pred = pd.DataFrame({"YearMonth": test["YearMonth"], "Pred": y_pred}) \
           .groupby("YearMonth")["Pred"].sum().reset_index()

plt.figure()
plt.plot(agg_test["YearMonth"], agg_test["Target"], label="Réel (somme clients)")
plt.plot(agg_pred["YearMonth"], agg_pred["Pred"], label="Prédit (somme clients)")
plt.title("Transactions mensuelles — Réel vs Prédit (agrégé)")
plt.xlabel("Mois")
plt.ylabel("Nombre de transactions")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.savefig("prediction_reel_vs_predit.png", dpi=150)
plt.show()

# -----------------------------
# 6) Inférence prochaine période (par client)
# -----------------------------
last_by_client = panel.sort_values(["ID_Client", "YearMonth"]).groupby("ID_Client").tail(1)
last_by_client["Pred_Next_Month_Tx"] = rf.predict(last_by_client[["Lag1","RollMean3"]])
last_by_client["Risque_Inactivite_Prochain_Mois"] = np.where(
    last_by_client["Pred_Next_Month_Tx"] <= 1, "Eleve", "Normal"
)

pred_clients = (last_by_client[["ID_Client","YearMonth","Lag1","RollMean3",
                                "Pred_Next_Month_Tx","Risque_Inactivite_Prochain_Mois"]]
                .rename(columns={"YearMonth":"Dernier_Mois_Observe"}))

# -----------------------------
# 7) KPI modèle & exports
# -----------------------------
kpi = pd.DataFrame([{
    "MAE": mae,
    "R2": r2,
    "Nb_Clients_Test": test["ID_Client"].nunique(),
    "Nb_Mois_Test": test["YearMonth"].nunique()
}])

pred_clients.to_csv("predictions_clients.csv", index=False)
kpi.to_csv("kpi_modele_pred.csv", index=False)

print("\n[OK] Fichiers exportés :")
print(" - predictions_clients.csv")
print(" - kpi_modele_pred.csv")
print(" - prediction_reel_vs_predit.png")
