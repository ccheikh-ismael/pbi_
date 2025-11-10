# -*- coding: utf-8 -*-
# bankia_segmentation.py — Segmentation K-Means (RFM + mix produits / types)

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

XLSX = Path("Dataset_Bankia2025.xlsx")
CSV_CLIENTS = Path("Clients.csv")

if not XLSX.exists(): raise FileNotFoundError(f"Introuvable: {XLSX.resolve()}")
if not CSV_CLIENTS.exists(): raise FileNotFoundError(f"Introuvable: {CSV_CLIENTS.resolve()}")

# ----- Chargement -----
x = pd.ExcelFile(XLSX)
transactions = pd.read_excel(x, "Transactions")
produits     = pd.read_excel(x, "Produits_Bancaires")
clients      = pd.read_csv(CSV_CLIENTS, encoding="utf-8")

# ----- Nettoyage minimal -----
for df in (transactions, produits, clients):
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()

transactions["Date_Transaction"] = pd.to_datetime(transactions["Date_Transaction"], errors="coerce")
transactions["Montant"] = pd.to_numeric(transactions["Montant"], errors="coerce")

# Sécurité : on garde les lignes valides
tx = transactions.dropna(subset=["ID_Client","Date_Transaction"]).copy()
tx["Montant"] = tx["Montant"].fillna(0)

# ----- Features RFM & fréquence -----
ref_date = tx["Date_Transaction"].max() + pd.Timedelta(days=1)

agg_num = (tx.groupby("ID_Client")
             .agg(Tx_Count=("ID_Transaction","count"),
                  Tx_Sum=("Montant","sum"),
                  Tx_Mean=("Montant","mean"),
                  Derniere_Tx=("Date_Transaction","max"))
             .reset_index())
agg_num["Recency_Jours"] = (ref_date - agg_num["Derniere_Tx"]).dt.days

tx["YearMonth"] = tx["Date_Transaction"].dt.to_period("M")
freq_mois = (tx.groupby(["ID_Client","YearMonth"])["ID_Transaction"]
               .count().reset_index(name="Tx_Month_Count"))
freq_summary = (freq_mois.groupby("ID_Client")["Tx_Month_Count"]
                .agg(Freq_Moy="mean", Freq_Max="max").reset_index())

# ----- Mix par type de transaction (proportions) -----
mix_type = (tx.pivot_table(index="ID_Client", columns="Type_Transaction",
                           values="ID_Transaction", aggfunc="count", fill_value=0))
mix_type = mix_type.div(mix_type.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
mix_type.columns = [f"Type__{c}" for c in mix_type.columns]
mix_type = mix_type.reset_index()

# ----- Mix par catégorie produit (proportions) -----
txp = tx.merge(produits[["ID_Produit","Catégorie"]], on="ID_Produit", how="left")
mix_cat = (txp.pivot_table(index="ID_Client", columns="Catégorie",
                           values="ID_Transaction", aggfunc="count", fill_value=0))
mix_cat = mix_cat.div(mix_cat.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
mix_cat.columns = [f"Cat__{c}" for c in mix_cat.columns]
mix_cat = mix_cat.reset_index()

# ----- Table features finale -----
features = clients[["ID_Client","Segment_Client"]].merge(
    agg_num.drop(columns=["Derniere_Tx"]), on="ID_Client", how="left"
).merge(freq_summary, on="ID_Client", how="left"
).merge(mix_type, on="ID_Client", how="left"
).merge(mix_cat, on="ID_Client", how="left")

for c in ["Tx_Count","Tx_Sum","Tx_Mean","Recency_Jours","Freq_Moy","Freq_Max"]:
    if c in features.columns: features[c] = features[c].fillna(0)
mix_cols = [c for c in features.columns if c.startswith("Type__") or c.startswith("Cat__")]
features[mix_cols] = features[mix_cols].fillna(0)

num_cols = ["Tx_Count","Tx_Sum","Tx_Mean","Recency_Jours","Freq_Moy","Freq_Max"] + mix_cols
X = features[num_cols].copy()

if len(X) < 5:
    raise SystemExit("Données insuffisantes (<5 clients) pour lancer K-Means.")

# ----- Standardisation -----
scaler = StandardScaler()
Xs = scaler.fit_transform(X)

# ----- Choix automatique du k (2..6) via silhouette -----
best_k, best_score = None, -1
for k in range(2, min(7, len(X))):  # borne haute = 6 ou nb lignes -1
    kmeans = KMeans(n_clusters=k, n_init=20, random_state=42)
    labels = kmeans.fit_predict(Xs)
    try:
        s = silhouette_score(Xs, labels)
        if s > best_score:
            best_k, best_score = k, s
    except Exception:
        continue

if best_k is None: best_k = 4  # fallback
kmeans = KMeans(n_clusters=best_k, n_init=20, random_state=42)
features["Cluster"] = kmeans.fit_predict(Xs)

# ----- Étiquettes lisibles (heuristiques) -----
q_txsum75  = np.nanquantile(features["Tx_Sum"], 0.75) if features["Tx_Sum"].notna().any() else 0
q_txmean75 = np.nanquantile(features["Tx_Mean"],0.75) if features["Tx_Mean"].notna().any() else 0
q_freq75   = np.nanquantile(features["Freq_Moy"],0.75) if features["Freq_Moy"].notna().any() else 0
q_rec75    = np.nanquantile(features["Recency_Jours"],0.75) if features["Recency_Jours"].notna().any() else 0
q_txcount25= np.nanquantile(features["Tx_Count"],0.25) if features["Tx_Count"].notna().any() else 0

def label_row(r):
    if r["Tx_Sum"] >= q_txsum75 and r["Freq_Moy"] >= q_freq75:
        return "Premium (valeur & frequence elevees)"
    if r["Tx_Count"] <= q_txcount25 and r["Recency_Jours"] >= q_rec75:
        return "Inactif / A reactiver"
    if r["Tx_Mean"] >= q_txmean75:
        return "Ticket moyen eleve"
    return "Regulier"

features["Segment_Label"] = features.apply(label_row, axis=1)

# ----- PCA pour scatter 2D -----
pca = PCA(n_components=2, random_state=42)
pts = pca.fit_transform(Xs)
features["PC1"], features["PC2"] = pts[:,0], pts[:,1]

# ----- Exports -----
out_clients = "clients_clusters.csv"
out_overvw  = "segmentation_overview.csv"
out_pca     = "pca_coordinates.csv"

features_out = features[["ID_Client","Segment_Client","Cluster","Segment_Label","PC1","PC2"] + num_cols]
features_out.to_csv(out_clients, index=False)

overview = (features_out
            .groupby(["Cluster","Segment_Label"], as_index=False)
            .agg(Nb_Clients=("ID_Client","count"),
                 Tx_Sum_Moy=("Tx_Sum","mean"),
                 Freq_Moy_Moy=("Freq_Moy","mean"),
                 Recency_Med=("Recency_Jours","median")))
overview.to_csv(out_overvw, index=False)

features_out[["ID_Client","Cluster","PC1","PC2"]].to_csv(out_pca, index=False)

print("[OK] Exports :")
print(" -", out_clients)
print(" -", out_overvw)
print(" -", out_pca)

# ----- (Option) Scatter PNG -----
plt.figure()
for cl in sorted(features_out["Cluster"].unique()):
    m = features_out["Cluster"] == cl
    plt.scatter(features_out.loc[m,"PC1"], features_out.loc[m,"PC2"], label=f"Cluster {cl}")
plt.title(f"Clusters clients (PCA 2D) — k={best_k}")
plt.xlabel("PC1"); plt.ylabel("PC2"); plt.legend(); plt.tight_layout()
plt.savefig("clusters_pca.png", dpi=150)
print(" - clusters_pca.png")
