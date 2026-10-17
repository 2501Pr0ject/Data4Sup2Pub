"""Chargement et préparation du fichier marketing_campaign.csv.

Module unique partagé par tous les notebooks du cours (décisions D1, D4, D5, D6,
D9 et D10 du registre docs/decisions.md). Il est chargé en première cellule de
chaque notebook. Il ne contient aucune donnée : il sait où aller la chercher
(URL publique Kaggle) et comment la préparer, règle par règle, en annonçant
chaque fois le nombre de lignes concernées.

Usage dans un notebook :

    import preparation as prep
    brut = prep.charger()            # fichier brut, jamais modifié
    df = prep.preparer(brut)         # version préparée, recalculée à l'identique
    train, test = prep.separer_train_test(df)
"""
from __future__ import annotations

import io
import os
import urllib.request
import zipfile

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- constantes
PROPRIETAIRE_GITHUB = "2501Pr0ject"
DEPOT_PUBLIC = "Data4Sup2Pub"
BRANCHE = "main"
URL_DEPOT = f"https://raw.githubusercontent.com/{PROPRIETAIRE_GITHUB}/{DEPOT_PUBLIC}/{BRANCHE}"
URL_DONNEES = f"{URL_DEPOT}/data/marketing_campaign.csv"      # D1 : fichier brut hébergé dans le dépôt public
URL_MODULE = f"{URL_DEPOT}/notebooks/preparation.py"
URL_KAGGLE = "https://www.kaggle.com/api/v1/datasets/download/imakash3011/customer-personality-analysis"  # repli
NOM_FICHIER = "marketing_campaign.csv"
SEPARATEUR = "\t"
FORMAT_DATE = "%d-%m-%Y"

DATE_REFERENCE = pd.Timestamp("2014-06-29")   # D6 : dernière inscription observée (hypothèse)
ANNEE_REFERENCE = 2014

COUT_CONTACT = 3        # Z_CostContact, constante du fichier (coût d'un contact)
REVENU_REPONDANT = 11   # Z_Revenue, constante du fichier (revenu d'un client qui accepte)
POINT_MORT = COUT_CONTACT / REVENU_REPONDANT   # utilisé au notebook 03

GRAINE = 42
PART_TEST = 0.30
PROFONDEUR_DEFAUT = 3   # profondeur par défaut de l'arbre du cours (notebooks 02 et 03)

# Encodage ordinal d'Education : HYPOTHÈSE (D4). « 2n Cycle » est lu comme le
# second cycle au sens de Bologne, donc au niveau Master. Basic < Graduation
# (licence, 1er cycle) < 2n Cycle = Master (2e cycle) < PhD (3e cycle).
EDUCATION_ORD = {"Basic": 0, "Graduation": 1, "2n Cycle": 2, "Master": 2, "PhD": 3}

CIBLE = "Response"

# Familles de variables (D3). Les noms d'origine restent en anglais, les dérivées en français (D10).
VARIABLES_PROFIL = ["Age", "Education_ord", "En_couple", "Income", "Enfants", "Anciennete_mois"]
VARIABLES_CAMPAGNES = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5",
                       "Campagnes_acceptees"]
VARIABLES_COMPORTEMENT = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts",
                          "MntGoldProds", "Depenses_total", "NumWebPurchases", "NumCatalogPurchases",
                          "NumStorePurchases", "Achats_total", "Part_web", "NumDealsPurchases",
                          "NumWebVisitsMonth"]
VARIABLES_RECENCE = ["Recency"]

JEU_SUR = VARIABLES_PROFIL + VARIABLES_CAMPAGNES                       # profil + campagnes passées
JEU_COMPLET = JEU_SUR + VARIABLES_COMPORTEMENT + VARIABLES_RECENCE     # toutes les variables explicatives

COLONNES_MNT = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
COLONNES_CMP = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]


