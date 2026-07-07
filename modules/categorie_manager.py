from database.database import Database


class CategorieManager:
    """
    Gère les catégories de produits.

    Une catégorie peut être :
    - interne à Pop Licence (canal_id = None)
    - propre à un canal de vente précis (canal_id = X),
      pour refléter l'arbre de catégories de ce canal
      (Amazon, Cdiscount, WiziShop...).

    Chaque catégorie rattachée à un canal peut avoir sa
    propre commission (commission_pourcentage), qui prend
    le dessus sur la commission par défaut du canal. Si
    elle est vide, c'est la commission du canal qui
    s'applique automatiquement.

    Rien n'est figé : les catégories se créent librement
    depuis l'interface, pour n'importe quel canal existant.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                c.id,
                c.nom,
                c.canal_id,
                c.commission_pourcentage,
                c.actif,
                cv.nom AS canal,
                cv.commission_pourcentage AS commission_canal
            FROM categories c

            LEFT JOIN canaux_vente cv
                ON cv.id = c.canal_id

            WHERE c.actif = 1

            ORDER BY cv.nom, c.nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM categories
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(self, nom, canal_id=None, commission_pourcentage=None):

        self.db.executer(
            """
            INSERT INTO categories
            (
                nom,
                canal_id,
                commission_pourcentage,
                actif
            )
            VALUES
            (
                ?, ?, ?, 1
            )
            """,
            (
                nom,
                canal_id,
                commission_pourcentage
            )
        )

    def modifier(
        self,
        identifiant,
        nom,
        canal_id=None,
        commission_pourcentage=None
    ):

        self.db.executer(
            """
            UPDATE categories
            SET
                nom = ?,
                canal_id = ?,
                commission_pourcentage = ?
            WHERE id = ?
            """,
            (
                nom,
                canal_id,
                commission_pourcentage,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE categories
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def commission_effective(self, categorie_id):
        """
        Renvoie la commission qui s'applique réellement
        pour une catégorie : la sienne si elle en a une,
        sinon celle par défaut de son canal.
        """

        ligne = self.db.lire_un(
            """
            SELECT
                c.commission_pourcentage AS commission_categorie,
                cv.commission_pourcentage AS commission_canal
            FROM categories c

            LEFT JOIN canaux_vente cv
                ON cv.id = c.canal_id

            WHERE c.id = ?
            """,
            (categorie_id,)
        )

        if ligne is None:
            return None

        if ligne["commission_categorie"] is not None:
            return ligne["commission_categorie"]

        return ligne["commission_canal"]