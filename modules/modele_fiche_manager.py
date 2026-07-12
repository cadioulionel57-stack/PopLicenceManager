from database.database import Database


class ModeleFicheManager:
    """
    Gère les modèles de fiche produit (chartes HTML) par
    catégorie du site + type de produit (stock/dropshipping)
    — un seul actif à la fois par combinaison, les autres
    (Noël, soldes...) restent en mémoire pour être réactivés
    plus tard sans avoir à les recréer.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                mfp.*,
                cs.nom AS nom_categorie
            FROM modeles_fiche_produit mfp

            LEFT JOIN categories_site cs
                ON cs.id = mfp.categorie_site_id

            ORDER BY cs.nom, mfp.type_produit, mfp.nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )

    def obtenir_actif(self, categorie_site_id, type_produit):
        """
        Le modèle actif pour cette catégorie+type — celui
        utilisé à l'export. None si aucun n'existe encore.
        """

        return self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE categorie_site_id = ?
            AND type_produit = ?
            AND actif = 1
            """,
            (categorie_site_id, type_produit)
        )

    def ajouter(self, nom, categorie_site_id, type_produit, html_template):

        curseur = self.db.executer(
            """
            INSERT INTO modeles_fiche_produit
            (nom, categorie_site_id, type_produit, html_template, actif)
            VALUES (?, ?, ?, ?, 0)
            """,
            (nom, categorie_site_id, type_produit, html_template)
        )

        return curseur.lastrowid

    def modifier(
        self, identifiant, nom, categorie_site_id, type_produit,
        html_template
    ):

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET nom = ?, categorie_site_id = ?, type_produit = ?,
                html_template = ?
            WHERE id = ?
            """,
            (nom, categorie_site_id, type_produit, html_template,
             identifiant)
        )

    def basculer_actif(self, identifiant):
        """
        Active ce modèle et désactive automatiquement tout
        autre modèle de la même catégorie+type — un seul
        actif à la fois.
        """

        modele = self.obtenir(identifiant)

        if modele is None:
            return

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 0
            WHERE categorie_site_id = ?
            AND type_produit = ?
            """,
            (modele["categorie_site_id"], modele["type_produit"])
        )

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 1
            WHERE id = ?
            """,
            (identifiant,)
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            DELETE FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )