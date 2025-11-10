# 📘 Projet Bankia 2025 – Bonus Power BI  
## 🔍 README – Analyse Prédictive & Segmentation Dynamique des Clients  

---

## 🧠 1. Analyse Prédictive  
### 🎯 Objectif  
Anticiper l’activité mensuelle des clients afin d’identifier ceux présentant un **risque d’inactivité**.  

### ⚙️ Méthodologie  
1. **Source de données** : `DWH_fact_transactions`, `DWH_dim_client`, `DWH_CALENDRIER`.  
2. **Agrégation** :  
   - Construction d’un jeu de données *Client × Mois* avec :  
     - `Tx_Month_Count` → nombre de transactions mensuelles.  
     - `Lag1` → activité du mois précédent.  
     - `RollMean3` → moyenne mobile sur trois mois.  
   - Cible (`Target`) : nombre de transactions du mois suivant.  
3. **Modèle** :  
   - Algorithme utilisé → **RandomForestRegressor**.  
   - Séparation temporelle : les deux derniers mois servent de test.  
   - Indicateurs de performance : **MAE** (erreur moyenne absolue) et **R²** (qualité de la prédiction).  
4. **Risque d’inactivité** :  
   - Seuil : ≤ 1 transaction prédite → *Risque Élevé*, sinon *Normal*.  
   - Export des résultats dans `predictions_clients.csv`.  

### 📊 Visualisations Power BI  
- **KPI Cards** : MAE, R², % de clients à risque.  
- **Courbe** : évolution mensuelle des transactions prédites.  
- **Barres** : répartition des clients par risque d’inactivité.  
- **Tableau** : liste des clients à risque (filtrable par segment, ville, agence).  

### 💡 Interprétation  
Le modèle met en évidence une majorité de clients à risque, révélant une tendance de baisse d’activité. Ces résultats servent de base pour cibler des actions de **relance commerciale** ou de **fidélisation proactive**.  

---

## 👥 2. Segmentation Dynamique des Clients  
### 🎯 Objectif  
Identifier des groupes de clients homogènes selon leur comportement transactionnel pour orienter la stratégie marketing.  

### ⚙️ Méthodologie  
1. **Source de données** : `DWH_fact_transactions`, `DWH_dim_client`, `DWH_CALENDRIER`.  
2. **Calculs RFM (Recence – Fréquence – Montant)** :  
   - `Recence` = jours depuis la dernière transaction.  
   - `Frequence` = nombre total de transactions.  
   - `Ticket` = montant moyen des transactions.  
3. **Clustering** :  
   - Algorithme → **K-Means** appliqué aux variables RFM.  
   - Seuils automatiques (quartiles 25e / 75e).  
   - Segments identifiés :  
     - *Premium (valeur & fréquence élevées)*  
     - *Régulier*  
     - *Ticket moyen élevé*  
     - *Inactif / À réactiver*  
4. **Exports** : `clients_clusters.csv` + `segmentation_overview.csv`.  

### 📊 Visualisations Power BI  
- **Barres** : nombre de clients par segment.  
- **Scatter (PCA 2D ou RFM)** : répartition visuelle des clusters.  
- **Slicers** : ville, segment client, agence.  
- **Cartes KPI** : part des Premium et des Inactifs.  

### 💡 Interprétation  
La segmentation révèle quatre profils types de clients, distinguant les plus rentables (*Premium*) des moins actifs (*Inactifs*). Cette classification permet de personnaliser les campagnes marketing : **fidéliser les Premium**, **réactiver les Inactifs**, et **optimiser les offres** selon la valeur et la fréquence d’utilisation.  

---

## 🧾 Structure du projet
```
📂 Projet_Bankia/
├── bankia_predict.py               # Script prédiction
├── bankia_segmentation.py          # Script segmentation
├── predictions_clients.csv         # Résultats modèle prédictif
├── clients_clusters.csv            # Segmentation clients
├── segmentation_overview.csv       # Statistiques segments
├── prediction_reel_vs_predit.png   # Visualisation prédiction
├── clusters_pca.png                # Visualisation segmentation
└── PowerBI_Report.pbix             # Rapport final Power BI (2 pages)
```

---

## 🧩 Pages Power BI
| Page | Titre | Contenu principal |
|------|--------|-------------------|
| **1** | 🔮 *Prédiction de l’activité client* | KPI MAE / R² / % Risque, courbe d’évolution, répartition par risque, tableau clients. |
| **2** | 👥 *Segmentation dynamique des clients* | Barres par segment, scatter PCA 2D, filtres dynamiques, cartes KPI par segment. |

---

## 🚀 Résumé global
Ce projet combine **machine learning** (Random Forest + K-Means) et **visualisation décisionnelle** dans Power BI pour offrir à Bankia une vision claire du **comportement client** et de son **évolution potentielle**.  
Les deux approches — prédiction et segmentation — permettent de **prévoir**, **comprendre** et **agir** sur la base de la donnée.  
