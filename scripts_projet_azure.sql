
-- ######## CREATEION DES TABLES ODS #########--
CREATE TABLE ODS.client(
	ID_Client INT NOT NULL,
	Nom_Client varchar(50) NOT NULL,
    Prenom_Client varchar(50) NOT NULL,
    Email varchar(100) NOT NULL,
    Telephone varchar(20) NOT NULL,
    Ville varchar(100) NOT NULL,
    Pays varchar(20) NOT NULL,
    Segment_Client varchar(20) NOT NULL

);

CREATE TABLE ODS.agence(
	ID_Agence int NOT NULL,
	Nom_Agence varchar(50) NOT NULL,
	Ville varchar(20) NOT NULL,
	Pays varchar(20) NOT NULL
);

CREATE TABLE ODS.produit(
	ID_Produit int NOT NULL,
	Nom_Produit varchar(50) NOT NULL,
	Categorie varchar(20) NOT NULL,
	Taux_Interet float NULL,
    Frais_Gestion float NULL

);

CREATE TABLE ODS.transactions(
	ID_Transaction int NOT NULL,
    Date_Transaction date NOT NULL,
    ID_Client int NOT NULL,
    ID_Produit int NOT NULL,
    Type_Transaction varchar(50) NOT NULL,
    Montant float NOT NULL,
    ID_Agence int

);

CREATE TABLE ODS.depenses(
	ID_Depense int NOT NULL,
    Date_Depense date NOT NULL,
    Categorie_Depense varchar(50) NOT NULL,
    Montant float NOT NULL,
    ID_Agence int NOT NULL
);


-- ######## VERIFICATION DU CHARGEMENT DES DONNEES DANS TABLES ODS #########--

SELECT * FROM ODS.client;
SELECT * FROM ODS.agence;
SELECT * FROM ODS.produit;
SELECT * FROM ODS.transactions;
SELECT * FROM ODS.depenses

-- ######## CREATEION DES TABLES DWH #########--

CREATE TABLE DWH.dim_type_transaction(
    Type_Transaction_rowid int identity(1,1) NOT NULL,
    Type_Transaction varchar(50) NOT NULL
);

CREATE TABLE DWH.dim_produit(
    Produit_rowid int identity(1,1) NOT NULL,
	ID_Produit int NOT NULL,
	Nom_Produit varchar(50) NOT NULL,
	Categorie varchar(20) NOT NULL,
	Taux_Interet float NULL,
    Frais_Gestion float NULL

);

CREATE TABLE DWH.dim_client(
    Client_rowid int identity(1,1) NOT NULL,
	ID_Client INT NOT NULL,
	Nom_Client varchar(50) NOT NULL,
    Prenom_Client varchar(50) NOT NULL,
    Email varchar(100) NOT NULL,
    Telephone varchar(20) NOT NULL,
    Ville varchar(100) NOT NULL,
    Pays varchar(20) NOT NULL,
    Segment_Client varchar(20) NOT NULL

);

CREATE TABLE DWH.dim_agence(
    Agence_rowid int identity(1,1) NOT NULL,
	ID_Agence int NOT NULL,
	Nom_Agence varchar(50) NOT NULL,
	Ville varchar(20) NOT NULL,
	Pays varchar(20) NOT NULL
);

CREATE TABLE DWH.dim_categorie_depense(
    Categorie_Depense_rowid int identity(1,1) NOT NULL,
    Categorie_Depense varchar(50) NOT NULL
);

-- ######## CREATEION DES TABLES DE FAITS DU DWH #########--
CREATE TABLE DWH.fact_transactions(
	ID_Transaction int NOT NULL,
    idDate int,
    Client_rowid int NOT NULL,
    Type_Transaction_rowid int NOT NULL,
    Agence_rowid int NOT NULL,
    Produit_rowid int NOT NULL,
    Montant float NOT NULL

);

CREATE TABLE DWH.fact_depenses(
	ID_Depense int NOT NULL,
    idDate int,
    Agence_rowid int NOT NULL,
    Categorie_Depense_rowid int,
    Montant float NOT NULL
    
);

-- ######## VERIFICATION DU CHARGEMENT DES DONNEES DANS TABLES DWH #########--
SELECT * FROM DWH.dim_client;
SELECT * FROM DWH.dim_produit;

-- ###### CREATION DE LA TABLE CALENDRIER ######## --

CREATE TABLE DWH.CALENDRIER (
    ID_Date INT PRIMARY KEY,
    Date_calendrier DATE,
    Year INT,
    Month INT,
    Day INT,
    Week INT,
    Quarter INT,
    DayOfWeek INT,
    DayName NVARCHAR(10),
    MonthName NVARCHAR(10),
    IsWeekend BIT,
    IsHoliday BIT
);


DECLARE @StartDate DATE = '2023-01-01';
DECLARE @EndDate DATE = '2027-12-31';

WITH Dates AS (
    SELECT @StartDate AS Date
    UNION ALL
    SELECT DATEADD(DAY, 1, Date)
    FROM Dates
    WHERE DATEADD(DAY, 1, Date) <= @EndDate
)
INSERT INTO DWH.CALENDRIER (ID_Date, Date_calendrier, Year, Month, Day, Week, Quarter, DayOfWeek, DayName, MonthName, IsWeekend, IsHoliday)
SELECT
    CONVERT(INT, FORMAT(Date, 'yyyyMMdd')) AS ID_Date,
    Date,
    YEAR(Date) AS Year,
    MONTH(Date) AS Month,
    DAY(Date) AS Day,
    DATEPART(WEEK, Date) AS Week,
    DATEPART(QUARTER, Date) AS Quarter,
    DATEPART(WEEKDAY, Date) AS DayOfWeek,
    DATENAME(WEEKDAY, Date) AS DayName,
    DATENAME(MONTH, Date) AS MonthName,
    CASE
        WHEN DATEPART(WEEKDAY, Date) IN (1, 7) THEN 1
        ELSE 0
    END AS IsWeekend,
    0 AS IsHoliday  -- Vous pouvez mettre à jour cette colonne manuellement pour les jours fériés
FROM Dates
OPTION (MAXRECURSION 0);