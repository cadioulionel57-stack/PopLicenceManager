r"""
modules/wizishop_produits.py
------------------------------------------------------------
Pousse les produits vers WiziShop par l'API v3.

L'API v3 ne sait PAS piloter l'affichage (visible et status
sont ignores, teste le 08/08/2026). Le seul levier est la
COMPLETUDE. UN SEUL champ est donc retenu a l'envoi : la
DESCRIPTION COURTE. La fiche arrive incomplete, donc EN
BROUILLON, mais tout le SEO (titre, meta description,
mots-cles) est deja en place : rien a ressaisir dans
WiziShop.

Pour publier ensuite, la description courte est renvoyee :
    python -m modules.wizishop_produits publier <id>

IMAGES : pousser depose lui-meme les images sur GitHub sous
un nom francais issu du produit. WiziShop reprend le nom du
fichier comme balise ALT. Les images ne partent QU'A LA
CREATION ; une mise a jour n'y touche pas, pour ne creer
aucun doublon dans le gestionnaire d'images. Pour forcer le
renvoi apres avoir change une photo : ajouter --images.

    python -m modules.wizishop_produits etat
    python -m modules.wizishop_produits apercu <id>
    python -m modules.wizishop_produits pousser <id> [<id> ...]
    python -m modules.wizishop_produits publier <id> [<id> ...]

pousser et publier acceptent plusieurs identifiants et des
plages : pousser 23 24 25  ou  publier 30-64

PAR FOURNISSEUR, pour ne plus chercher les identifiants :

    python -m modules.wizishop_produits pousser --fournisseur Stor

Ce filtre ne retient QUE LES PRODUITS JAMAIS POUSSES. Une
fiche deja en ligne est ecartee de la liste : le travail
repris a la main dans WiziShop apres l'envoi ne peut pas
etre ecrase par cette voie.
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
from modules.images_github import deposer, slug, extension

BASE_PATH = Path(__file__).parent.parent / "database" / "poplicence.db"

PAUSE_ENTRE_APPELS = 0.6

NOM_BOUTIQUE = "Pop Licence"

NOM_VARIATION_CADEAU = "Emballage Cadeau"

PREFIXE_GITHUB = "https://raw.githubusercontent.com/"

COLONNES_IMAGES = ("image_principale", "image_2", "image_3")


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

    def a_pousser_par_fournisseur(self, nom_fournisseur):
        """
        Les produits ACTIFS d'un fournisseur qui n'ont JAMAIS
        ete pousses. La condition sur id_wizishop est le
        verrou : une fiche deja en ligne ne peut pas ressortir
        d'ici, donc le travail repris a la main dans WiziShop
        apres l'envoi ne risque rien.

        Le nom du fournisseur est compare sans tenir compte de
        la casse ni des espaces autour, pour que 'stor',
        'Stor' et ' Stor ' donnent le meme resultat.
        """

        cherche = (nom_fournisseur or "").strip().lower()

        if not cherche:
            raise ValueError("Aucun nom de fournisseur donne.")

        fournisseurs = self.connexion.execute(
            "SELECT id, nom FROM fournisseurs"
        ).fetchall()

        trouves = [
            ligne for ligne in fournisseurs
            if (ligne["nom"] or "").strip().lower() == cherche
        ]

        if not trouves:

            connus = ", ".join(
                sorted((l["nom"] or "") for l in fournisseurs)
            )

            raise ValueError(
                f"Fournisseur '{nom_fournisseur}' introuvable.\n"
                f"Fournisseurs enregistres : {connus}"
            )

        identifiants = [ligne["id"] for ligne in trouves]

        marques = ",".join("?" for _ in identifiants)

        lignes = self.connexion.execute(
            f"SELECT id, nom FROM produits "
            f"WHERE fournisseur_id IN ({marques}) "
            f"AND actif = 1 "
            f"AND (id_wizishop IS NULL OR id_wizishop = '' "
            f"     OR id_wizishop = 0) "
            f"ORDER BY id",
            identifiants
        ).fetchall()

        # Compte ce qui est ECARTE, pour le dire a l'ecran :
        # sans ce chiffre, une liste courte ressemble a un bug.

        deja = self.connexion.execute(
            f"SELECT COUNT(*) AS n FROM produits "
            f"WHERE fournisseur_id IN ({marques}) "
            f"AND actif = 1 "
            f"AND id_wizishop IS NOT NULL "
            f"AND id_wizishop != '' AND id_wizishop != 0",
            identifiants
        ).fetchone()["n"]

        nom_reel = trouves[0]["nom"]

        return [(l["id"], l["nom"]) for l in lignes], deja, nom_reel

    def preparer_images(self, identifiant):
        """
        Depose sur GitHub les images encore hebergees chez le
        fournisseur, sous un nom francais issu du nom du produit,
        et remplace les adresses dans la base.
        """

        produit = self.produit(identifiant)

        base = slug(produit["nom"])

        messages = []

        for rang, colonne in enumerate(COLONNES_IMAGES, start=1):

            adresse = (produit[colonne] or "").strip()

            if not adresse:
                continue

            if adresse.startswith(PREFIXE_GITHUB):
                continue

            nom_fichier = f"{base}-{rang}{extension(adresse)}"

            try:
                nouvelle = deposer(adresse, nom_fichier)

            except Exception as erreur:
                messages.append(
                    f"image {rang} NON renommee ({erreur}) : "
                    f"l'adresse du fournisseur part telle quelle"
                )
                continue

            self.connexion.execute(
                f"UPDATE produits SET {colonne} = ? WHERE id = ?",
                (nouvelle, identifiant)
            )

            messages.append(f"image {rang} renommee : {nom_fichier}")

        self.connexion.commit()

        return messages

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
        """
        UNE SEULE variation "Emballage Cadeau", avec une
        option par OCCASION saisie dans Parametres >
        Reglages. Le client n'en choisit qu'une : le
        supplement est donc facture une seule fois, quel
        que soit le nombre d'occasions proposees.
        """

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

        # Une occasion par ligne. Les lignes vides et les
        # doublons sont ecartes : envoyes tels quels, ils
        # creeraient chez WiziShop des choix vides mais
        # selectionnables.

        brut = parametres.obtenir("libelles_cadeau_choix") or ""

        occasions = []

        for ligne in brut.splitlines():

            texte = self._sans_emoji(ligne)

            if texte and texte not in occasions:
                occasions.append(texte)

        # Repli sur l'ancien libelle unique : tant que la
        # liste n'a jamais ete enregistree, la fiche part
        # exactement comme avant.

        if not occasions:

            unique = self._sans_emoji(
                parametres.obtenir("libelle_cadeau_oui")
                or "Je souhaite un Emballage Cadeau"
            )

            occasions = [unique]

        options = [{
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
        }]

        for occasion in occasions:

            options.append({
                "value": occasion,
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
            })

        return [{
            "name": NOM_VARIATION_CADEAU,
            "label": NOM_VARIATION_CADEAU,
            "options": options,
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
            for colonne in COLONNES_IMAGES
            if produit[colonne]
        ]

        if not images:
            avertissements.append("aucune image")

        restantes = [
            adresse for adresse in images
            if not adresse.startswith(PREFIXE_GITHUB)
        ]

        if restantes:
            avertissements.append(
                f"{len(restantes)} image(s) encore chez le "
                f"fournisseur : le nom de fichier ne sera pas "
                f"francais"
            )

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

        # TOUT LE SEO PART AVEC LA FICHE. Seule la DESCRIPTION
        # COURTE est retenue : c'est elle qui garde la fiche en
        # BROUILLON, et elle seule est renvoyee par publier.

        titre_seo = produit["titre_seo"] or ""
        meta_description = produit["meta_description"] or ""
        mots_cles = produit["mots_cles"] or ""

        if visible:
            description_courte = produit["description_courte"] or ""

            if not description_courte:
                avertissements.append(
                    "ATTENTION : description courte VIDE dans le "
                    "logiciel, la fiche restera en brouillon"
                )
        else:
            description_courte = ""

            avertissements.append(
                "description courte RETENUE : la fiche arrive "
                "en brouillon, tout le SEO est deja en place"
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

    def pousser(self, identifiant, visible=False, forcer_images=False):

        produit = self.produit(identifiant)

        deja = produit["id_wizishop"]

        messages_images = []

        # Les images ne sont preparees et envoyees qu'a la
        # CREATION, ou sur demande expresse avec --images.

        envoyer_images = (not deja) or forcer_images

        if envoyer_images:
            messages_images = self.preparer_images(identifiant)
            produit = self.produit(identifiant)

        corps, avertissements = self.payload(produit, visible=visible)

        avertissements = messages_images + avertissements

        shop = self.api.id_boutique()

        if deja:

            chemin = f"/v3/shops/{shop}/products/{deja}"

            A_PRESERVER = [
                "features",
                "tags",
                "product_advanced_option",
                "other_categories_id",
                "type_editor",
                "ecotax",
                "cross_selling_products_id",
            ]

            if not forcer_images:
                A_PRESERVER.append("images")

            try:
                existant = self.api._appel("GET", chemin)

                for cle in A_PRESERVER:
                    if cle in existant:
                        corps[cle] = existant[cle]

            except WiziShopAPIError:
                avertissements.append(
                    "fiche WiziShop illisible : les champs du "
                    "logiciel sont envoyes tels quels"
                )

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


def lire_identifiants(morceaux):

    identifiants = []

    for morceau in morceaux:

        if "-" in morceau:
            depart, arrivee = morceau.split("-", 1)
            identifiants.extend(range(int(depart), int(arrivee) + 1))
        else:
            identifiants.append(int(morceau))

    return identifiants


if __name__ == "__main__":

    arguments = sys.argv[1:]

    forcer_images = "--images" in arguments

    arguments = [a for a in arguments if a != "--images"]

    # --fournisseur <nom> : le nom peut contenir des espaces,
    # tout ce qui suit est donc repris jusqu'au bout.

    fournisseur_demande = None

    if "--fournisseur" in arguments:

        position = arguments.index("--fournisseur")

        fournisseur_demande = " ".join(
            arguments[position + 1:]
        ).strip()

        arguments = arguments[:position]

    action = arguments[0] if arguments else "etat"

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

        elif action == "apercu" and len(arguments) > 1:

            produit = poussee.produit(int(arguments[1]))

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

        elif action in ("pousser", "publier") and (
            len(arguments) > 1 or fournisseur_demande
        ):

            publication = (action == "publier")

            a_envoyer = []

            if fournisseur_demande:

                a_envoyer, ecartes, nom_reel = (
                    poussee.a_pousser_par_fournisseur(
                        fournisseur_demande
                    )
                )

                print(f"\nFOURNISSEUR : {nom_reel}")

                if ecartes:
                    print(
                        f"{ecartes} fiche(s) DEJA EN LIGNE, "
                        f"ecartee(s) : elles ne seront pas "
                        f"renvoyees."
                    )

            else:

                identifiants = lire_identifiants(arguments[1:])

                for identifiant in identifiants:

                    try:
                        produit = poussee.produit(identifiant)

                    except Exception:
                        print(
                            f"   {identifiant:>3}  introuvable, ignore"
                        )
                        continue

                    a_envoyer.append((identifiant, produit["nom"]))

            if not a_envoyer:
                print("\nAucun produit a traiter.\n")
                sys.exit(0)

            mot = "PUBLIER" if publication else "envoyer"

            print(f"\n{len(a_envoyer)} produit(s) a {mot} :\n")

            for identifiant, nom in a_envoyer:
                print(f"   {identifiant:>3}  {nom[:60]}")

            if forcer_images:
                print(
                    "\nLes images seront RENVOYEES "
                    "(--images demande)."
                )

            reponse = input(
                f"\n{mot} vers WiziShop ? (tape oui) : "
            )

            if reponse.strip().lower() not in ("oui", "o"):
                print("\nAnnule.\n")
                sys.exit(0)

            print()

            attendu = "visible" if publication else "draft"

            conformes = 0
            autres = []
            echecs = []

            for identifiant, nom in a_envoyer:

                try:
                    fait, id_ws, avertissements, etat = poussee.pousser(
                        identifiant,
                        visible=publication,
                        forcer_images=forcer_images,
                    )

                except Exception as erreur:
                    print(f"   {identifiant:>3}  ECHEC : {erreur}")
                    echecs.append(identifiant)
                    continue

                print(
                    f"   {identifiant:>3}  {str(fait):<9} "
                    f"WiziShop {str(id_ws):<6} etat {etat}"
                )

                if etat == attendu:
                    conformes += 1
                else:
                    autres.append((identifiant, etat))

                for texte in avertissements:
                    print(f"        - {texte}")

            if publication:
                print(f"\n{conformes} produit(s) PUBLIES.")
            else:
                print(f"\n{conformes} produit(s) arrives EN BROUILLON.")

            if autres:
                print(f"\nATTENTION, etat inattendu :")
                for identifiant, etat in autres:
                    print(f"   {identifiant} : {etat}")

            if echecs:
                print(f"\n{len(echecs)} echec(s) : {echecs}")

            print()

        else:
            print(
                "\nActions :\n"
                "   etat\n"
                "   apercu <id>\n"
                "   pousser <id> [<id> ...] [--images]\n"
                "   publier <id> [<id> ...]\n"
                "   pousser --fournisseur <nom>\n"
                "      ex : pousser 43\n"
                "      ex : pousser 30-64\n"
                "      ex : publier 30-64\n"
                "      ex : pousser --fournisseur Stor\n"
                "\n"
                "   --fournisseur ne retient QUE les produits\n"
                "   jamais pousses. Les fiches deja en ligne\n"
                "   sont ecartees et ne peuvent pas etre\n"
                "   ecrasees par cette voie.\n"
            )

    except (ValueError, WiziShopAPIError) as erreur:
        print(f"\nErreur : {erreur}\n")

    finally:
        poussee.fermer()