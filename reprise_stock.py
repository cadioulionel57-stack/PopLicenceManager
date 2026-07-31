"""
Reprise du stock initial.

Reprend la quantite deja saisie dans chaque fiche produit
et la transforme en mouvement d'entree, pour que l'ecran
Stock parte de tes chiffres reels au lieu de zero.

Le prix unitaire est repris de la fiche : d'abord le prix
d'achat de gestion, sinon le prix fournisseur HT. Sans prix,
la quantite est quand meme reprise, mais la valeur restera a
zero tant que le prix ne sera pas renseigne.

A lancer une seule fois depuis la racine du projet :
    python reprise_stock.py

Relancer le script ne cree aucun doublon : les produits deja
repris sont ignores.
"""

from database.database import Database
from modules.stock_manager import StockManager


ORIGINE = "reprise"

db = Database()
manager = StockManager()

produits = db.lire(
    """
    SELECT
        id,
        sku,
        nom,
        quantite_stock,
        prix_achat_gestion,
        prix_fournisseur_ht
    FROM produits
    WHERE type_produit = 'stock'
      AND actif = 1
      AND COALESCE(quantite_stock, 0) > 0
    ORDER BY sku
    """
)

deja_repris = {
    ligne["produit_id"]
    for ligne in db.lire(
        "SELECT DISTINCT produit_id FROM mouvements_stock "
        "WHERE origine = ?",
        (ORIGINE,)
    )
}

repris = 0
ignores = 0
sans_prix = []

for produit in produits:

    if produit["id"] in deja_repris:
        ignores += 1
        continue

    prix = (
        produit["prix_achat_gestion"]
        or produit["prix_fournisseur_ht"]
        or None
    )

    if not prix:
        sans_prix.append(f"{produit['sku']} — {produit['nom']}")

    manager.enregistrer_mouvement(
        produit_id=produit["id"],
        type_mouvement=StockManager.ENTREE,
        quantite=produit["quantite_stock"],
        origine=ORIGINE,
        reference=produit["id"],
        prix_unitaire_ht=prix,
        commentaire="Reprise du stock saisi en fiche produit",
    )

    repris += 1

print()
print(f"Produits repris   : {repris}")
print(f"Deja repris avant : {ignores}")
print(f"Valeur du stock   : {manager.valeur_totale():.2f} EUR")

if sans_prix:
    print()
    print("Repris SANS prix d'achat (valeur a zero) :")
    for ligne in sans_prix:
        print("   -", ligne)
    print()
    print("Renseigne leur prix d'achat en fiche produit,")
    print("puis corrige-les avec le bouton Inventaire.")