# --------------------------------------------------------------------------- chargement
def charger(chemin: str | None = None) -> pd.DataFrame:
    """Retourne le fichier brut, tel quel.

    1. `chemin` donné : lecture locale (scripts du dépôt source).
    2. Sinon : URL raw du dépôt public GitHub (D1, choix principal).
    3. Sinon : téléchargement anonyme depuis l'URL publique Kaggle (repli documenté).
    4. Sinon, dans Colab : dépôt manuel du fichier par l'étudiant.
    """
    if chemin is not None:
        return pd.read_csv(chemin, sep=SEPARATEUR)
    try:
        df = pd.read_csv(URL_DONNEES, sep=SEPARATEUR)
        print(f"Fichier chargé depuis le dépôt du cours : {df.shape[0]} lignes × {df.shape[1]} colonnes")
        return df
    except Exception as e:
        print(f"Dépôt du cours injoignable ({type(e).__name__}), essai de la source Kaggle…")
    try:
        req = urllib.request.Request(URL_KAGGLE, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            archive = zipfile.ZipFile(io.BytesIO(r.read()))
        with archive.open(NOM_FICHIER) as f:
            df = pd.read_csv(f, sep=SEPARATEUR)
        print(f"Fichier chargé depuis Kaggle : {df.shape[0]} lignes × {df.shape[1]} colonnes")
        return df
    except Exception as e:  # réseau, format, quota…
        print(f"Téléchargement Kaggle impossible ({type(e).__name__}). Déposez le fichier {NOM_FICHIER}.")
        try:
            from google.colab import files  # type: ignore
        except ImportError:
            raise RuntimeError(f"Placez {NOM_FICHIER} localement et appelez charger(chemin=...)") from e
        envoi = files.upload()
        nom = next(iter(envoi))
        df = pd.read_csv(io.BytesIO(envoi[nom]), sep=SEPARATEUR)
        print(f"Fichier chargé depuis votre poste : {df.shape[0]} lignes × {df.shape[1]} colonnes")
        return df


# --------------------------------------------------------------------------- préparation
def preparer(brut: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Applique les règles validées (D4, D5) et crée les variables dérivées.

    Le DataFrame reçu n'est jamais modifié : on travaille sur une copie.
    Chaque règle annonce le nombre de lignes ou colonnes qu'elle touche.
    Le journal des règles est conservé dans `df.attrs["journal"]`.
    """
    df = brut.copy()
    journal: list[tuple[str, int]] = []

    def note(regle: str, n: int) -> None:
        journal.append((regle, n))
        if verbose:
            print(f"  {regle:<70} {n:>5}")

    if verbose:
        print(f"Fichier brut : {len(df)} lignes")

    # D5 — doublons de profils (mêmes valeurs sur toutes les colonnes sauf ID)
    colonnes_profil = [c for c in df.columns if c != "ID"]
    masque = df.duplicated(subset=colonnes_profil, keep="first")
    note("D5  Doublons de profil retirés (ID différent, tout le reste identique)", int(masque.sum()))
    df = df[~masque]

    # R1 — colonnes constantes
    constantes = [c for c in ["Z_CostContact", "Z_Revenue"] if c in df.columns]
    note("R1  Colonnes constantes retirées (Z_CostContact, Z_Revenue)", len(constantes))
    df = df.drop(columns=constantes)

    # R2 — revenu manquant
    masque = df["Income"].isna()
    note("R2  Lignes sans Income retirées", int(masque.sum()))
    df = df[~masque]

    # R3 — revenu égal à 666 666
    masque = df["Income"] == 666666
    note("R3  Ligne Income = 666 666 retirée", int(masque.sum()))
    df = df[~masque]

    # R4 — année de naissance antérieure à 1930
    masque = df["Year_Birth"] < 1930
    note("R4  Lignes Year_Birth < 1930 retirées", int(masque.sum()))
    df = df[~masque]

    # R5 — Marital_Status : deux modalités retirées, une recodée
    masque = df["Marital_Status"].isin(["Absurd", "YOLO"])
    note("R5a Lignes Marital_Status Absurd/YOLO retirées", int(masque.sum()))
    df = df[~masque]
    masque = df["Marital_Status"] == "Alone"
    note("R5b Marital_Status Alone recodé en Single", int(masque.sum()))
    df.loc[masque, "Marital_Status"] = "Single"

    df = df.copy()  # évite les avertissements de vue

    # R6 — dates et âge
    df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"], format=FORMAT_DATE)
    df["Age"] = ANNEE_REFERENCE - df["Year_Birth"]
    df["Anciennete_mois"] = ((DATE_REFERENCE.year - df["Dt_Customer"].dt.year) * 12
                             + (DATE_REFERENCE.month - df["Dt_Customer"].dt.month))
    note("R6  Dt_Customer converti en date ; Age et Anciennete_mois créés", 2)

    # R7 — variables de synthèse
    df["Enfants"] = df["Kidhome"] + df["Teenhome"]
    df["En_couple"] = df["Marital_Status"].isin(["Married", "Together"]).astype(int)
    df["Depenses_total"] = df[COLONNES_MNT].sum(axis=1)
    df["Achats_total"] = df["NumWebPurchases"] + df["NumCatalogPurchases"] + df["NumStorePurchases"]
    df["Part_web"] = np.where(df["Achats_total"] > 0,
                              df["NumWebPurchases"] / df["Achats_total"].replace(0, np.nan), 0.0)
    df["Campagnes_acceptees"] = df[COLONNES_CMP].sum(axis=1)
    df["Education_ord"] = df["Education"].map(EDUCATION_ORD)
    assert df["Education_ord"].notna().all(), "Modalité d'Education inconnue"
    note("R7  Enfants, En_couple, Depenses_total, Achats_total, Part_web, Campagnes_acceptees, Education_ord créés", 7)
    note("     dont Part_web fixé à 0 faute d'achat (Achats_total = 0)", int((df["Achats_total"] == 0).sum()))

    df = df.reset_index(drop=True)
    df.attrs["journal"] = journal
    if verbose:
        print(f"Fichier préparé : {len(df)} lignes × {df.shape[1]} colonnes")
    return df


# --------------------------------------------------------------------------- séparation
def separer_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare 70 / 30, stratifié sur la cible, graine fixe (D9).

    Toujours la même séparation, quel que soit le jeu de variables utilisé
    ensuite : les comparaisons de modèles portent sur les mêmes clients.
    """
    from sklearn.model_selection import train_test_split

    train, test = train_test_split(df, test_size=PART_TEST, random_state=GRAINE, stratify=df[CIBLE])
    return train, test


# --------------------------------------------------------------------------- modèle
def entrainer_arbre(X: pd.DataFrame, y: pd.Series, profondeur: int | None = PROFONDEUR_DEFAUT):
    """Entraîne l'arbre de décision du cours (D9) : même graine, même profondeur par défaut.

    Appelée par les notebooks 02 et 03 pour garantir qu'ils travaillent sur le même arbre
    et les mêmes prédictions. `profondeur=None` : aucune limite.
    """
    from sklearn.tree import DecisionTreeClassifier

    return DecisionTreeClassifier(max_depth=profondeur, random_state=GRAINE).fit(X, y)


def resume_journal(df: pd.DataFrame) -> pd.DataFrame:
    """Le journal des règles sous forme de table (pour affichage dans un notebook)."""
    return pd.DataFrame(df.attrs.get("journal", []), columns=["règle", "lignes ou colonnes touchées"])
