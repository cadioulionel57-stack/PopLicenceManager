from database.database import Database


class ProductLoader:

    def __init__(self):

        self.db = Database()

    def charger(self):

        self.db.cursor.execute("""
            SELECT
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
            FROM produits
            ORDER BY nom
        """)

        return self.db.cursor.fetchall()