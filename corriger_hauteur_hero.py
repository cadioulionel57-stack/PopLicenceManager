r"""
Test : par quel champ WiziShop decide-t-il de l'etat d'un
produit cree par l'API ?

La documentation dit qu'une fiche incomplete reste en
"Brouillon" et qu'elle passe en "Affiche" des qu'elle est
complete a 100 %. On teste donc le champ "complete", et deux
autres noms possibles pour l'etat.

Chaque produit de test est supprime aussitot.

Usage :
    python corriger_hauteur_hero.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError


ESSAIS = [
    ("complete = False", {"complete": False}),
    ("state = hidden", {"state": "hidden"}),
    ("etat = hidden", {"etat": "hidden"}),
    ("complete False + status draft", {"complete": False, "status": "draft"}),
]


def corps_de_base(numero):

    return {
        "category_id": 48,
        "other_categories_id": [],
        "sku": f"TEST-API-{numero}",
        "name": f"TEST API A SUPPRIMER {numero}",
        "description": "test",
        "short_description": "test",
        "brand": "",
        "ean13": "",
        "isbn": "",
        "supplier": "",
        "supplier_reference": "",
        "tags": [],
        "features": [],
        "tax": 20,
        "weight": 0.1,
        "quantity": 1,
        "price_tax_excluded": 10,
        "wholesale_price_tax_excluded": 5,
        "reduction": 0,
        "reduction_type": "percentage",
        "images": [],
        "visible": False,
        "url": f"test-api-a-supprimer-{numero}",
        "attributes": [],
        "cross_selling_products_id": [],
        "meta": {"title": "", "description": "", "keywords": ""},
        "customizations": [],
        "complete": True,
    }


if __name__ == "__main__":

    api = WiziShopAPI()

    shop = api.id_boutique()

    print("\n=== CE QUE WIZISHOP EN FAIT ===\n")

    for numero, (libelle, ajout) in enumerate(ESSAIS, start=10):

        corps = corps_de_base(numero)
        corps.update(ajout)

        try:
            cree = api._appel(
                "POST", f"/v3/shops/{shop}/products", corps
            )

        except WiziShopAPIError as erreur:
            print(f"   {libelle:<32} refus : {str(erreur)[:60]}")
            continue

        identifiant = (cree or {}).get("id")

        relu = api._appel(
            "GET", f"/v3/shops/{shop}/products/{identifiant}"
        )

        print(
            f"   {libelle:<32} status = {str(relu.get('status')):<12} "
            f"complete = {relu.get('complete')}"
        )

        try:
            api._appel(
                "DELETE", f"/v3/shops/{shop}/products/{identifiant}"
            )
        except WiziShopAPIError:
            print(f"      (produit {identifiant} a supprimer a la main)")

    print()