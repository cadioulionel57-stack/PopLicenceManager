from database.database import Database


class ProductManager:

    def __init__(self):

        self.db = Database()

    def ajouter(
        self,
        type_produit,
        ean,
        sku,
        nom,
        licence_id,
        marque_id,
        fournisseur_id,
        reference_fournisseur,
        categorie_poplicence_id=None,
        famille_produit_id=None,
        marge_visee_pourcentage=None,
        longueur=None,
        largeur=None,
        hauteur=None,
        poids=None,
        matiere=None,
        couleur=None,
        age_minimum=None,
        pays_fabrication=None,
    ):
        """
        Crée un produit et renvoie son identifiant
        (nécessaire ensuite pour enregistrer ses
        catégories par canal de vente).
        """

        curseur = self.db.executer(
            """
            INSERT INTO produits
            (
                type_produit,
                ean,
                sku,
                nom,
                licence_id,
                marque_id,
                fournisseur_id,
                reference_fournisseur,
                categorie_poplicence_id,
                famille_produit_id,
                marge_visee_pourcentage,
                longueur,
                largeur,
                hauteur,
                poids,
                matiere,
                couleur,
                age_minimum,
                pays_fabrication,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                type_produit,
                ean,
                sku,
                nom,
                licence_id,
                marque_id,
                fournisseur_id,
                reference_fournisseur,
                categorie_poplicence_id,
                famille_produit_id,
                marge_visee_pourcentage,
                longueur,
                largeur,
                hauteur,
                poids,
                matiere,
                couleur,
                age_minimum,
                pays_fabrication,
            )
        )

        return curseur.lastrowid

    def tous(self):

        return self.db.lire(
            """
            SELECT
                p.id,
                p.type_produit,
                p.ean,
                p.sku,
                p.nom,
                p.reference_fournisseur,
                p.licence_id,
                p.marque_id,
                p.fournisseur_id,
                l.nom AS licence,
                m.nom AS marque,
                f.nom AS fournisseur
            FROM produits p

            LEFT JOIN licences l
                ON l.id = p.licence_id

            LEFT JOIN marques m
                ON m.id = p.marque_id

            LEFT JOIN fournisseurs f
                ON f.id = p.fournisseur_id

            WHERE p.actif = 1

            ORDER BY p.nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM produits
            WHERE id = ?
            """,
            (identifiant,)
        )

    def modifier(
        self,
        identifiant,
        type_produit,
        ean,
        nom,
        licence_id,
        marque_id,
        fournisseur_id,
        reference_fournisseur,
        categorie_poplicence_id=None,
        famille_produit_id=None,
        marge_visee_pourcentage=None,
        longueur=None,
        largeur=None,
        hauteur=None,
        poids=None,
        matiere=None,
        couleur=None,
        age_minimum=None,
        pays_fabrication=None,
    ):

        self.db.executer(
            """
            UPDATE produits
            SET
                type_produit = ?,
                ean = ?,
                nom = ?,
                licence_id = ?,
                marque_id = ?,
                fournisseur_id = ?,
                reference_fournisseur = ?,
                categorie_poplicence_id = ?,
                famille_produit_id = ?,
                marge_visee_pourcentage = ?,
                longueur = ?,
                largeur = ?,
                hauteur = ?,
                poids = ?,
                matiere = ?,
                couleur = ?,
                age_minimum = ?,
                pays_fabrication = ?
            WHERE id = ?
            """,
            (
                type_produit,
                ean,
                nom,
                licence_id,
                marque_id,
                fournisseur_id,
                reference_fournisseur,
                categorie_poplicence_id,
                famille_produit_id,
                marge_visee_pourcentage,
                longueur,
                largeur,
                hauteur,
                poids,
                matiere,
                couleur,
                age_minimum,
                pays_fabrication,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE produits
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Catégories par canal de vente
    #
    # Un produit peut avoir une catégorie différente pour
    # chaque canal (Amazon, Cdiscount, WiziShop...). Cette
    # liste n'est jamais figée : elle dépend simplement des
    # canaux actifs au moment de l'enregistrement.
    ########################################################

    def categories_canaux(self, produit_id):
        """
        Renvoie {canal_id: categorie_id} pour un produit.
        """

        lignes = self.db.lire(
            """
            SELECT canal_id, categorie_id
            FROM produits_categories_canaux
            WHERE produit_id = ?
            """,
            (produit_id,)
        )

        return {
            ligne["canal_id"]: ligne["categorie_id"]
            for ligne in lignes
        }

    def definir_categories_canaux(self, produit_id, mapping):
        """
        Remplace les catégories par canal d'un produit.

        mapping : {canal_id: categorie_id}
        """

        self.db.executer(
            """
            DELETE FROM produits_categories_canaux
            WHERE produit_id = ?
            """,
            (produit_id,)
        )

        for canal_id, categorie_id in mapping.items():

            self.db.executer(
                """
                INSERT INTO produits_categories_canaux
                (
                    produit_id,
                    canal_id,
                    categorie_id
                )
                VALUES
                (
                    ?, ?, ?
                )
                """,
                (
                    produit_id,
                    canal_id,
                    categorie_id
                )
            )

    ########################################################
    # Publication sur les canaux de vente
    #
    # Détermine sur quels canaux un produit est vendu
    # (WiziShop, Amazon, Cdiscount...), avec sa référence
    # externe et son statut sur ce canal précis.
    ########################################################

    def canaux_produit(self, produit_id):
        """
        Renvoie {canal_id: {publie, reference_externe, statut}}
        pour un produit.
        """

        lignes = self.db.lire(
            """
            SELECT canal_id, publie, reference_externe, statut
            FROM produits_canaux
            WHERE produit_id = ?
            """,
            (produit_id,)
        )

        return {
            ligne["canal_id"]: {
                "publie": bool(ligne["publie"]),
                "reference_externe": ligne["reference_externe"],
                "statut": ligne["statut"],
            }
            for ligne in lignes
        }

    def definir_canaux_produit(self, produit_id, lignes):
        """
        Remplace les informations de publication d'un
        produit pour tous les canaux.

        lignes : liste de dictionnaires
        {canal_id, publie, reference_externe, statut}
        """

        self.db.executer(
            """
            DELETE FROM produits_canaux
            WHERE produit_id = ?
            """,
            (produit_id,)
        )

        for ligne in lignes:

            self.db.executer(
                """
                INSERT INTO produits_canaux
                (
                    produit_id,
                    canal_id,
                    publie,
                    reference_externe,
                    statut
                )
                VALUES
                (
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    produit_id,
                    ligne["canal_id"],
                    1 if ligne["publie"] else 0,
                    ligne["reference_externe"],
                    ligne["statut"],
                )
            )