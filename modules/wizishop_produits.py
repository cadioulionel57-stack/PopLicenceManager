r"""
modules/wizishop_produits.py
------------------------------------------------------------
Pousse les produits vers WiziShop par l'API v3.

L'API v3 ne sait PAS piloter l'affichage (visible et status
sont ignores, teste le 08/08/2026). Le seul levier est la
COMPLETUDE. Quatre champs sont donc retenus a l'envoi :
titre SEO, description courte, meta description, mots-cles.
La fiche arrive incomplete, donc EN BROUILLON.

    python -m modules.wizishop_produits etat
    python -m modules.wizishop_produits apercu <id>
    python -m modules.wizishop_produits pousser <id>
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
from modules.parametre_manager import ParametreManager
from modules.wizishop_variations import groupes_variations

BASE_PATH = Path(__file__).parent.parent / "database" / "poplicence.db"

PAUSE_ENTRE_APPELS = 0.6

NOM_BOUTIQUE = "Pop Licence"

NOM_VARIATION_CADEAU = "Emballage Cadeau"


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

    @staticmethod
    def _sans_emoji(texte):

        return "".join(
            c for c in str(texte or "") if ord(c) < 256
        ).strip()

    def option_cadeau(self, produit):

        expedie_par_nous = produit["type_produit"] in ("stock", "bundle")

        if not (produit["eligible_papier_cadeau"] and expedie_par_nous):
            return []

        parametres = ParametreManager()

        prix_ttc = parametres.obtenir_nombre(
            "prix_emballage_cadeau", 2.90
        )

        supplement_ht = round(float(prix_ttc) / 1.2, 2)

        refus = self._sans_emoji(
            parametres.obtenir("libelle_cadeau_non") or "Non"
        )

        oui = self._sans_emoji(
            parametres.obtenir("libelle_cadeau_oui")
            or "Je souhaite un Emballage Cadeau"
        )

        return [{
            "name": NOM_VARIATION_CADEAU,
            "label": NOM_VARIATION_CADEAU,
            "options": [
                {
                    "value": refus,
                    "sku": "",
                    "ean13": "",
                    "weight": 0,
                    "quantity": 0,
                    "price_tax_excluded": 0,
                    "reduction": 0,
                    "reduction_type": "amount",
                    "image": "",
                    "active": True,
                    "default": True,
                },
                {
                    "value": oui,
                    "sku": "",
                    "ean13": "",
                    "weight": 0,
                    "quantity": 0,
                    "price_tax_excluded": supplement_ht,
                    "reduction": 0,
                    "reduction_type": "amount",
                    "image": "",
                    "active": True,
                    "default": False,
                },
            ],
        }]

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

        licence = self._valeur("licences", produit["licence_id"], "nom")

        fabricant = self._valeur("marques", produit["marque_id"], "nom") or ""

        marque = licence or fabricant

        if not licence and produit["type_produit"] == "bundle":
            marque = NOM_BOUTIQUE

        elif not licence and fabricant:
            avertissements.append(
                "aucune licence sur ce produit : c'est le "
                f"fabricant ({fabricant}) qui part en marque"
            )

        fournisseur = self._valeur(
            "fournisseurs", produit["fournisseur_id"], "nom"
        ) or ""

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

        try:
            remise = float(produit["remise_precommande"] or 0)
        except (KeyError, IndexError, TypeError, ValueError):
            remise = 0

        images = [
            produit[colonne]
            for colonne in ("image_principale", "image_2", "image_3")
            if produit[colonne]
        ]

        if not images:
            avertissements.append("aucune image")

        variations, alertes_variations = groupes_variations(
            self.connexion, produit, prix_ht
        )

        ean_produit = produit["ean"] or ""

        if variations:

            sans_ean = [
                option
                for groupe in variations
                for option in groupe["options"]
                if not option["ean13"]
            ]

            if len(sans_ean) == 1 and ean_produit:

                sans_ean[0]["ean13"] = ean_produit

                avertissements.append(
                    f"l'EAN {ean_produit} a ete donne a la "
                    f"variation {sans_ean[0]['value']}"
                )

                alertes_variations = [
                    texte for texte in alertes_variations
                    if not texte.startswith("variations sans EAN")
                ]

                ean_produit = ""

        avertissements.extend(alertes_variations)

        # LES QUATRE CHAMPS RETENUS : c'est ce qui garde la
        # fiche en BROUILLON chez WiziShop.

        if visible:
            titre_seo = produit["titre_seo"] or ""
            description_courte = produit["description_courte"] or ""
            meta_description = produit["meta_description"] or ""
            mots_cles = produit["mots_cles"] or ""
        else:
            titre_seo = ""
            description_courte = ""
            meta_description = ""
            mots_cles = ""

            avertissements.append(
                "titre SEO, description courte, meta "
                "description et mots-cles RETENUS : la fiche "
                "arrive en brouillon"
            )

        corps = {
            "category_id": int(id_wizishop_categorie or 0),
            "other_categories_id": [],
            "sku": produit["sku"] or "",
            "name": produit["nom"] or "",
            "description": description,
            "short_description": description_courte,
            "brand": marque,
            "ean13": ean_produit,
            "isbn": "",
            "supplier": fournisseur,
            "supplier_reference": produit["reference_fournisseur"] or "",
            "tags": [],
            "features": [],
            "tax": float(produit["tva"] or 20),
            "weight": int(round(float(produit["poids"] or 0) * 1000)),
            "quantity": int(produit["quantite_stock"] or 0),
            "price_tax_excluded": round(float(prix_ht), 2),
            "wholesale_price_tax_excluded": round(
                float(produit["prix_fournisseur_ht"] or 0), 2
            ),
            "reduction": remise,
            "reduction_type": "percentage",
            "images": images,
            "attributes": (
                variations + self.option_cadeau(produit)
            ),
            "visible": bool(visible),
            "complete": bool(visible),
            "url": produit["url_slug"] or "",
            "cross_selling_products_id": [],
            "meta": {
                "title": titre_seo,
                "description": meta_description,
                "keywords": mots_cles,
            },
            "customizations": [],
        }

        return corps, avertissements

    def pousser(self, identifiant, visible=False):

        produit = self.produit(identifiant)

        corps, avertissements = self.payload(produit, visible=visible)

        shop = self.api.id_boutique()

        deja = produit["id_wizishop"]

        if deja:

            chemin = f"/v3/shops/{shop}/products/{deja}"

            A_PRESERVER = [
                "images",
                "features",
                "tags",
                "product_advanced_option",
                "other_categories_id",
                "type_editor",
                "ecotax",
                "cross_selling_products_id",
            ]

            try:
                existant = self.api._appel("GET", chemin)

                for cle in A_PRESERVER:
                    if cle in existant:
                        corps[cle] = existant[cle]

            except WiziShopAPIError:
                corps["images"] = []

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

        etat_reel = ""

        try:
            relu = self.api._appel(
                "GET", f"/v3/shops/{shop}/products/{id_wizishop}"
            )
            etat_reel = relu.get("status", "")
        except WiziShopAPIError:
            pass

        return action, id_wizishop, avertissements, etat_reel


if __name__ == "__main__":

    action = sys.argv[1] if len(sys.argv) > 1 else "etat"

    poussee = PousseeProduits()

    try:

        if action == "etat":

            lignes = poussee.connexion.execute(
                "SELECT id, nom, type_produit, id_wizishop "
                "FROM produits WHERE actif = 1 ORDER BY id"
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

            fait, id_ws, avertissements, etat = poussee.pousser(identifiant)

            print(f"\nProduit {fait}. Id WiziShop : {id_ws}")
            print(f"ETAT RENVOYE PAR WIZISHOP : {etat}")

            if avertissements:
                print("\nA savoir :")
                for texte in avertissements:
                    print(f"   - {texte}")
                print()

        else:
            print(
                "\nActions :\n"
                "   etat\n"
                "   apercu <id>\n"
                "   pousser <id>\n"
            )

    except (ValueError, WiziShopAPIError) as erreur:
        print(f"\nErreur : {erreur}\n")

    finally:
        poussee.fermer()