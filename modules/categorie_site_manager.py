from database.database import Database


class CategorieSiteManager:
    """
    Gère les catégories du site (WiziShop) — distinctes des
    catégories de commission par canal. Une hiérarchie à
    deux niveaux : catégorie principale, et sous-catégories
    qui lui sont rattachées, chacune avec son identifiant
    WiziShop (#N).
    """

    def __init__(self):

        self.db = Database()

    def categories_principales(self):

        return self.db.lire(
            """
            SELECT *
            FROM categories_site
            WHERE actif = 1
            AND categorie_parente_id IS NULL
            ORDER BY nom
            """
        )

    def sous_categories(self, categorie_parente_id):

        return self.db.lire(
            """
            SELECT *
            FROM categories_site
            WHERE actif = 1
            AND categorie_parente_id = ?
            ORDER BY nom
            """,
            (categorie_parente_id,)
        )

    def toutes_sous_categories(self):
        """
        Toutes les sous-catégories, toutes catégories
        principales confondues, avec le nom de leur parent
        — pratique pour un menu déroulant unique côté fiche
        produit.
        """

        return self.db.lire(
            """
            SELECT
                cs.*,
                parent.nom AS nom_parent
            FROM categories_site cs

            INNER JOIN categories_site parent
                ON parent.id = cs.categorie_parente_id

            WHERE cs.actif = 1
            AND parent.actif = 1

            ORDER BY parent.nom, cs.nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM categories_site
            WHERE id = ?
            """,
            (identifiant,)
        )

    def obtenir_avec_parent(self, identifiant):
        """
        Renvoie la sous-catégorie ET sa catégorie principale
        d'un coup — utile pour l'export CSV, qui a besoin
        des deux niveaux.
        """

        return self.db.lire_un(
            """
            SELECT
                cs.id,
                cs.nom AS nom_sous_categorie,
                cs.id_wizishop AS id_wizishop_sous_categorie,
                parent.id AS id_categorie_principale,
                parent.nom AS nom_categorie_principale,
                parent.id_wizishop AS id_wizishop_categorie_principale
            FROM categories_site cs

            INNER JOIN categories_site parent
                ON parent.id = cs.categorie_parente_id

            WHERE cs.id = ?
            """,
            (identifiant,)
        )

    def ajouter(self, nom, id_wizishop, categorie_parente_id=None):

        curseur = self.db.executer(
            """
            INSERT INTO categories_site
            (nom, id_wizishop, categorie_parente_id, actif)
            VALUES (?, ?, ?, 1)
            """,
            (nom, id_wizishop, categorie_parente_id)
        )

        return curseur.lastrowid

    def modifier(self, identifiant, nom, id_wizishop, categorie_parente_id=None):

        self.db.executer(
            """
            UPDATE categories_site
            SET nom = ?, id_wizishop = ?, categorie_parente_id = ?
            WHERE id = ?
            """,
            (nom, id_wizishop, categorie_parente_id, identifiant)
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE categories_site
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )