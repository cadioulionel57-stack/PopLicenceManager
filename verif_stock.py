"""
Compare ce qui est ecrit dans la fiche produit et ce que
l'ecran Stock affiche, ligne par ligne.

A lancer depuis la racine du projet :
    python verif_stock.py
"""

from database.database import Database
from modules.stock_manager import StockManager

db = Database()
manager = StockManager()

produits = db.lire(
    """
    SELECT id, sku, nom, quantite_stock, prix_achat_gestion,
           prix_fournisseur_ht
    FROM produits
    WHERE type_produit = 'stock'
      AND actif = 1
    ORDER BY sku
    """
)

print()
print(f"{'SKU':<10} {'PRODUIT':<32} {'FICHE':>6} {'STOCK':>6} {'PRIX FICHE':>11}")
print("-" * 70)

a_reprendre = []

for produit in produits:

    fiche = produit["quantite_stock"] or 0
    reel = manager.quantite(produit["id"])
    prix = (
        produit["prix_achat_gestion"]
        or produit["prix_fournisseur_ht"]
    )

    print(
        f"{produit['sku'] or '':<10} "
        f"{(produit['nom'] or '')[:32]:<32} "
        f"{fiche:>6} {reel:>6} "
        f"{(f'{prix:.2f}' if prix else '-'):>11}"
    )

    if fiche == 0 and reel == 0:
        a_reprendre.append(produit["sku"])

print()

if a_reprendre:
    print("Fiches a zero (rien a reprendre tant qu'elles le restent) :")
    for sku in a_reprendre:
        print("   -", sku)
    print()
    print("Renseigne la quantite dans ces fiches produit,")
    print("puis relance :  python reprise_stock.py")
else:
    print("Toutes les fiches ont une quantite.")