# -*- coding: utf-8 -*-
# bankia_eda.py
# EDA + visualisations pour Bankia (transactions, produits, segments)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------- FICHIERS (dans le même dossier que ce script) ----------
XLSX_PATH = Path("Dataset_Bankia2025.xlsx")  # 4 feuilles: Agences, Produits_Bancaires, Transactions, Depenses
CSV_CLIENTS = Path("Clients.csv")            # colonnes: ID_Client, Nom_Client, Prenom_Client, Email, Téléphone, Ville, Pays, Segment_Client

# ---------- CHARGEMENT ----------
if not XLSX_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable: {XLSX_PATH.resolve()}")
if not CSV_CLIENTS.exists():
    raise FileNotFoundError(f"Fichier introuvable: {CSV_CLIENTS.resolve()}")

x = pd.ExcelFile(XLSX_PATH)
sheet_names = set(x.sheet_names)
required = {"Agences", "Produits_Bancaires", "Transactions", "Depenses"}
missing = required - sheet_names
if missing:
    raise ValueError(f"Feuilles manquantes dans l'Excel: {missing}")

agences = pd.read_excel(x, "Agences")
produits = pd.read_excel(x, "Produits_Bancaires")
transactions = pd.read_excel(x, "Transactions")
depenses = pd.read_excel(x, "Depenses")
clients = pd.read_csv(CSV_CLIENTS, encoding="utf-8")

# ---------- NETTOYAGE MINIMAL ----------
def clean_str_df(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    return df

for df in [agences, produits, transactions, depenses, clients]:
    clean_str_df(df)

# types et formats
if "Date_Transaction" in transactions.columns:
    transactions["Date_Transaction"] = pd.to_datetime(transactions["Date_Transaction"], errors="coerce")
if "Montant" in transactions.columns:
    transactions["Montant"] = pd.to_numeric(transactions["Montant"], errors="coerce")

# Standardise ville/pays si présents
for df in [agences, clients]:
    for c in ["Ville", "Pays"]:
        if c in df.columns:
            df[c] = df[c].str.title()

# ---------- AGRÉGATS ----------
# 1) Transactions par type
tx_by_type = (transactions
              .groupby("Type_Transaction", as_index=False)
              .agg(Nb_Tx=("ID_Transaction", "count"),
                   Montant_Total=("Montant", "sum"))
              .sort_values("Nb_Tx", ascending=False))

# 2) Tendances mensuelles (count & sum)
if "Date_Transaction" in transactions.columns and transactions["Date_Transaction"].notna().any():
    transactions["YearMonth"] = transactions["Date_Transaction"].dt.to_period("M").dt.to_timestamp()
    tx_monthly = (transactions
                  .groupby("YearMonth", as_index=False)
                  .agg(Nb_Tx=("ID_Transaction", "count"),
                       Montant_Total=("Montant", "sum"))
                  .sort_values("YearMonth"))
else:
    tx_monthly = pd.DataFrame(columns=["YearMonth", "Nb_Tx", "Montant_Total"])

# 3) Top produits par recette
tx_prod = transactions.merge(
    produits[["ID_Produit", "Nom_Produit", "Catégorie"]],
    on="ID_Produit", how="left"
)
top_products = (tx_prod.groupby(["ID_Produit", "Nom_Produit", "Catégorie"], as_index=False)
                .agg(Recette=("Montant", "sum"))
                .sort_values("Recette", ascending=False)
                .head(10))

# 4) Transactions par segment client
tx_client = transactions.merge(clients[["ID_Client", "Segment_Client"]], on="ID_Client", how="left")
tx_by_segment = (tx_client.groupby("Segment_Client", as_index=False)
                 .agg(Nb_Tx=("ID_Transaction", "count"),
                      Montant_Total=("Montant", "sum"))
                 .sort_values("Montant_Total", ascending=False))

# ---------- VISUALISATIONS (matplotlib pur, 1 figure par graphique) ----------
# Graphique 1 : Nombre de transactions par type
plt.figure()
if not tx_by_type.empty:
    plt.bar(tx_by_type["Type_Transaction"], tx_by_type["Nb_Tx"])
    plt.title("Nombre de transactions par type")
    plt.xlabel("Type de transaction")
    plt.ylabel("Nombre de transactions")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
else:
    plt.text(0.5, 0.5, "Pas de données pour 'Type_Transaction'", ha="center")
    plt.axis("off")
plt.show()

# Graphique 2 : Tendance mensuelle (Nb_Tx)
plt.figure()
if not tx_monthly.empty:
    plt.plot(tx_monthly["YearMonth"], tx_monthly["Nb_Tx"])
    plt.title("Évolution mensuelle - Nombre de transactions")
    plt.xlabel("Mois")
    plt.ylabel("Nombre de transactions")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
else:
    plt.text(0.5, 0.5, "Pas de données mensuelles", ha="center")
    plt.axis("off")
plt.show()

# Graphique 3 : Tendance mensuelle (Montant_Total)
plt.figure()
if not tx_monthly.empty:
    plt.plot(tx_monthly["YearMonth"], tx_monthly["Montant_Total"])
    plt.title("Évolution mensuelle - Montant total")
    plt.xlabel("Mois")
    plt.ylabel("Montant total")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
else:
    plt.text(0.5, 0.5, "Pas de données mensuelles", ha="center")
    plt.axis("off")
plt.show()

# Graphique 4 : Top 10 produits par recette
plt.figure()
if not top_products.empty:
    plt.bar(top_products["Nom_Produit"], top_products["Recette"])
    plt.title("Top 10 produits par recette")
    plt.xlabel("Produit")
    plt.ylabel("Recette totale")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
else:
    plt.text(0.5, 0.5, "Pas de données produits", ha="center")
    plt.axis("off")
plt.show()

# ---------- EXPORTS (pour Power BI si besoin) ----------
OUT_DIR = Path(".")
tx_by_type.to_csv(OUT_DIR / "tx_by_type.csv", index=False)
tx_monthly.to_csv(OUT_DIR / "tx_monthly.csv", index=False)
top_products.to_csv(OUT_DIR / "top_products.csv", index=False)
tx_by_segment.to_csv(OUT_DIR / "tx_by_segment.csv", index=False)

print("[OK] Exports créés : tx_by_type.csv, tx_monthly.csv, top_products.csv, tx_by_segment.csv")
