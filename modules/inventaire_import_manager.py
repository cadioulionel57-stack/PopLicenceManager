import csv

from datetime import date

from database.database import Database
from modules.stock_manager import StockManager


class InventaireImportManager:
    """
    Import d'un comptage d'inventaire réalisé au collecteur
    de données.

    L'appareil produit un fichier à deux colonnes : le
    code-barres scanné et la quantité saisie au clavier. Ce
    module le relit, retrouve à quel produit — ou à quelle
    taille — correspond chaque code, compare au stock
    théorique, et n'écrit les mouvements de régularisation
    qu'une fois le tableau validé à l'écran.
    """

    SEPARATEURS = [";", "\t", ",", "|"]

    def __init__(self):

        self.db = Database()
        self.stock = StockManager()

    ########################################################
    # Lecture du fichier
    ########################################################

    def detecter_separateur(self, chemin):
        """
        Devine le séparateur en regardant la première ligne
        utile. Les collecteurs sortent tantôt du point-virgule,
        tantôt de la tabulation, sans prévenir.
        """

        try:

            with open(
                chemin, "r", encoding="utf-8-sig", errors="ignore"
            ) as fichier:

                for ligne in fichier:

                    if not ligne.strip():
                        continue

                    meilleurs = [
                        (ligne.count(s), s) for s in self.SEPARATEURS
                    ]

                    meilleurs.sort(reverse=True)

                    if meilleurs[0][0] > 0:
                        return meilleurs[0][1]

                    return ";"

        except OSError:
            return ";"

        return ";"

    def lire_fichier(
        self,
        chemin,
        colonne_code=0,
        colonne_quantite=1,
        separateur=None,
        ignorer_premiere_ligne=False,
    ):
        """
        Renvoie la liste des couples code / quantité lus dans
        le fichier, en additionnant les quantités quand un
        même code revient plusieurs fois — cas courant quand
        on repasse dans un rayon.

        Chaque entrée : {"code", "quantite", "lignes"}.
        """

        if separateur is None:
            separateur = self.detecter_separateur(chemin)

        cumul = {}
        ordre = []

        with open(
            chemin, "r", encoding="utf-8-sig", errors="ignore", newline=""
        ) as fichier:

            lecteur = csv.reader(fichier, delimiter=separateur)

            for numero, cellules in enumerate(lecteur, start=1):

                if ignorer_premiere_ligne and numero == 1:
                    continue

                if not cellules:
                    continue

                if colonne_code >= len(cellules):
                    continue

                code = (cellules[colonne_code] or "").strip()

                if code == "":
                    continue

                quantite = 1

                if colonne_quantite < len(cellules):

                    brut = (cellules[colonne_quantite] or "").strip()
                    brut = brut.replace(" ", "").replace(",", ".")

                    try:
                        quantite = int(float(brut))
                    except ValueError:
                        quantite = 1

                if code not in cumul:
                    cumul[code] = {
                        "code": code,
                        "quantite": 0,
                        "lignes": [],
                    }
                    ordre.append(code)

                cumul[code]["quantite"] += quantite
                cumul[code]["lignes"].append(numero)

        return [cumul[code] for code in ordre]

    ########################################################
    # Résolution des codes
    ########################################################

    def resoudre(self, code):
        """
        Retrouve le produit ou la déclinaison portant ce
        code-barres. Cherche d'abord dans les variations —
        une taille a son propre EAN, et c'est elle qu'il faut
        mouvementer — puis dans les produits.

        Renvoie None si le code est inconnu.
        """

        if not code:
            return None

        variation = self.db.lire_un(
            """
            SELECT v.id AS variation_id,
                   v.produit_id AS produit_id,
                   v.libelle AS libelle,
                   p.nom AS nom
            FROM produits_variations v
            LEFT JOIN produits p ON p.id = v.produit_id
            WHERE v.ean = ? OR v.sku = ?
            """,
            (code, code),
        )

        if variation is not None:

            nom = variation["nom"] or ""
            libelle = variation["libelle"] or ""

            return {
                "produit_id": variation["produit_id"],
                "variation_id": variation["variation_id"],
                "nom": f"{nom} — {libelle}".strip(" —"),
            }

        produit = self.db.lire_un(
            """
            SELECT id, nom
            FROM produits
            WHERE (ean = ? OR sku = ?) AND actif = 1
            """,
            (code, code),
        )

        if produit is None:
            return None

        return {
            "produit_id": produit["id"],
            "variation_id": None,
            "nom": produit["nom"] or "",
        }

    ########################################################
    # Préparation du tableau des écarts
    ########################################################

    def preparer(self, lectures):
        """
        Enrichit chaque ligne lue avec le produit reconnu, le
        stock théorique et l'écart. Les codes inconnus sont
        conservés dans la liste, marqués comme tels — ils ne
        doivent pas disparaître en silence, c'est ainsi qu'on
        repère un article reçu mais jamais créé.
        """

        resultat = []

        for lecture in lectures:

            trouve = self.resoudre(lecture["code"])

            if trouve is None:

                resultat.append({
                    "code": lecture["code"],
                    "connu": False,
                    "nom": "— code inconnu —",
                    "produit_id": None,
                    "variation_id": None,
                    "quantite_comptee": lecture["quantite"],
                    "quantite_theorique": None,
                    "ecart": None,
                })

                continue

            theorique = self.stock.quantite(
                trouve["produit_id"], trouve["variation_id"]
            ) or 0

            resultat.append({
                "code": lecture["code"],
                "connu": True,
                "nom": trouve["nom"],
                "produit_id": trouve["produit_id"],
                "variation_id": trouve["variation_id"],
                "quantite_comptee": lecture["quantite"],
                "quantite_theorique": theorique,
                "ecart": lecture["quantite"] - theorique,
            })

        return resultat

    ########################################################
    # Écriture des mouvements
    ########################################################

    def appliquer(self, lignes, date_inventaire=None, commentaire=""):
        """
        Écrit les mouvements de régularisation pour les
        lignes reconnues dont l'écart n'est pas nul. Renvoie
        (nombre de mouvements écrits, nombre de lignes sans
        écart).

        Le prix d'achat moyen est repris pour les entrées :
        sans lui, la quantité serait juste mais la valeur du
        stock resterait fausse.
        """

        if date_inventaire is None:
            date_inventaire = date.today().strftime("%Y-%m-%d")

        remarque = commentaire.strip() or "Inventaire"

        ecrits = 0
        sans_ecart = 0

        for ligne in lignes:

            if not ligne.get("connu"):
                continue

            ecart = ligne.get("ecart") or 0

            if ecart == 0:
                sans_ecart += 1
                continue

            prix = None

            if ecart > 0:

                try:
                    prix = self.stock.prix_moyen(
                        ligne["produit_id"], ligne["variation_id"]
                    )
                except Exception:
                    prix = None

            self.stock.enregistrer_mouvement(
                produit_id=ligne["produit_id"],
                type_mouvement=(
                    StockManager.ENTREE if ecart > 0
                    else StockManager.SORTIE
                ),
                quantite=abs(ecart),
                origine="inventaire",
                reference="",
                prix_unitaire_ht=prix,
                commentaire=f"{remarque} — écart {ecart:+d}",
                date_mouvement=date_inventaire,
                variation_id=ligne["variation_id"],
            )

            ecrits += 1

        return (ecrits, sans_ecart)