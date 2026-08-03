from datetime import date

from database.database import Database
from modules.stock_manager import StockManager
from modules.inventaire_import_manager import InventaireImportManager


class ReceptionScanManager:
    """
    Contrôle d'une réception fournisseur au collecteur.

    On ne fait plus entrer en stock ce qui avait été
    COMMANDÉ, mais ce qui est réellement ARRIVÉ. Chaque
    livraison partielle s'ajoute à la précédente, et la
    commande reste ouverte tant qu'il reste un reliquat.
    """

    STATUT_PARTIEL = "Partiellement reçu"
    STATUT_COMPLET = "Reçu"

    def __init__(self):

        self.db = Database()
        self.stock = StockManager()
        self.lecteur = InventaireImportManager()

    ########################################################
    # Lecture du fichier — déléguée au module d'inventaire
    ########################################################

    def lire_fichier(self, chemin, **options):

        return self.lecteur.lire_fichier(chemin, **options)

    def detecter_separateur(self, chemin):

        return self.lecteur.detecter_separateur(chemin)

    ########################################################
    # Lignes de la commande
    ########################################################

    def lignes_commande(self, achat_id):
        """
        Les lignes de l'achat, avec le code-barres de la
        référence exacte — celui de la taille quand la ligne
        porte sur une déclinaison.
        """

        return self.db.lire(
            """
            SELECT
                l.id AS ligne_id,
                l.produit_id,
                l.variation_id,
                l.nom_produit,
                l.quantite,
                COALESCE(l.quantite_recue, 0) AS quantite_recue,
                l.prix_unitaire_ht,
                p.type_produit,
                p.nom AS nom_fiche,
                COALESCE(v.ean, p.ean) AS ean
            FROM achats_fournisseurs_lignes l
            LEFT JOIN produits p ON p.id = l.produit_id
            LEFT JOIN produits_variations v ON v.id = l.variation_id
            WHERE l.achat_id = ? AND l.actif = 1
            ORDER BY l.id
            """,
            (achat_id,),
        )

    ########################################################
    # Rapprochement
    ########################################################

    def preparer(self, achat_id, lectures):
        """
        Confronte le fichier scanné aux lignes de la
        commande.

        Renvoie (lignes, intrus) :
        - lignes : une entrée par ligne de commande, avec ce
          qui était attendu, ce qui avait déjà été reçu, ce
          qui vient d'être scanné et ce qu'il restera ;
        - intrus : les codes scannés qui ne correspondent à
          aucune ligne — un article livré par erreur, ou une
          référence jamais créée.
        """

        commandees = self.lignes_commande(achat_id)

        scannees = {}

        for lecture in lectures:

            trouve = self.lecteur.resoudre(lecture["code"])

            cle = (
                (trouve["produit_id"], trouve["variation_id"])
                if trouve else None
            )

            scannees.setdefault(
                cle, {"quantite": 0, "codes": []}
            )

            scannees[cle]["quantite"] += lecture["quantite"]
            scannees[cle]["codes"].append(lecture["code"])

        lignes = []
        consommees = set()

        for ligne in commandees:

            cle = (ligne["produit_id"], ligne["variation_id"])

            scanne = 0

            if cle in scannees:
                scanne = scannees[cle]["quantite"]
                consommees.add(cle)

            commande = ligne["quantite"] or 0
            deja = ligne["quantite_recue"] or 0

            lignes.append({
                "ligne_id": ligne["ligne_id"],
                "produit_id": ligne["produit_id"],
                "variation_id": ligne["variation_id"],
                "nom": ligne["nom_produit"] or ligne["nom_fiche"] or "",
                "ean": ligne["ean"] or "",
                "type_produit": ligne["type_produit"],
                "prix_unitaire_ht": ligne["prix_unitaire_ht"],
                "commande": commande,
                "deja_recue": deja,
                "scanne": scanne,
                "reliquat": commande - deja - scanne,
            })

        intrus = []

        for cle, valeur in scannees.items():

            if cle is None:

                for code in valeur["codes"]:
                    intrus.append({
                        "code": code,
                        "nom": "— code inconnu —",
                        "quantite": valeur["quantite"],
                    })

                continue

            if cle in consommees:
                continue

            nom = ""

            produit = self.db.lire_un(
                "SELECT nom FROM produits WHERE id = ?",
                (cle[0],),
            )

            if produit is not None:
                nom = produit["nom"] or ""

            intrus.append({
                "code": ", ".join(valeur["codes"]),
                "nom": nom or "— hors commande —",
                "quantite": valeur["quantite"],
            })

        return (lignes, intrus)

    ########################################################
    # Validation
    ########################################################

    def _numero_reception(self, achat_id):
        """
        Compte les réceptions déjà enregistrées sur cet
        achat. La première porte la référence de l'achat
        seule, pour que l'ancien garde-fou anti double
        entrée continue de jouer son rôle.
        """

        ligne = self.db.lire_un(
            """
            SELECT COUNT(DISTINCT reference) AS nombre
            FROM mouvements_stock
            WHERE origine = 'achat'
              AND (reference = ? OR reference LIKE ?)
            """,
            (str(achat_id), f"{achat_id}/R%"),
        )

        return (ligne["nombre"] if ligne else 0) + 1

    def appliquer(
        self, achat_id, lignes, date_reception=None, commentaire=""
    ):
        """
        Fait entrer en stock les quantités scannées, met à
        jour le cumul reçu de chaque ligne et le statut de
        l'achat.

        Renvoie (entrées écrites, nouveau statut).
        """

        if date_reception is None:
            date_reception = date.today().isoformat()

        achat = self.db.lire_un(
            "SELECT numero FROM achats_fournisseurs WHERE id = ?",
            (achat_id,),
        )

        numero = (achat["numero"] if achat else "") or str(achat_id)

        rang = self._numero_reception(achat_id)

        reference = (
            str(achat_id) if rang == 1 else f"{achat_id}/R{rang}"
        )

        remarque = commentaire.strip()

        entrees = 0

        for ligne in lignes:

            scanne = ligne.get("scanne") or 0

            if scanne <= 0:
                continue

            if ligne.get("type_produit") in StockManager.TYPES_GERES:

                texte = f"Réception achat {numero}"

                if rang > 1:
                    texte += f" — livraison {rang}"

                if remarque:
                    texte += f" — {remarque}"

                self.stock.enregistrer_mouvement(
                    produit_id=ligne["produit_id"],
                    type_mouvement=StockManager.ENTREE,
                    quantite=scanne,
                    origine="achat",
                    reference=reference,
                    prix_unitaire_ht=ligne.get("prix_unitaire_ht"),
                    commentaire=texte,
                    date_mouvement=date_reception,
                    variation_id=ligne["variation_id"],
                )

                entrees += 1

            self.db.executer(
                """
                UPDATE achats_fournisseurs_lignes
                SET quantite_recue = COALESCE(quantite_recue, 0) + ?
                WHERE id = ?
                """,
                (scanne, ligne["ligne_id"]),
            )

        statut = self._majStatut(achat_id, date_reception)

        return (entrees, statut)

    def _majStatut(self, achat_id, date_reception):
        """
        Reçu quand plus rien n'est attendu, partiellement
        reçu tant qu'il reste un reliquat.
        """

        lignes = self.lignes_commande(achat_id)

        if not lignes:
            return None

        reste = sum(
            max(
                0,
                (l["quantite"] or 0) - (l["quantite_recue"] or 0),
            )
            for l in lignes
        )

        recu = sum((l["quantite_recue"] or 0) for l in lignes)

        if recu <= 0:
            return None

        statut = (
            self.STATUT_COMPLET if reste == 0
            else self.STATUT_PARTIEL
        )

        if reste == 0:

            self.db.executer(
                """
                UPDATE achats_fournisseurs
                SET statut = ?, date_reception = ?
                WHERE id = ?
                """,
                (statut, date_reception, achat_id),
            )

        else:

            self.db.executer(
                """
                UPDATE achats_fournisseurs
                SET statut = ?
                WHERE id = ?
                """,
                (statut, achat_id),
            )

        return statut