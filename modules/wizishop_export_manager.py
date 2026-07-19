import csv

from modules.product_manager import ProductManager
from modules.reference_manager import ReferenceManager
from modules.canal_manager import CanalManager
from modules.moteur_prix import MoteurPrix
from modules.generateur_fiche_html import GenerateurFicheHtml


class WizishopExportManager:
    """
    Génère un fichier CSV conforme à la nomenclature du
    catalogue produits WiziShop, à partir d'une sélection de
    produits du logiciel — séparateur point-virgule, encodage
    UTF-8 (les emojis des fiches HTML ne passeraient pas en
    ISO-8859-1, WiziShop accepte les deux encodages).

    Ne touche jamais tout le catalogue : uniquement les
    identifiants de produits explicitement passés en
    paramètre (ceux sélectionnés dans la liste au moment du
    clic sur Export).
    """

    # Nom du canal représentant le site WiziShop dans les
    # réglages du logiciel (Paramètres > Canaux) — confirmé
    # avec l'utilisateur, pas une convention WiziShop.
    NOM_CANAL_SITE = "Site"

    # WiziShop limite chaque fichier CSV à 500 lignes.
    LIMITE_LIGNES = 500

    # Correspondance entre le statut de stock interne et
    # l'état attendu par WiziShop.
    ETATS = {
        "actif": "Affiché",
        "rupture": "Indisponible",
        "fin_de_vie": "Non affiché",
    }

    # Colonnes facultatives : clé interne (cochée dans la
    # fenêtre de sélection) → en-tête exact attendu par
    # WiziShop.
    COLONNES_FACULTATIVES_ENTETES = {
        "reference_fournisseur": "Référence fournisseur",
        "nom_fournisseur": "Nom du fournisseur",
        "ean13": "EAN 13",
        "isbn": "ISBN",
        "mots_cles": "Mots clés",
        "caracteristiques": "Caractéristiques",
        "titre_page": "Titre de la page",
        "url": "URL",
        "meta_description": "Méta description",
        "photo_2": "Photo 2",
        "photo_3": "Photo 3",
        "date_debut": "Date de début",
        "date_fin": "Date de fin",
        "produit_en_selection": "Produit dans la sélection",
    }

    ENTETES_OBLIGATOIRES = [
        "ID Produit",
        "Référence produit",
        "Nom du produit",
        "Description courte",
        "Description longue",
        "Poids",
        "Nombre de produits en stock",
        "Photo 1",
        "État",
        "ID Marque",
        "Nom Marque",
        "ID Catégorie principale parente",
        "Catégorie principale parente",
        "ID Sous-catégorie principale",
        "Sous-catégorie principale",
        "Prix TTC",
    ]

    def __init__(self):

        self.produits = ProductManager()
        self.references = ReferenceManager()
        self.canaux = CanalManager()
        self.moteur_prix = MoteurPrix()

    def _canal_site_id(self):
        """
        Retrouve l'id du canal WiziShop par son NOM plutôt que
        par un identifiant numérique fixe — les canaux sont
        librement configurables dans le logiciel, un id en dur
        casserait dès que l'ordre de création changerait.
        """

        for canal in self.canaux.tous():

            if canal["nom"] == self.NOM_CANAL_SITE:
                return canal["id"]

        return None

    def exporter(
        self,
        identifiants_produits,
        colonnes_facultatives,
        chemin_fichier,
    ):
        """
        Génère le fichier CSV pour les produits donnés, puis
        les marque comme exportés. Renvoie un dictionnaire
        avec le nombre de lignes écrites et, le cas échéant,
        les produits pour lesquels aucun gabarit de fiche
        actif n'a été trouvé (description longue de secours
        utilisée à la place du HTML généré).
        """

        if len(identifiants_produits) > self.LIMITE_LIGNES:

            raise ValueError(
                f"WiziShop limite chaque fichier CSV à "
                f"{self.LIMITE_LIGNES} lignes. Tu as sélectionné "
                f"{len(identifiants_produits)} produits — "
                f"exporte-les en plusieurs fois (par lots de "
                f"{self.LIMITE_LIGNES} maximum)."
            )

        canal_id = self._canal_site_id()

        if canal_id is None:

            raise ValueError(
                f"Le canal '{self.NOM_CANAL_SITE}' est introuvable "
                f"dans Paramètres > Canaux — vérifie qu'il existe "
                f"bien sous ce nom exact."
            )

        entetes_facultatives = [
            self.COLONNES_FACULTATIVES_ENTETES[cle]
            for cle in colonnes_facultatives
            if cle in self.COLONNES_FACULTATIVES_ENTETES
        ]

        entetes = self.ENTETES_OBLIGATOIRES + entetes_facultatives

        lignes = []
        produits_sans_gabarit = []

        for produit_id in identifiants_produits:

            produit = self.produits.obtenir(produit_id)

            if produit is None:
                continue

            ligne, a_un_gabarit = self._construire_ligne(
                produit, canal_id, colonnes_facultatives
            )

            lignes.append(ligne)

            if not a_un_gabarit:
                produits_sans_gabarit.append(produit["nom"] or f"#{produit_id}")

        with open(chemin_fichier, "w", newline="", encoding="utf-8") as f:

            redacteur = csv.writer(f, delimiter=";")
            redacteur.writerow(entetes)

            for ligne in lignes:
                redacteur.writerow([ligne.get(entete, "") for entete in entetes])

        self.produits.marquer_produits_exportes(identifiants_produits)

        return {
            "nombre_lignes": len(lignes),
            "produits_sans_gabarit": produits_sans_gabarit,
        }

    def _construire_ligne(self, produit, canal_id, colonnes_facultatives):

        ####################################################
        # Licence (pour la génération HTML uniquement, pas
        # une colonne du CSV en elle-même)
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
        marque_id_wizishop = ""

        if produit["marque_id"]:

            marque = self.references.obtenir(
                "marques", produit["marque_id"]
            )

            if marque:
                marque_nom = marque["nom"] or ""
                marque_id_wizishop = marque["id_wizishop"] or ""

        ####################################################
        # Catégorie principale + sous-catégorie
        ####################################################

        categorie_principale_nom = ""
        categorie_principale_id_wizishop = ""
        sous_categorie_nom = ""
        sous_categorie_id_wizishop = ""

        if produit["categorie_site_id"]:

            sous_categorie = self.references.obtenir(
                "categories_site", produit["categorie_site_id"]
            )

            if sous_categorie:

                sous_categorie_nom = sous_categorie["nom"] or ""
                sous_categorie_id_wizishop = (
                    sous_categorie["id_wizishop"] or ""
                )

                if sous_categorie["categorie_parente_id"]:

                    categorie_principale = self.references.obtenir(
                        "categories_site",
                        sous_categorie["categorie_parente_id"]
                    )

                    if categorie_principale:

                        categorie_principale_nom = (
                            categorie_principale["nom"] or ""
                        )
                        categorie_principale_id_wizishop = (
                            categorie_principale["id_wizishop"] or ""
                        )

        ####################################################
        # Prix TTC — calculé à la volée par le moteur de prix
        # sur le canal Site+Drop, jamais stocké tel quel.
        ####################################################

        resultat_prix = self.moteur_prix.calculer(produit, canal_id, None)

        prix_ttc = ""

        if not resultat_prix.get("erreur"):
            prix_ttc = f"{resultat_prix['prix_vente_ttc']:.2f}"

        ####################################################
        # Description longue — le HTML complet généré par le
        # moteur de templates (bannières, FAQ, image de fond
        # incluse), pas un texte brut séparé.
        ####################################################

        description_longue = GenerateurFicheHtml.generer(
            produit, licence_nom
        )

        a_un_gabarit = description_longue is not None

        if not a_un_gabarit:
            description_longue = produit["description_longue"] or ""

        ####################################################
        # État
        ####################################################

        etat = self.ETATS.get(
            produit["statut_stock"] or "actif", "Affiché"
        )

        ####################################################
        # ID Produit — réutilise l'ID déjà attribué par
        # WiziShop si ce produit a déjà été importé/exporté
        # une fois (id_wizishop renseigné) ; sinon laissé
        # VIDE (décision actée : pari que WiziShop attribue un
        # nouvel ID à l'import plutôt que de rejeter la ligne).
        ####################################################

        id_produit = ""

        if produit["id_wizishop"]:

            id_produit = produit["id_wizishop"]

            if not id_produit.startswith("#"):
                id_produit = f"#{id_produit}"

        id_marque_formate = (
            f"#{marque_id_wizishop}" if marque_id_wizishop else ""
        )
        id_categorie_principale_formate = (
            f"#{categorie_principale_id_wizishop}"
            if categorie_principale_id_wizishop else ""
        )
        id_sous_categorie_formate = (
            f"#{sous_categorie_id_wizishop}"
            if sous_categorie_id_wizishop else ""
        )

        ligne = {
            "ID Produit": id_produit,
            "Référence produit": produit["sku"] or "",
            "Nom du produit": produit["nom"] or "",
            "Description courte": produit["description_courte"] or "",
            "Description longue": description_longue,
            "Poids": produit["poids"] or "",
            "Nombre de produits en stock": (
                1 if produit["type_produit"] == "precommande"
                else (produit["quantite_stock"] or 0)
            ),
            "Photo 1": produit["image_principale"] or "",
            "État": etat,
            "ID Marque": id_marque_formate,
            "Nom Marque": marque_nom,
            "ID Catégorie principale parente": (
                id_categorie_principale_formate
            ),
            "Catégorie principale parente": categorie_principale_nom,
            "ID Sous-catégorie principale": id_sous_categorie_formate,
            "Sous-catégorie principale": sous_categorie_nom,
            "Prix TTC": prix_ttc,
        }

        ####################################################
        # Colonnes facultatives cochées dans la fenêtre
        ####################################################

        if "reference_fournisseur" in colonnes_facultatives:
            ligne["Référence fournisseur"] = (
                produit["reference_fournisseur"] or ""
            )

        if "nom_fournisseur" in colonnes_facultatives:

            nom_fournisseur = ""

            if produit["fournisseur_id"]:

                fournisseur = self.references.obtenir(
                    "fournisseurs", produit["fournisseur_id"]
                )
                nom_fournisseur = (
                    fournisseur["nom"] if fournisseur else ""
                )

            ligne["Nom du fournisseur"] = nom_fournisseur

        if "ean13" in colonnes_facultatives:
            ligne["EAN 13"] = produit["ean"] or ""

        if "isbn" in colonnes_facultatives:
            # Pas de champ ISBN sur le produit (PopLicence ne
            # vend pas de livres) — colonne laissée vide si
            # cochée, sans erreur.
            ligne["ISBN"] = ""

        if "mots_cles" in colonnes_facultatives:
            ligne["Mots clés"] = produit["mots_cles"] or ""

        if "caracteristiques" in colonnes_facultatives:
            # Pas de champ dédié "caractéristiques en liste"
            # sur le produit actuellement — laissé vide,
            # remplissable manuellement sur WiziShop si besoin.
            ligne["Caractéristiques"] = ""

        if "titre_page" in colonnes_facultatives:
            ligne["Titre de la page"] = (produit["titre_seo"] or "")[:65]

        if "url" in colonnes_facultatives:
            ligne["URL"] = produit["url_slug"] or ""

        if "meta_description" in colonnes_facultatives:
            ligne["Méta description"] = produit["meta_description"] or ""

        if "photo_2" in colonnes_facultatives:
            ligne["Photo 2"] = produit["image_2"] or ""

        if "photo_3" in colonnes_facultatives:
            ligne["Photo 3"] = produit["image_3"] or ""

        if "date_debut" in colonnes_facultatives:
            ligne["Date de début"] = ""

        if "date_fin" in colonnes_facultatives:
            ligne["Date de fin"] = ""

        if "produit_en_selection" in colonnes_facultatives:
            ligne["Produit dans la sélection"] = ""

        return ligne, a_un_gabarit