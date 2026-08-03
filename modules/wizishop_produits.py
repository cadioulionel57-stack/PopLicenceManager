r"""
modules/wizishop_produits.py
------------------------------------------------------------
Pousse les produits de PopLicenceManager vers WiziShop par
l'API v3.

Un produit part TOUJOURS MASQUE. Il n'apparait sur la
boutique qu'apres la commande "publier".

Usage depuis la racine du projet :
    python -m modules.wizishop_produits etat
    python -m modules.wizishop_produits apercu <id_produit>
    python -m modules.wizishop_produits pousser <id_produit>
    python -m modules.wizishop_produits publier <id_produit>
------------------------------------------------------------
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError
from modules.canal_manager import CanalManager
from modules.moteur_prix import MoteurPrix
from modules.generateur_fiche_html import GenerateurFicheHtml

BASE_PATH = Path(__file__).parent.parent / "database" / "poplicence.db"

PAUSE_ENTRE_APPELS = 0.6


class PousseeProduits:

    NOM_CANAL_SITE = "Site"

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else BASE_PATH
        self.connexion = sqlite3.connect(str(self.base_path))
        self.connexion.row_factory = sqlite3.Row
        self.api = WiziShopAPI()
        self.canaux = CanalManager()
        self.moteur_prix = MoteurPrix()

    def fermer(self):
        self.connexion.close()

    def produit(self, identifiant):

        ligne = self.connexion.execute(
            "SELECT * FROM produits WHERE id = ?", (identifiant,)
        ).fetchone()

        if ligne is None:
            raise ValueError(f"Produit {identifiant} introuvable.")

        return ligne

    def _valeur(self, table, identifiant, colonne):

        if not identifiant:
            return None

        ligne = self.connexion.execute(
            f"SELECT {colonne} FROM {table} WHERE id = ?",
            (identifiant,)
        ).fetchone()

        return ligne[colonne] if ligne else None

    def _canal_site_id(self):

        for canal in self.canaux.tous():
            if canal["nom"] == self.NOM_CANAL_SITE:
                return canal["id"]

        raise ValueError(
            f"Canal '{self.NOM_CANAL_SITE}' introuvable dans "
            f"Parametres > Canaux."
        )

    def payload(self, produit, visible=False):

        avertissements = []

        id_wizishop_categorie = self._valeur(
            "categories_site", produit["categorie_site_id"], "id_wizishop"
        )

        if not id_wizishop_categorie:
            avertissements.append(
                "aucune categorie WiziShop : le produit ne sera "
                "range nulle part"
            )

        # --- marque -------------------------------------
        #
        # La MARQUE cote WiziShop porte la LICENCE, pas le
        # fabricant : c'est la convention retenue pour le site
        # (une marque Bluey, une marque Marvel...). Le
        # fabricant reste une information interne.

        licence = self._valeur("licences", produit["licence_id"], "nom")

        fabricant = self._valeur("marques", produit["marque_id"], "nom") or ""

        marque = licence or fabricant

        if not licence and fabricant:
            avertissements.append(
                "aucune licence sur ce produit : c'est le "
                f"fabricant ({fabricant}) qui part en marque"
            )

        fournisseur = self._valeur(
            "fournisseurs", produit["fournisseur_id"], "nom"
        ) or ""

        # --- prix, calcule sur le canal Site --------------

        canal_id = self._canal_site_id()

        donnees = dict(produit)

        marge_canal = self.connexion.execute(
            "SELECT marge_pourcentage FROM produits_marges "
            "WHERE produit_id = ? AND canal_id = ?",
            (produit["id"], canal_id)
        ).fetchone()

        if marge_canal is not None:
            donnees["marge_visee_pourcentage"] = (
                marge_canal["marge_pourcentage"]
            )
        else:
            avertissements.append(
                "aucune marge propre au canal Site : la marge "
                "par defaut du produit est utilisee"
            )

        ligne_categorie = self.connexion.execute(
            "SELECT categorie_id FROM produits_categories_canaux "
            "WHERE produit_id = ? AND canal_id = ?",
            (produit["id"], canal_id)
        ).fetchone()

        categorie_canal = (
            ligne_categorie["categorie_id"] if ligne_categorie else None
        )

        resultat = self.moteur_prix.calculer(
            donnees, canal_id, categorie_canal
        )

        if resultat.get("erreur"):
            raise ValueError(
                f"Prix incalculable : {resultat['erreur']}"
            )

        prix_ht = resultat["prix_vente_ht"]

        description = GenerateurFicheHtml.generer(donnees, licence)

        if description is None:
            description = produit["description_longue"] or ""
            avertissements.append(
                "aucun modele de fiche actif : la description "
                "longue brute est envoyee a la place du HTML"
            )

        images = [
            produit[colonne]
            for colonne in ("image_principale", "image_2", "image_3")
            if produit[colonne]
        ]

        if not images:
            avertissements.append("aucune image")

        corps = {
            "category_id": int(id_wizishop_categorie or 0),
            "other_categories_id": [],
            "sku": produit["sku"] or "",
            "name": produit["nom"] or "",
            "description": description,
            "short_description": produit["description_courte"] or "",
            "brand": marque,
            "ean13": produit["ean"] or "",
            "isbn": "",
            "supplier": fournisseur,
            "supplier_reference": produit["reference_fournisseur"] or "",
            "tags": [],
            "features": [],
            "tax": float(produit["tva"] or 20),
            "weight": float(produit["poids"] or 0),
            "quantity": int(produit["quantite_stock"] or 0),
            "price_tax_excluded": round(float(prix_ht), 2),
            "wholesale_price_tax_excluded": round(
                float(produit["prix_fournisseur_ht"] or 0), 2
            ),
            "reduction": 0,
            "reduction_type": "percentage",
            "images": images,
            "visible": bool(visible),
            "url": produit["url_slug"] or "",
            "attributes": [],
            "cross_selling_products_id": [],
            "meta": {
                "title": produit["titre_seo"] or "",
                "description": produit["meta_description"] or "",
                "keywords": produit["mots_cles"] or "",
            },
            "customizations": [],
            "complete": True,
        }

        return corps, avertissements

    def pousser(self, identifiant, visible=False):
        """
        Envoie le produit. Par defaut il part MASQUE.
        """

        produit = self.produit(identifiant)

        corps, avertissements = self.payload(produit, visible=visible)

        shop = self.api.id_boutique()

        deja = produit["id_wizishop"]

        if deja:
            chemin = f"/v3/shops/{shop}/products/{deja}"
            self.api._appel("PUT", chemin, corps)
            action = "mis a jour"
            id_wizishop = deja

        else:
            chemin = f"/v3/shops/{shop}/products"
            reponse = self.api._appel("POST", chemin, corps)
            action = "cree"
            id_wizishop = (reponse or {}).get("id")

            if id_wizishop:
                self.connexion.execute(
                    "UPDATE produits SET id_wizishop = ?, "
                    "exporte_wizishop = 1 WHERE id = ?",
                    (id_wizishop, identifiant)
                )
                self.connexion.commit()

        time.sleep(PAUSE_ENTRE_APPELS)

        return action, id_wizishop, avertissements

    def publier(self, identifiant):
        """
        Rend le produit visible sur la boutique.
        """

        produit = self.produit(identifiant)

        if not produit["id_wizishop"]:
            raise ValueError(
                "Ce produit n'a pas encore ete envoye vers "
                "WiziShop. Lance d'abord : pousser."
            )

        return self.pousser(identifiant, visible=True)


if __name__ == "__main__":

    action = sys.argv[1] if len(sys.argv) > 1 else "etat"

    poussee = PousseeProduits()

    try:

        if action == "etat":

            lignes = poussee.connexion.execute(
                "SELECT id, nom, type_produit, id_wizishop "
                "FROM produits ORDER BY id"
            ).fetchall()

            print("\n=== PRODUITS DU LOGICIEL ===\n")

            for ligne in lignes:
                etat = (
                    f"WiziShop {ligne['id_wizishop']}"
                    if ligne["id_wizishop"] else "pas encore pousse"
                )
                print(
                    f"   {ligne['id']:>3}  {ligne['nom'][:40]:<42} "
                    f"{ligne['type_produit'] or '':<14} {etat}"
                )

            print()

        elif action == "apercu" and len(sys.argv) > 2:

            produit = poussee.produit(int(sys.argv[2]))

            corps, avertissements = poussee.payload(produit)

            apercu = dict(corps)
            longueur = len(apercu["description"])
            apercu["description"] = (
                f"<{longueur} caracteres de HTML genere>"
            )

            print("\n=== CE QUI SERAIT ENVOYE ===\n")
            print(json.dumps(apercu, indent=2, ensure_ascii=False))

            prix_ttc = round(corps["price_tax_excluded"] * 1.2, 2)
            print(f"\nPrix affiche sur le site : {prix_ttc} EUR TTC")

            if avertissements:
                print("\nA savoir :")
                for texte in avertissements:
                    print(f"   - {texte}")

            print("\nRien n'a ete envoye.\n")

        elif action == "pousser" and len(sys.argv) > 2:

            identifiant = int(sys.argv[2])

            produit = poussee.produit(identifiant)

            print(f"\nProduit : {produit['nom']}")

            reponse = input("Envoyer vers WiziShop ? (tape oui) : ")

            if reponse.strip().lower() not in ("oui", "o"):
                print("\nAnnule.\n")
                sys.exit(0)

            fait, id_wizishop, avertissements = poussee.pousser(identifiant)

            print(f"\nProduit {fait}. Id WiziShop : {id_wizishop}")
            print(
                "Il est envoye MASQUE : verifie la fiche dans "
                "WiziShop, puis publie-la avec\n"
                f"   python -m modules.wizishop_produits publier "
                f"{identifiant}\n"
            )

            if avertissements:
                print("A savoir :")
                for texte in avertissements:
                    print(f"   - {texte}")
                print()

        elif action == "publier" and len(sys.argv) > 2:

            identifiant = int(sys.argv[2])

            produit = poussee.produit(identifiant)

            print(f"\nProduit : {produit['nom']}")

            reponse = input("Le rendre VISIBLE sur la boutique ? (tape oui) : ")

            if reponse.strip().lower() not in ("oui", "o"):
                print("\nAnnule. Le produit reste masque.\n")
                sys.exit(0)

            poussee.publier(identifiant)

            print("\nProduit publie, il est maintenant en ligne.\n")

        else:
            print(
                "\nActions : etat | apercu <id> | pousser <id> | "
                "publier <id>\n"
            )

    except (ValueError, WiziShopAPIError) as erreur:
        print(f"\nErreur : {erreur}\n")

    finally:
        poussee.fermer()