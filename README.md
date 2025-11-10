# 📘 Projet Bankia 2025 – Système Décisionnel Power BI  
## README – Data Engineering & Data Analysis  

---

## 🏦 Contexte du projet
La banque fictive **Bankia** souhaite mettre en place un **système d’information décisionnel (SID)** pour centraliser, historiser et analyser ses données commerciales et financières.  
Le projet combine deux compétences : **Data Engineering** (construction du pipeline et entrepôt de données) et **Data Analysis** (visualisation Power BI et insights décisionnels).  

Les données proviennent de 5 sources principales :
- `clients.xls` → informations clients  
- `agences.txt` → réseau d’agences  
- `produits_bancaires.csv` → produits et services bancaires  
- `transactions.csv` → opérations clients  
- `depenses.csv` → dépenses de fonctionnement des agences  

---

## ⚙️ Phase 1 – Data Engineering

### 🎯 Objectif
Concevoir et automatiser une **architecture data complète** (Data Lake → ODS → Data Warehouse) afin de fiabiliser et centraliser les données de Bankia.

### 🧩 Étapes principales
1. **Stockage des données brutes** dans un **Data Lake Azure**.  
2. **Création d’un ODS (Operational Data Store)** pour nettoyer, uniformiser et historiser les données.  
3. **Alimentation du Data Warehouse (DWH)** à partir de l’ODS avec un modèle en étoile :  
   - **Faits** : transactions, dépenses  
   - **Dimensions** : clients, produits, agences, calendrier  
4. **Pipelines Azure Data Factory (ADF)** :  
   - `Master_Pipeline_ODS` → chargement ODS  
   - `Master_Pipeline_DWH` → chargement DWH  
   - `Master_Pipeline` → orchestration complète  

### 💾 Livrables
- Base de données Azure SQL (DWH) avec accès fourni.  
- Pipelines ADF fonctionnels et documentés.  
- Architecture cloud opérationnelle et reproductible.  

---

## 📊 Phase 2 – Data Analysis (Power BI)

### 🎯 Objectif
Créer un **rapport Power BI** interactif offrant une vision complète de la **performance commerciale et financière** de Bankia.  

### 🔹 1. Analyse des Transactions et Produits
- Volume et valeur des transactions par type (Retrait, Dépôt, Virement, Paiement CB).  
- Produits les plus utilisés et clients les plus rentables.  
- Évolution mensuelle et annuelle de l’activité.  

### 🔹 2. Analyse Financière et Rentabilité
- Comparaison **revenus produits bancaires vs dépenses agences**.  
- Calcul de la **marge nette** et du **bénéfice global**.  
- Classement des agences les plus performantes.  

### 🧮 Indicateurs DAX
- `Total_Transactions`, `Montant_Total`, `Marge_Nette`, `Revenu_Produit`, `Top_Client`, `Bénéfice_Global`.  
- Filtres dynamiques : période, agence, produit, segment client.

### 💡 Visualisations Power BI
- KPI Cards (revenus, marges, top clients)  
- Graphiques temporels (tendances mensuelles)  
- Tableaux de performance agence / produit  
- Cartes géographiques interactives (par ville ou pays)  

---

## 🚀 Bonus – Analyse Prédictive & Segmentation Dynamique

### 🔮 Analyse Prédictive
- Modèle **Random Forest Regressor** entraîné sur les transactions mensuelles.  
- Variables clés : `Lag1`, `RollMean3`, `Target`.  
- Évaluation : MAE = 0.17, R² = 0.63.  
- Identification de 64,7 % de clients à risque d’inactivité.  
- Visualisations : KPI (% risque), courbe prédictions, répartition par ville.

### 👥 Segmentation Dynamique
- Approche **RFM (Récence, Fréquence, Montant)** + **K-Means clustering**.  
- 4 profils détectés :  
  1. *Premium (valeur & fréquence élevées)*  
  2. *Régulier*  
  3. *Ticket moyen élevé*  
  4. *Inactif / À réactiver*  
- Visualisations : barres par segment, scatter PCA 2D, KPI par segment.  

---

## 🧠 Synthèse
Le projet **Bankia 2025** illustre l’intégration complète d’une solution **DataOps + BI** :  
- **Phase 1** : Architecture Azure industrialisée (Data Lake → ODS → DWH).  
- **Phase 2** : Tableau de bord Power BI stratégique (performance, rentabilité, fidélisation).  
- **Bonus** : Intelligence prédictive et segmentation comportementale des clients.  

💡 L’ensemble permet à la direction de Bankia de **suivre sa performance en temps réel**, **anticiper les tendances**, et **optimiser la stratégie commerciale et financière**.

---

## Equipe
Waï Lekone
Patricia Koto
Bintou Diop
Jiwon YI
Cheikh Ismaël COULIBALY
