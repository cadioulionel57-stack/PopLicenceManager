from modules.wizishop_api import WiziShopAPI
import sqlite3, json
c = sqlite3.connect("database/poplicence.db")
ws = c.execute("select id_wizishop from produits where id = 110").fetchone()[0]
api = WiziShopAPI()
fiche = api._appel("GET", f"/v3/shops/{api.id_boutique()}/products/{ws}")
print("id WiziShop :", ws)
print(json.dumps(fiche.get("images"), indent=2, ensure_ascii=False))
