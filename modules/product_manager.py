from database.database import Database


class ProductManager:

    def __init__(self):

        self.db = Database()

    def ajouter(
        self,
        ean,
        sku,
        nom,
        licence,
        categorie,
        fournisseur,
        prix_achat,
        prix_vente,
        stock,
        poids,
        amazon,
        wizishop
    ):

        self.db.cursor.execute("""
        INSERT INTO produits(
            ean,
            sku,
            nom,
            licence,
            categorie,
            fournisseur,
            prix_achat,
            prix_vente,
            stock,
            poids,
            amazon,
            wizishop
        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
            ean,
            sku,
            nom,
            licence,
            categorie,
            fournisseur,
            prix_achat,
            prix_vente,
            stock,
            poids,
            amazon,
            wizishop
        ))

        self.db.conn.commit()