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

    Une catégorie peut aussi avoir plusieurs PALIERS de
    commission selon le prix de vente (ex : Amazon
    Vêtements : 5% jusqu'à 15€, 10% jusqu'à 20€, 17%
    au-delà). Si des paliers existent, ils prennent le
    dessus sur commission_pourcentage.

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

        curseur = self.db.executer(
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

        return curseur.lastrowid

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

    ########################################################
    # Paliers de commission selon le prix de vente
    ########################################################

    def paliers(self, categorie_id):
        """
        Renvoie les paliers de commission d'une catégorie,
        triés du seuil le plus bas au plus haut (le palier
        "sans limite" toujours en dernier).
        """

        return self.db.lire(
            """
            SELECT *
            FROM paliers_commission_categorie
            WHERE categorie_id = ?
            ORDER BY
                CASE WHEN seuil_prix_max IS NULL THEN 1 ELSE 0 END,
                seuil_prix_max ASC
            """,
            (categorie_id,)
        )

    def definir_paliers(self, categorie_id, paliers):
        """
        Remplace tous les paliers d'une catégorie.

        paliers : liste de dictionnaires
        {seuil_prix_max, commission_pourcentage}
        (seuil_prix_max = None pour le dernier palier,
        sans limite haute)
        """

        self.db.executer(
            """
            DELETE FROM paliers_commission_categorie
            WHERE categorie_id = ?
            """,
            (categorie_id,)
        )

        for ordre, palier in enumerate(paliers):

            self.db.executer(
                """
                INSERT INTO paliers_commission_categorie
                (
                    categorie_id,
                    seuil_prix_max,
                    commission_pourcentage,
                    ordre
                )
                VALUES
                (
                    ?, ?, ?, ?
                )
                """,
                (
                    categorie_id,
                    palier["seuil_prix_max"],
                    palier["commission_pourcentage"],
                    ordre
                )
            )

    def commission_effective(self, categorie_id, prix_vente=None):
        """
        Renvoie la commission qui s'applique réellement
        pour une catégorie et (si fourni) un prix de vente
        donné :

        1. S'il existe des paliers pour cette catégorie,
           on utilise le palier correspondant au prix de
           vente (ou le premier palier si aucun prix n'est
           fourni, à titre d'estimation de départ).
        2. Sinon, la commission propre à la catégorie si
           elle existe.
        3. Sinon, la commission par défaut du canal.
        """

        paliers = self.paliers(categorie_id)

        if paliers:

            if prix_vente is None:
                return paliers[0]["commission_pourcentage"]

            for palier in paliers:

                if palier["seuil_prix_max"] is None:
                    return palier["commission_pourcentage"]

                if prix_vente <= palier["seuil_prix_max"]:
                    return palier["commission_pourcentage"]

            return paliers[-1]["commission_pourcentage"]

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

    ########################################################
    # Duplication des catégories vers un autre canal
    #
    # Utile par exemple pour recopier les catégories et
    # commissions déjà saisies pour Amazon FBM vers Amazon
    # FBA, puisque la commission de vente (hors transport)
    # est généralement identique entre les deux.
    ########################################################

    def dupliquer_vers_canal(self, canal_source_id, canal_cible_id):
        """
        Copie toutes les catégories actives d'un canal
        source vers un canal cible, avec leur commission
        et leurs éventuels paliers de prix.

        Ne touche pas aux catégories déjà existantes sur
        le canal cible : ajoute uniquement des copies.

        Renvoie le nombre de catégories dupliquées.
        """

        categories_source = self.db.lire(
            """
            SELECT *
            FROM categories
            WHERE canal_id = ?
            AND actif = 1
            """,
            (canal_source_id,)
        )

        compteur = 0

        for categorie in categories_source:

            nouvel_id = self.ajouter(
                nom=categorie["nom"],
                canal_id=canal_cible_id,
                commission_pourcentage=categorie["commission_pourcentage"],
            )

            paliers = self.paliers(categorie["id"])

            if paliers:

                self.definir_paliers(
                    nouvel_id,
                    [
                        {
                            "seuil_prix_max": p["seuil_prix_max"],
                            "commission_pourcentage": p["commission_pourcentage"],
                        }
                        for p in paliers
                    ]
                )

            compteur += 1

        return compteur