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
        reference_fournisseur
    ):

        self.db.executer(
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
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, 1
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
                reference_fournisseur
            )
        )

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
        reference_fournisseur
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
                reference_fournisseur = ?
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