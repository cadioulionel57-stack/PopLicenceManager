import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.wizishop_api import WiziShopAPI

BASE = Path(__file__).parent.parent / "database" / "poplicence.db"

connexion = sqlite3.connect(str(BASE))
ligne = connexion.execute(
    "SELECT nom, id_wizishop FROM produits WHERE id = ?",
    (int(sys.argv[1]),)
).fetchone()
connexion.close()

print("\nProduit :", ligne[0], "| id WiziShop :", ligne[1], "\n")

api = WiziShopAPI()
produit = api._appel(
    "GET", "/v3/shops/%s/products/%s" % (api.id_boutique(), ligne[1])
)

print(json.dumps({
    "status": produit.get("status"),
    "visible": produit.get("visible"),
    "complete": produit.get("complete"),
    "price_tax_excluded": produit.get("price_tax_excluded"),
    "tax": produit.get("tax"),
    "meta": produit.get("meta"),
    "attributes": produit.get("attributes"),
}, indent=2, ensure_ascii=False))