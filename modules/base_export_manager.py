import csv
import os

from modules.product_manager import ProductManager
from modules.reference_manager import ReferenceManager
from modules.canal_manager import CanalManager
from modules.categorie_manager import CategorieManager
from modules.moteur_prix import MoteurPrix
from modules.generateur_fiche_html import GenerateurFicheHtml


class BaseExportManager:
    """
    Génère un fichier CSV pour l'import produits vers
    Base.com (ex-BaseLinker), la plateforme centrale qui
    redistribue ensuite le catalogue vers les marketplaces
    connectées (Amazon, eBay, Fnac, Cdiscount, Rakuten,
    Leclerc...).

    Contrairement à WiziShop, Base.com accepte n'importe
    quelle structure de colonnes CSV — l'association
    colonne ↔ champ Base.com se fait une seule fois côté
    Base.com au premier import (mapping réutilisable
    ensuite), pas de nomenclature imposée ici.

    Une colonne de prix est générée automatiquement pour
    CHAQUE canal actif du logiciel, à l'exception du canal
    "Site" (réservé à l'export WiziShop dédié) — cela
    correspond aux "groupes de prix" de Base.com, un par
    marketplace, chacun ensuite assigné à la marketplace
    correspondante dans les réglages Base.com.

    Séparateur point-virgule, encodage UTF-8 (comme pour
    WiziShop).
    """

    # Nom du canal à exclure de cet export — il a son propre
    # export dédié (WizishopExportManager). Retrouvé par NOM,
    # pas par id, les canaux étant librement configurables.
    NOM_CANAL_EXCLU = "Site"

    # Base.com limite chaque fichier importé à 2 Mo — on
    # avertit plutôt que de bloquer, la limite dépendant
    # surtout du nombre de produits et de la longueur des
    # descriptions HTML.
    TAILLE_MAX_OCTETS = 2 * 1024 * 1024

    def __init__(self):

        self.produits = ProductManager()
        self.references = ReferenceManager()
        self.canaux = CanalManager()
        self.categories = CategorieManager()
        self.moteur_prix = MoteurPrix()

    def _canaux_a_exporter(self):
        """
        Tous les canaux actifs, sauf celui réservé à
        WiziShop.
        """

        return [
            canal for canal in self.canaux.tous()
            if canal["nom"] != self.NOM_CANAL_EXCLU
        ]

    def exporter(self, identifiants_produits, chemin_fichier):
        """
        Génère le fichier CSV pour les produits donnés.

        Renvoie un dictionnaire avec le nombre de lignes
        écrites, les produits sans gabarit de fiche actif
        (description de secours utilisée à la place), et un
        avertissement si le fichier dépasse la taille
        recommandée par Base.com.
        """

        canaux = self._canaux_a_exporter()

        entetes = [
            "SKU",
            "EAN",
            "EAN colis",
            "Nom du produit",
            "Description courte",
            "Description longue",
            "Marque",
            "Poids (kg)",
            "Longueur (cm)",
            "Largeur (cm)",
            "Hauteur (cm)",
            "Stock",
            "Photo 1",
            "Photo 2",
            "Photo 3",
        ]

        # Une colonne "Prix TTC" et une colonne "Catégorie"
        # par canal actif à exporter — l'ordre suit celui
        # des canaux dans Paramètres > Canaux (via ordre/nom).
        for canal in canaux:
            entetes.append(f"Prix TTC - {canal['nom']}")
            entetes.append(f"Catégorie - {canal['nom']}")

        lignes = []
        produits_sans_gabarit = []

        for produit_id in identifiants_produits:

            produit = self.produits.obtenir(produit_id)

            if produit is None:
                continue

            ligne, a_un_gabarit = self._construire_ligne(
                produit, canaux
            )

            lignes.append(ligne)

            if not a_un_gabarit:
                produits_sans_gabarit.append(
                    produit["nom"] or f"#{produit_id}"
                )

        with open(chemin_fichier, "w", newline="", encoding="utf-8") as f:

            redacteur = csv.writer(f, delimiter=";")
            redacteur.writerow(entetes)

            for ligne in lignes:
                redacteur.writerow(
                    [ligne.get(entete, "") for entete in entetes]
                )

        taille_fichier = os.path.getsize(chemin_fichier)
        fichier_trop_lourd = taille_fichier > self.TAILLE_MAX_OCTETS

        return {
            "nombre_lignes": len(lignes),
            "produits_sans_gabarit": produits_sans_gabarit,
            "taille_octets": taille_fichier,
            "fichier_trop_lourd": fichier_trop_lourd,
        }

    def _construire_ligne(self, produit, canaux):

        ####################################################
        # Licence (pour la génération HTML uniquement)
        ####################################################

        licence_nom = None

        if produit["licence_id"]:

            licence = self.references.obtenir(
                "licences", produit["licence_id"]
            )
            licence_nom = licence["nom"] if licence else None

        ####################################################
        # Marque
        ####################################################

        marque_nom = ""

        if produit["marque_id"]:

            marque = self.references.obtenir(
                "marques", produit["marque_id"]
            )

            if marque:
                marque_nom = marque["nom"] or ""

        ####################################################
        # Description longue — même HTML généré que pour
        # WiziShop, réutilisable tel quel.
        ####################################################

        description_longue = GenerateurFicheHtml.generer(
            produit, licence_nom
        )

        a_un_gabarit = description_longue is not None

        if not a_un_gabarit:
            description_longue = produit["description_longue"] or ""

        ligne = {
            "SKU": produit["sku"] or "",
            "EAN": produit["ean"] or "",
            "EAN colis": produit["ean_colis"] or "",
            "Nom du produit": produit["nom"] or "",
            "Description courte": produit["description_courte"] or "",
            "Description longue": description_longue,
            "Marque": marque_nom,
            "Poids (kg)": produit["poids"] or "",
            "Longueur (cm)": produit["longueur"] or "",
            "Largeur (cm)": produit["largeur"] or "",
            "Hauteur (cm)": produit["hauteur"] or "",
            "Stock": (
                1 if produit["type_produit"] == "precommande"
                else (produit["quantite_stock"] or 0)
            ),
            "Photo 1": produit["image_principale"] or "",
            "Photo 2": produit["image_2"] or "",
            "Photo 3": produit["image_3"] or "",
        }

        ####################################################
        # Prix + catégorie par canal — un "groupe de prix"
        # Base.com par marketplace, calculé à la volée par
        # le moteur de prix, jamais stocké tel quel.
        ####################################################

        categories_canaux = self.produits.categories_canaux(produit["id"])

        for canal in canaux:

            categorie_id = categories_canaux.get(canal["id"])

            resultat_prix = self.moteur_prix.calculer(
                produit, canal["id"], categorie_id
            )

            prix_ttc = ""

            if not resultat_prix.get("erreur"):
                prix_ttc = f"{resultat_prix['prix_vente_ttc']:.2f}"

            categorie_nom = ""

            if categorie_id:

                categorie = self.references.obtenir(
                    "categories", categorie_id
                )
                categorie_nom = categorie["nom"] if categorie else ""

            ligne[f"Prix TTC - {canal['nom']}"] = prix_ttc
            ligne[f"Catégorie - {canal['nom']}"] = categorie_nom

        return ligne, a_un_gabarit