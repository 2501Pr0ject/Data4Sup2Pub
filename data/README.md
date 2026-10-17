# Fichier `marketing_campaign.csv`

| | |
|---|---|
| **Contenu** | 2 240 lignes (une par client), 29 colonnes, séparateur tabulation, encodage ASCII |
| **Source** | Kaggle, *Customer Personality Analysis*, publié par Akash Patel (`imakash3011`), version 1 du 22 août 2021 — https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis |
| **Licence affichée** | **CC0 : Public Domain**, telle qu'indiquée sur la page Kaggle, vérifiée le **17 octobre 2026** |
| **Origine** | La page Kaggle attribue les données à Dr Omar Romero-Hernandez. Le même fichier figure dans le cas de recrutement « iFood CRM Data Analyst Case » (dépôt GitHub `nailson/ifood-data-business-analyst-test`, 2020, sans licence), qui le présente comme un échantillon **simulé** d'informations clients et d'interactions de campagnes |
| **Nature des données** | **Données simulées.** Aucune ligne ne correspond à une personne réelle |
| **État** | Fichier **brut**, publié tel que téléchargé, sans aucun nettoyage. Empreinte SHA-256 : `cd0affa36b1b981e80ba0e27767e9b3ab723f7a3dba948f722af81abc6b990ea` |
| **Usage** | Pédagogique, non commercial, dans le cadre d'un cours d'introduction à la data science |

## Retrait sur demande

Ce fichier est republié ici sur la foi de la licence CC0 affichée par la page Kaggle. Si vous êtes titulaire de droits sur ces données et souhaitez leur retrait, ouvrez une *issue* sur ce dépôt : le fichier sera retiré sans délai et les notebooks basculeront sur un chargement direct depuis Kaggle.

## Description des colonnes

| Colonne | Description (d'après la page Kaggle) |
|---|---|
| `ID` | identifiant du client |
| `Year_Birth` | année de naissance |
| `Education` | niveau d'études |
| `Marital_Status` | situation familiale |
| `Income` | revenu annuel du foyer |
| `Kidhome`, `Teenhome` | nombre d'enfants, d'adolescents au foyer |
| `Dt_Customer` | date d'inscription (jour-mois-année) |
| `Recency` | jours depuis le dernier achat |
| `Complain` | 1 si réclamation dans les 2 dernières années |
| `MntWines`, `MntFruits`, `MntMeatProducts`, `MntFishProducts`, `MntSweetProducts`, `MntGoldProds` | montants dépensés par rayon sur les 2 dernières années |
| `NumDealsPurchases` | achats avec remise |
| `NumWebPurchases`, `NumCatalogPurchases`, `NumStorePurchases` | achats par canal : site, catalogue, magasin |
| `NumWebVisitsMonth` | visites du site le mois dernier |
| `AcceptedCmp1` … `AcceptedCmp5` | 1 si l'offre de la campagne n a été acceptée |
| `Response` | 1 si l'offre de la dernière campagne a été acceptée |
| `Z_CostContact`, `Z_Revenue` | constantes (coût d'un contact, revenu d'un client qui accepte) |
