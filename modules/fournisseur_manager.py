from database.database import Database


class FournisseurManager:
    """
    Gère les fournisseurs — distinct de ReferenceManager
    (Marques, etc.) car un fournisseur a des champs propres
    (contact, téléphone, email, site, conditions
    commerciales), pas de description.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM fournisseurs
            WHERE actif = 1
            ORDER BY nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM fournisseurs
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        nom,
        contact="",
        telephone="",
        email="",
        site="",
        seuil_minimum_commande=None,
        franco_port=None,
        frais_port=None,
        conditions_reglement="",
        delai_livraison="",
        actif=True
    ):

        curseur = self.db.executer(
            """
            INSERT INTO fournisseurs
            (
                nom,
                contact,
                telephone,
                email,
                site,
                seuil_minimum_commande,
                franco_port,
                frais_port,
                conditions_reglement,
                delai_livraison,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                nom,
                contact,
                telephone,
                email,
                site,
                seuil_minimum_commande,
                franco_port,
                frais_port,
                conditions_reglement,
                delai_livraison,
                1 if actif else 0
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        nom,
        contact="",
        telephone="",
        email="",
        site="",
        seuil_minimum_commande=None,
        franco_port=None,
        frais_port=None,
        conditions_reglement="",
        delai_livraison="",
        actif=True
    ):

        self.db.executer(
            """
            UPDATE fournisseurs
            SET
                nom = ?,
                contact = ?,
                telephone = ?,
                email = ?,
                site = ?,
                seuil_minimum_commande = ?,
                franco_port = ?,
                frais_port = ?,
                conditions_reglement = ?,
                delai_livraison = ?,
                actif = ?
            WHERE id = ?
            """,
            (
                nom,
                contact,
                telephone,
                email,
                site,
                seuil_minimum_commande,
                franco_port,
                frais_port,
                conditions_reglement,
                delai_livraison,
                1 if actif else 0,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE fournisseurs
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )