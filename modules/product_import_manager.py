import csv

from database.database import Database
from modules.product_manager import ProductManager
from modules.numerotation_manager import NumerotationManager


class ProductImportManager:
    """
    Import de produits depuis un fichier CSV.

    Fonctionne en deux temps :

    1. analyser(chemin) : lit le fichier, controle tout,
       et renvoie un rapport SANS RIEN ECRIRE en base.

    2. importer(chemin) : refait la meme analyse puis
       cree reellement les produits valides.

    Le SKU n'est JAMAIS lu dans le fichier : il est genere
    par la numerotation du logiciel, exactement comme
    lorsqu'on cree une fiche a la main.
    """

    # Correspondance entre le type de produit du fichier
    # et le code de numerotation qui genere le SKU.
    CODES_NUMEROTATION = {
        "stock": "SKU_STOCK",
        "dropshipping": "SKU_DROP",
        "precommande": "SKU_PRECO",
        "bundle": "SKU_BUNDLE",
    }

    def __init__(self):

        self.db = Database()
        self.productManager = ProductManager()
        self.numerotation = NumerotationManager()

    # ------------------------------------------------------
    # Lecture du fichier
    # ------------------------------------------------------

    def lire_fichier(self, chemin):
        """
        Lit le CSV et renvoie la liste des lignes.

        encoding utf-8-sig : indispensable, Excel ajoute une
        marque invisible en debut de fichier qui collerait
        sinon au nom de la premiere colonne.
        """

        with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:

            lecteur = csv.DictReader(fichier, delimiter=";")

            lignes = []

            for numero, ligne in enumerate(lecteur, start=2):

                propre = {}

                for cle, valeur in ligne.items():

                    if cle is None:
                        continue

                    propre[cle.strip()] = (valeur or "").strip()

                propre["_ligne"] = numero

                lignes.append(propre)

        return lignes

    # ------------------------------------------------------
    # Resolution des libelles en identifiants
    # ------------------------------------------------------

    def trouver_id(self, table, nom):
        """
        Cherche un enregistrement par son nom, sans tenir
        compte de la casse ni des espaces.
        """

        if not nom:
            return None

        resultat = self.db.lire_un(
            f"SELECT id FROM {table} "
            f"WHERE TRIM(LOWER(nom)) = TRIM(LOWER(?))",
            (nom,)
        )

        return resultat["id"] if resultat else None

    def trouver_ou_creer_marque(self, nom):
        """
        Les marques portent les licences sur le site.
        Si la marque n'existe pas encore, on la cree.
        """

        if not nom:
            return None

        identifiant = self.trouver_id("marques", nom)

        if identifiant is not None:
            return identifiant

        curseur = self.db.executer(
            "INSERT INTO marques (nom, actif) VALUES (?, 1)",
            (nom,)
        )

        return curseur.lastrowid

    # ------------------------------------------------------
    # Controles
    # ------------------------------------------------------

    def analyser(self, chemin):
        """
        Controle le fichier sans rien ecrire.

        Renvoie un dictionnaire :
            lignes    : nombre de lignes lues
            valides   : lignes importables
            erreurs   : liste de messages bloquants
            avertissements : liste de messages non bloquants
            marques_a_creer : marques absentes de la base
        """

        rapport = {
            "lignes": 0,
            "valides": 0,
            "erreurs": [],
            "avertissements": [],
            "marques_a_creer": [],
        }

        try:
            lignes = self.lire_fichier(chemin)

        except Exception as erreur:

            rapport["erreurs"].append(
                f"Fichier illisible : {erreur}"
            )
            return rapport

        rapport["lignes"] = len(lignes)

        if not lignes:
            rapport["erreurs"].append("Le fichier est vide.")
            return rapport

        colonnes_obligatoires = [
            "type_produit",
            "nom",
            "marque",
            "fournisseur",
            "reference_fournisseur",
        ]

        for colonne in colonnes_obligatoires:

            if colonne not in lignes[0]:

                rapport["erreurs"].append(
                    f"Colonne obligatoire absente : {colonne}"
                )

        if rapport["erreurs"]:
            return rapport

        eans_fichier = {}
        refs_fichier = {}

        for ligne in lignes:

            numero = ligne["_ligne"]

            # --- type de produit

            type_produit = ligne.get("type_produit", "").lower()

            if type_produit not in self.CODES_NUMEROTATION:

                rapport["erreurs"].append(
                    f"Ligne {numero} : type de produit inconnu "
                    f"({type_produit or 'vide'})"
                )
                continue

            # --- nom

            if not ligne.get("nom"):

                rapport["erreurs"].append(
                    f"Ligne {numero} : nom vide"
                )
                continue

            # --- fournisseur

            fournisseur_id = self.trouver_id(
                "fournisseurs", ligne.get("fournisseur")
            )

            if fournisseur_id is None:

                rapport["erreurs"].append(
                    f"Ligne {numero} : fournisseur introuvable "
                    f"({ligne.get('fournisseur')})"
                )
                continue

            # --- reference fournisseur, doublons

            reference = ligne.get("reference_fournisseur", "")

            if not reference:

                rapport["erreurs"].append(
                    f"Ligne {numero} : reference fournisseur vide"
                )
                continue

            if reference in refs_fichier:

                rapport["erreurs"].append(
                    f"Ligne {numero} : reference {reference} deja "
                    f"presente ligne {refs_fichier[reference]}"
                )
                continue

            refs_fichier[reference] = numero

            existe = self.db.lire_un(
                "SELECT id, nom FROM produits "
                "WHERE reference_fournisseur = ? "
                "AND fournisseur_id = ?",
                (reference, fournisseur_id)
            )

            if existe:

                rapport["erreurs"].append(
                    f"Ligne {numero} : la reference {reference} "
                    f"existe deja en base ({existe['nom']})"
                )
                continue

            # --- EAN

            ean = ligne.get("ean", "")

            if ean:

                if ean in eans_fichier:

                    rapport["erreurs"].append(
                        f"Ligne {numero} : EAN {ean} deja present "
                        f"ligne {eans_fichier[ean]}"
                    )
                    continue

                eans_fichier[ean] = numero

                deja = self.db.lire_un(
                    "SELECT nom FROM produits WHERE ean = ?",
                    (ean,)
                )

                if deja:

                    rapport["erreurs"].append(
                        f"Ligne {numero} : EAN {ean} deja en base "
                        f"({deja['nom']})"
                    )
                    continue

            else:

                rapport["avertissements"].append(
                    f"Ligne {numero} : pas d'EAN"
                )

            # --- marque

            marque = ligne.get("marque", "")

            if marque and self.trouver_id("marques", marque) is None:

                if marque not in rapport["marques_a_creer"]:
                    rapport["marques_a_creer"].append(marque)

            # --- correspondances non bloquantes

            for colonne, table in [
                ("categorie_site", "categories_site"),
                ("theme_template", "themes_template"),
                ("famille_produit", "familles_produit"),
            ]:

                valeur = ligne.get(colonne, "")

                if valeur and self.trouver_id(table, valeur) is None:

                    rapport["avertissements"].append(
                        f"Ligne {numero} : {colonne} introuvable "
                        f"({valeur}) - le champ restera vide"
                    )

            rapport["valides"] += 1

        return rapport

    # ------------------------------------------------------
    # Import reel
    # ------------------------------------------------------

    def nombre(self, valeur):

        if valeur in (None, ""):
            return None

        try:
            return float(str(valeur).replace(",", "."))
        except ValueError:
            return None

    def entier(self, valeur, defaut=0):

        nombre = self.nombre(valeur)

        return defaut if nombre is None else int(nombre)

    def importer(self, chemin):
        """
        Cree reellement les produits.

        Ne cree QUE les lignes valides : une ligne en erreur
        est ignoree, les autres passent quand meme.
        """

        rapport = self.analyser(chemin)

        rapport["crees"] = 0
        rapport["marques_creees"] = []

        if rapport["erreurs"] and rapport["valides"] == 0:
            return rapport

        lignes = self.lire_fichier(chemin)

        lignes_en_erreur = set()

        for message in rapport["erreurs"]:

            morceaux = message.split()

            if len(morceaux) > 1 and morceaux[0] == "Ligne":
                lignes_en_erreur.add(morceaux[1].rstrip(" :"))

        for ligne in lignes:

            if str(ligne["_ligne"]) in lignes_en_erreur:
                continue

            type_produit = ligne.get("type_produit", "").lower()

            if type_produit not in self.CODES_NUMEROTATION:
                continue

            marque = ligne.get("marque", "")

            existait = self.trouver_id("marques", marque) is not None

            marque_id = self.trouver_ou_creer_marque(marque)

            if marque and not existait:
                rapport["marques_creees"].append(marque)

            sku = self.numerotation.generer(
                self.CODES_NUMEROTATION[type_produit]
            )

            self.productManager.ajouter(

                type_produit=type_produit,

                # NULL et non chaine vide : la colonne est
                # UNIQUE, et SQLite refuse deux chaines vides
                # identiques mais accepte autant de NULL.
                ean=ligne.get("ean") or None,

                sku=sku,

                nom=ligne.get("nom"),

                licence_id=None,

                marque_id=marque_id,

                fournisseur_id=self.trouver_id(
                    "fournisseurs", ligne.get("fournisseur")
                ),

                reference_fournisseur=ligne.get(
                    "reference_fournisseur"
                ),

                prix_fournisseur_ht=self.nombre(
                    ligne.get("prix_fournisseur_ht")
                ),

                famille_produit_id=self.trouver_id(
                    "familles_produit", ligne.get("famille_produit")
                ),

                longueur=self.nombre(ligne.get("longueur")),
                largeur=self.nombre(ligne.get("largeur")),
                hauteur=self.nombre(ligne.get("hauteur")),
                poids=self.nombre(ligne.get("poids")),

                image_principale=ligne.get("image_principale") or None,
                image_2=ligne.get("image_2") or None,
                image_3=ligne.get("image_3") or None,

                quantite_stock=self.entier(
                    ligne.get("quantite_stock"), 0
                ),

                statut_stock=ligne.get("statut_stock") or "actif",

                eligible_papier_cadeau=self.entier(
                    ligne.get("eligible_papier_cadeau"), 0
                ),

                # Toujours a 1 : il manquera forcement le
                # poids, les descriptions ou le SEO.
                fiche_a_terminer=1,

                categorie_site_id=self.trouver_id(
                    "categories_site", ligne.get("categorie_site")
                ),

                theme_template_id=self.trouver_id(
                    "themes_template", ligne.get("theme_template")
                ),
            )

            rapport["crees"] += 1

        return rapport