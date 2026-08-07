r"""
Retrouve les numeros de tes badges WiziShop.

Le catalogue de la boutique porte, pour chaque produit, la
liste de ses badges avec leur numero et leur libelle. On va
donc les chercher la.

Ce script ne modifie rien : il lit et il affiche.

Usage :
    python corriger_hauteur_hero.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.wizishop_api import WiziShopAPI, WiziShopAPIError


def chercher(objet, cle_voulue, resultats):
    """
    Parcourt toute la reponse et ramasse tout ce qui se
    trouve sous la cle demandee.
    """

    if isinstance(objet, dict):

        for cle, valeur in objet.items():

            if cle == cle_voulue and valeur:
                resultats.append(valeur)

            chercher(valeur, cle_voulue, resultats)

    elif isinstance(objet, list):

        for valeur in objet:
            chercher(valeur, cle_voulue, resultats)


if __name__ == "__main__":

    api = WiziShopAPI()

    shop = api.id_boutique()

    reponse = api._appel("GET", f"/v3/shops/{shop}/catalog")

    print("\n=== BADGES TROUVES DANS LE CATALOGUE ===\n")

    badges = []
    chercher(reponse, "badges", badges)

    vus = {}

    for groupe in badges:

        if isinstance(groupe, dict):
            groupe = [groupe]

        for badge in groupe:

            if isinstance(badge, dict) and "id" in badge:
                vus[badge["id"]] = badge

    if vus:
        for numero, badge in sorted(vus.items()):
            print(
                f"   numero {numero:<4} "
                f"{badge.get('label') or badge.get('name') or ''}  "
                f"{badge.get('color', '')}"
            )
    else:
        print("   aucun badge trouve dans le catalogue")

    print("\n=== BADGE POSE SUR CHAQUE PRODUIT ===\n")

    options = []
    chercher(reponse, "product_advanced_option", options)

    for option in options:

        if isinstance(option, dict):
            print(f"   badge_id : {option.get('badge_id')}")

    print("\n=== EXTRAIT BRUT, pour que je voie la structure ===\n")

    print(json.dumps(reponse, ensure_ascii=False)[:1200])

    print()