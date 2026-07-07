from database.database import Database
 
 
class ProductLoader:
    """
    Charge la liste des produits avec leurs informations
    de référence (licence, marque, fournisseur) et leur
    statut de publication par canal de vente.
    """
 
    def __init__(self):
 
        self.db = Database()
 
    def charger(self):
 
        return self.db.lire(
            """
            SELECT
                p.id,
                p.ean,
                p.sku,
                p.type_produit,
                p.nom,
                p.reference_fournisseur,
                p.prix_fournisseur_ht,
                p.prix_achat_gestion,
                p.cout_revient,
                p.longueur,
                p.largeur,
                p.hauteur,
                p.poids,
                l.nom AS licence,
                m.nom AS marque,
                f.nom AS fournisseur,
                SUM(CASE WHEN pc.publie = 1 THEN 1 ELSE 0 END) AS nb_canaux_publies,
                COUNT(pc.id) AS nb_canaux_rattaches
            FROM produits p
 
            LEFT JOIN licences l
                ON l.id = p.licence_id
 
            LEFT JOIN marques m
                ON m.id = p.marque_id
 
            LEFT JOIN fournisseurs f
                ON f.id = p.fournisseur_id
 
            LEFT JOIN produits_canaux pc
                ON pc.produit_id = p.id
 
            WHERE p.actif = 1
 
            GROUP BY p.id
 
            ORDER BY p.nom
            """
        )
 
    def charger_pour_canal(self, canal_id):
        """
        Charge les produits ainsi que leur statut de
        publication pour un canal de vente donné
        (ex : WiziShop, Base.com, Amazon).
        """
 
        return self.db.lire(
            """
            SELECT
                p.id,
                p.ean,
                p.sku,
                p.nom,
                l.nom AS licence,
                f.nom AS fournisseur,
                pc.publie,
                pc.reference_externe,
                pc.statut
            FROM produits p
 
            LEFT JOIN licences l
                ON l.id = p.licence_id
 
            LEFT JOIN fournisseurs f
                ON f.id = p.fournisseur_id
 
            LEFT JOIN produits_canaux pc
                ON pc.produit_id = p.id
                AND pc.canal_id = ?
 
            WHERE p.actif = 1
 
            ORDER BY p.nom
            """,
            (canal_id,)
        )