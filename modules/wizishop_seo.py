r"""
modules/wizishop_seo.py
------------------------------------------------------------
Remplit les balises SEO des categories WiziShop.

Fabrique pour chaque categorie un titre (60 caracteres maximum)
et une meta description (155 caracteres maximum), puis les
envoie via PUT sur l'API.

Ne touche PAS au champ content : le texte descriptif de bas de
page s'ecrit a la main, il n'est pas concerne ici.

Usage depuis la racine du projet :
    python -m modules.wizishop_seo apercu
    python -m modules.wizishop_seo titres
------------------------------------------------------------
"""

import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError

BASE_PATH = Path(__file__).parent.parent / "database" / "poplicence.db"

BOUTIQUE = "Pop Licence"
LIMITE_TITRE = 60
LIMITE_DESCRIPTION = 155
PAUSE_ENTRE_APPELS = 0.6

# Parents dont les enfants sont des licences, pas des types de produit
PARENTS_LICENCE = ("Lego", "Playmobil", "Univers & Licences")


class BalisesSEO:

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else BASE_PATH
        self.api = WiziShopAPI()
        self.connexion = sqlite3.connect(str(self.base_path))
        self.connexion.row_factory = sqlite3.Row

    def fermer(self):
        self.connexion.close()

    # ------------------------------------------------------------------
    # Fabrication des balises
    # ------------------------------------------------------------------

    def _premier_qui_tient(self, propositions, limite):
        for texte in propositions:
            if len(texte) <= limite:
                return texte
        return propositions[-1][:limite].rstrip()

    def titre(self, nom, nom_parent):
        if nom_parent in ("Lego", "Playmobil"):
            marque = nom_parent.upper()
            return self._premier_qui_tient(
                [
                    f"{marque} {nom} - sets officiels | {BOUTIQUE}",
                    f"{marque} {nom} - sets officiels",
                    f"{marque} {nom}",
                ],
                LIMITE_TITRE,
            )

        if nom_parent == "Univers & Licences":
            return self._premier_qui_tient(
                [
                    f"{nom} - produits dérivés officiels | {BOUTIQUE}",
                    f"{nom} - produits dérivés officiels",
                    f"{nom} - produits dérivés",
                ],
                LIMITE_TITRE,
            )

        return self._premier_qui_tient(
            [
                f"{nom} sous licence officielle | {BOUTIQUE}",
                f"{nom} sous licence officielle",
                f"{nom} | {BOUTIQUE}",
                nom,
            ],
            LIMITE_TITRE,
        )

    def description(self, nom, nom_parent):
        if nom_parent in ("Lego", "Playmobil"):
            debut = f"Sets {nom_parent} {nom} officiels et neufs."
        elif nom_parent == "Univers & Licences":
            debut = f"Tous les produits dérivés {nom} sous licence officielle."
        else:
            debut = f"{nom} sous licence officielle."

        suite = (
            " Produits en stock expédiés le jour même avant 11h, "
            "du lundi au vendredi. Retours offerts 30 jours."
        )
        texte = debut + suite
        if len(texte) <= LIMITE_DESCRIPTION:
            return texte

        court = debut + " Stock expédié le jour même avant 11h. Retours offerts 30 jours."
        if len(court) <= LIMITE_DESCRIPTION:
            return court
        return court[:LIMITE_DESCRIPTION].rstrip()

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------

    def _lignes(self):
        return self.connexion.execute(
            "SELECT id, nom, id_wizishop, categorie_parente_id "
            "FROM categories_site ORDER BY id"
        ).fetchall()

    def _nom_parent(self, parent_id):
        if not parent_id:
            return None
        ligne = self.connexion.execute(
            "SELECT nom FROM categories_site WHERE id=?", (parent_id,)
        ).fetchone()
        return ligne["nom"] if ligne else None

    def _id_wizishop_parent(self, parent_id):
        if not parent_id:
            return 0
        ligne = self.connexion.execute(
            "SELECT id_wizishop FROM categories_site WHERE id=?", (parent_id,)
        ).fetchone()
        if ligne and ligne["id_wizishop"]:
            return int(ligne["id_wizishop"])
        return 0

    def _carte_wizishop(self):
        """Toutes les categories WiziShop, rangees par identifiant."""
        carte = {}

        def parcourir(liste):
            for categorie in liste:
                carte[str(categorie.get("id"))] = categorie
                parcourir(categorie.get("children") or [])

        parcourir(self.api.lister_categories())
        return carte

    # ------------------------------------------------------------------
    # Apercu
    # ------------------------------------------------------------------

    def apercu(self, combien=15):
        lignes = []
        for ligne in self._lignes()[:combien]:
            nom_parent = self._nom_parent(ligne["categorie_parente_id"])
            titre = self.titre(ligne["nom"], nom_parent)
            description = self.description(ligne["nom"], nom_parent)
            lignes.append(f"{ligne['nom']}")
            lignes.append(f"   TITRE ({len(titre)}) : {titre}")
            lignes.append(f"   META  ({len(description)}) : {description}")
            lignes.append("")
        return "\n".join(lignes)

    # ------------------------------------------------------------------
    # Envoi
    # ------------------------------------------------------------------

    def pousser(self):
        shop_id = self.api.id_boutique()
        carte = self._carte_wizishop()
        faits, sautes, echecs = 0, 0, []

        for ligne in self._lignes():
            identifiant = ligne["id_wizishop"]
            if not identifiant:
                sautes += 1
                continue

            info = carte.get(str(identifiant))
            if not info:
                echecs.append(f"{ligne['nom']} : introuvable sur WiziShop")
                continue

            nom_parent = self._nom_parent(ligne["categorie_parente_id"])
            corps = {
                "id_parent": self._id_wizishop_parent(ligne["categorie_parente_id"]),
                "name": info.get("name") or ligne["nom"],
                "url": info.get("url"),
                "menu_title": info.get("menu_title") or ligne["nom"],
                "visible": True,
                "meta": {
                    "title": self.titre(ligne["nom"], nom_parent),
                    "description": self.description(ligne["nom"], nom_parent),
                },
            }

            try:
                self.api._appel(
                    "PUT", f"/v3/shops/{shop_id}/categories/{identifiant}", corps=corps
                )
                faits += 1
                if faits % 20 == 0:
                    print(f"   {faits} categories traitees...")
            except WiziShopAPIError as erreur:
                echecs.append(f"{ligne['nom']} : {erreur}")

            time.sleep(PAUSE_ENTRE_APPELS)

        rapport = [
            f"Balises posees : {faits}",
            f"Sans identifiant WiziShop, sautees : {sautes}",
            f"Echecs : {len(echecs)}",
        ]
        for message in echecs[:20]:
            rapport.append("   - " + message)
        return "\n".join(rapport)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "apercu"
    balises = BalisesSEO()
    try:
        if action == "apercu":
            print(balises.apercu())
        elif action == "titres":
            print(balises.pousser())
        else:
            print("Actions : apercu | titres")
    except WiziShopAPIError as erreur:
        print("ERREUR :", erreur)
    finally:
        balises.fermer()