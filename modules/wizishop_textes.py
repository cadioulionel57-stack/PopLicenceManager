r"""
modules/wizishop_textes.py
------------------------------------------------------------
Cherche et remplace un texte dans la description de TOUTES
les categories WiziShop.

Le texte descriptif d'une categorie vit dans le champ content
de l'API. Ce module le lit, applique le remplacement, et le
renvoie. Il ne touche a rien d'autre : ni le nom, ni l'URL,
ni les balises SEO.

Usage depuis la racine du projet :
    python -m modules.wizishop_textes chercher "4,99"
    python -m modules.wizishop_textes remplacer "4,99" "6,90"
------------------------------------------------------------
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError

PAUSE_ENTRE_APPELS = 0.6


class TextesCategories:

    def __init__(self):
        self.api = WiziShopAPI()

    def _toutes(self):
        """Aplatit l'arborescence en (categorie, id du parent)."""
        plat = []

        def parcourir(liste, id_parent=0):
            for categorie in liste:
                plat.append((categorie, id_parent))
                parcourir(categorie.get("children") or [], categorie.get("id"))

        parcourir(self.api.lister_categories())
        return plat

    def chercher(self, texte):
        trouvees = []
        for categorie, _ in self._toutes():
            contenu = categorie.get("content") or ""
            if texte in contenu:
                trouvees.append(
                    f"   {categorie.get('name')} ({contenu.count(texte)} fois)"
                )
        if not trouvees:
            return f"Aucune categorie ne contient : {texte}"
        return f"Categories contenant '{texte}' : {len(trouvees)}\n" + "\n".join(trouvees)

    def remplacer(self, ancien, nouveau):
        shop_id = self.api.id_boutique()
        faites, echecs = 0, []

        for categorie, id_parent in self._toutes():
            contenu = categorie.get("content") or ""
            if ancien not in contenu:
                continue

            corps = {
                "id_parent": int(id_parent or 0),
                "name": categorie.get("name"),
                "url": categorie.get("url"),
                "menu_title": categorie.get("menu_title") or categorie.get("name"),
                "visible": True,
                "content": contenu.replace(ancien, nouveau),
                "meta": categorie.get("meta") or {},
            }

            try:
                self.api._appel(
                    "PUT",
                    f"/v3/shops/{shop_id}/categories/{categorie.get('id')}",
                    corps=corps,
                )
                faites += 1
                print(f"   OK  {categorie.get('name')}")
            except WiziShopAPIError as erreur:
                echecs.append(f"{categorie.get('name')} : {erreur}")
                print(f"   ECHEC  {categorie.get('name')}")

            time.sleep(PAUSE_ENTRE_APPELS)

        rapport = [f"Categories corrigees : {faites}", f"Echecs : {len(echecs)}"]
        for message in echecs[:20]:
            rapport.append("   - " + message)
        return "\n".join(rapport)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "aide"
    outil = TextesCategories()
    try:
        if action == "chercher" and len(sys.argv) > 2:
            print(outil.chercher(sys.argv[2]))
        elif action == "remplacer" and len(sys.argv) > 3:
            print(outil.remplacer(sys.argv[2], sys.argv[3]))
        else:
            print('Actions : chercher "<texte>" | remplacer "<ancien>" "<nouveau>"')
    except WiziShopAPIError as erreur:
        print("ERREUR :", erreur)