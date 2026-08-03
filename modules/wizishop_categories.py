r"""
modules/wizishop_categories.py
------------------------------------------------------------
Pousse les categories de PopLicenceManager vers WiziShop.

Lit la table categories_site, cree chaque categorie via l'API
et enregistre aussitot l'identifiant renvoye par WiziShop dans
la colonne id_wizishop.

Le traitement est REPRENABLE : toute categorie qui possede deja
un id_wizishop est ignoree. On peut donc relancer sans risque
de doublon.

Usage depuis la racine du projet :
    python -m modules.wizishop_categories etat
    python -m modules.wizishop_categories demo
    python -m modules.wizishop_categories principales
    python -m modules.wizishop_categories sous
------------------------------------------------------------
"""

import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError

BASE_PATH = Path(__file__).parent.parent / "database" / "poplicence.db"

# Pause entre deux appels, pour ne pas declencher la limite de debit
PAUSE_ENTRE_APPELS = 0.6


class PousseeCategories:

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else BASE_PATH
        self.api = WiziShopAPI()
        self.connexion = sqlite3.connect(str(self.base_path))
        self.connexion.row_factory = sqlite3.Row

    def fermer(self):
        self.connexion.close()

    # ------------------------------------------------------------------
    # Lecture de la base
    # ------------------------------------------------------------------

    def _lignes(self, principales):
        if principales:
            condition = "categorie_parente_id IS NULL"
        else:
            condition = "categorie_parente_id IS NOT NULL"
        requete = (
            "SELECT id, nom, id_wizishop, categorie_parente_id "
            f"FROM categories_site WHERE {condition} ORDER BY id"
        )
        return self.connexion.execute(requete).fetchall()

    def _id_wizishop_du_parent(self, parent_id):
        ligne = self.connexion.execute(
            "SELECT id_wizishop FROM categories_site WHERE id=?", (parent_id,)
        ).fetchone()
        return ligne["id_wizishop"] if ligne else None

    def _enregistrer_id(self, ligne_id, id_wizishop):
        self.connexion.execute(
            "UPDATE categories_site SET id_wizishop=? WHERE id=?",
            (str(id_wizishop), ligne_id),
        )
        self.connexion.commit()

    def etat(self):
        total = self.connexion.execute(
            "SELECT COUNT(*) FROM categories_site"
        ).fetchone()[0]
        faites = self.connexion.execute(
            "SELECT COUNT(*) FROM categories_site "
            "WHERE id_wizishop IS NOT NULL AND id_wizishop <> ''"
        ).fetchone()[0]
        principales = self.connexion.execute(
            "SELECT COUNT(*) FROM categories_site WHERE categorie_parente_id IS NULL"
        ).fetchone()[0]
        return (
            f"Categories dans le logiciel : {total} "
            f"({principales} principales, {total - principales} sous-categories)\n"
            f"Deja poussees vers WiziShop : {faites}\n"
            f"Restant a pousser : {total - faites}"
        )

    # ------------------------------------------------------------------
    # Adresses (slugs)
    # ------------------------------------------------------------------

    def _slug(self, texte):
        texte = unicodedata.normalize("NFKD", texte)
        texte = "".join(c for c in texte if not unicodedata.combining(c))
        texte = texte.lower().replace("&", "et").replace("'", " ")
        garde = [c if (c.isalnum() or c == " ") else " " for c in texte]
        return "-".join("".join(garde).split())

    def _slugs_deja_pris(self):
        pris = set()
        for categorie in self.api.lister_categories():
            if categorie.get("url"):
                pris.add(categorie["url"])
            for enfant in categorie.get("children") or []:
                if enfant.get("url"):
                    pris.add(enfant["url"])
        return pris

    def _slug_unique(self, nom, pris, nom_parent=None):
        base = self._slug(nom)
        if base not in pris:
            pris.add(base)
            return base
        if nom_parent:
            avec_parent = base + "-" + self._slug(nom_parent)
            if avec_parent not in pris:
                pris.add(avec_parent)
                return avec_parent
        indice = 2
        while f"{base}-{indice}" in pris:
            indice += 1
        pris.add(f"{base}-{indice}")
        return f"{base}-{indice}"

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def _creer(self, nom, url, id_parent):
        shop_id = self.api.id_boutique()
        corps = {
            "id_parent": int(id_parent),
            "name": nom,
            "url": url,
            "menu_title": nom,
            "visible": True,
        }
        reponse = self.api._appel(
            "POST", f"/v3/shops/{shop_id}/categories", corps=corps
        )
        return reponse.get("id")

    def pousser(self, principales):
        lignes = self._lignes(principales)
        pris = self._slugs_deja_pris()
        crees, ignorees, echecs = 0, 0, []

        for ligne in lignes:
            if ligne["id_wizishop"]:
                ignorees += 1
                continue

            if principales:
                id_parent = 0
                nom_parent = None
            else:
                id_parent = self._id_wizishop_du_parent(ligne["categorie_parente_id"])
                if not id_parent:
                    echecs.append(
                        f"{ligne['nom']} : sa categorie parente n'est pas encore "
                        "poussee vers WiziShop"
                    )
                    continue
                parent = self.connexion.execute(
                    "SELECT nom FROM categories_site WHERE id=?",
                    (ligne["categorie_parente_id"],),
                ).fetchone()
                nom_parent = parent["nom"] if parent else None

            url = self._slug_unique(ligne["nom"], pris, nom_parent)

            try:
                id_wizishop = self._creer(ligne["nom"], url, id_parent)
                if not id_wizishop:
                    echecs.append(f"{ligne['nom']} : aucun identifiant renvoye")
                    continue
                self._enregistrer_id(ligne["id"], id_wizishop)
                crees += 1
                print(f"   OK  {ligne['nom']}  ->  id WiziShop {id_wizishop}")
            except WiziShopAPIError as erreur:
                echecs.append(f"{ligne['nom']} : {erreur}")
                print(f"   ECHEC  {ligne['nom']}")

            time.sleep(PAUSE_ENTRE_APPELS)

        rapport = [
            f"Creees : {crees}",
            f"Deja faites, ignorees : {ignorees}",
            f"Echecs : {len(echecs)}",
        ]
        for message in echecs[:20]:
            rapport.append("   - " + message)
        return "\n".join(rapport)

    # ------------------------------------------------------------------
    # Categories de demonstration WiziShop
    # ------------------------------------------------------------------

    def lister_demo(self):
        lignes = []
        for categorie in self.api.lister_categories():
            lignes.append(
                f"id {categorie.get('id')} : {categorie.get('name')} "
                f"({len(categorie.get('children') or [])} sous-categories)"
            )
        return "\n".join(lignes) if lignes else "Aucune categorie dans la boutique."

    def supprimer(self, id_categorie):
        shop_id = self.api.id_boutique()
        self.api._appel("DELETE", f"/v3/shops/{shop_id}/categories/{id_categorie}")
        return f"Categorie {id_categorie} supprimee."


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "etat"
    poussee = PousseeCategories()
    try:
        if action == "etat":
            print(poussee.etat())
        elif action == "demo":
            print(poussee.lister_demo())
        elif action == "supprimer":
            print(poussee.supprimer(sys.argv[2]))
        elif action == "principales":
            print(poussee.pousser(principales=True))
        elif action == "sous":
            print(poussee.pousser(principales=False))
        else:
            print("Actions : etat | demo | supprimer <id> | principales | sous")
    except WiziShopAPIError as erreur:
        print("ERREUR :", erreur)
    finally:
        poussee.fermer()