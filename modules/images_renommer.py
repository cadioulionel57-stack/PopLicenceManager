"""
Renomme les images d'un produit : les depose sur GitHub sous un nom
lisible, puis remplace les URL dans la base.

Le module de poussee lit les colonnes image_principale, image_2,
image_3 telles quelles : une fois les URL remplacees ici, la poussee
vers WiziShop envoie les adresses GitHub sans aucune modification.

Utilisation, depuis C:\\PopLicenceManager :
    python -m modules.images_renommer 45
    python -m modules.images_renommer 23 24 25
    python -m modules.images_renommer 23-64
"""

import sqlite3
import sys
from pathlib import Path

from modules.images_github import slug, extension, deposer

BASE = Path(__file__).resolve().parent.parent / "database" / "poplicence.db"

COLONNES = ("image_principale", "image_2", "image_3", "image_ambiance")

DEJA_FAIT = "raw.githubusercontent.com"


def _connexion():
    connexion = sqlite3.connect(BASE)
    connexion.row_factory = sqlite3.Row
    return connexion


def identifiants(morceaux):
    """Accepte 45, plusieurs id, ou une plage 23-64."""
    resultat = []
    for morceau in morceaux:
        if "-" in morceau:
            debut, fin = morceau.split("-", 1)
            resultat.extend(range(int(debut), int(fin) + 1))
        else:
            resultat.append(int(morceau))
    return resultat


def renommer(produit_id, connexion):
    ligne = connexion.execute(
        "SELECT id, nom, image_principale, image_2, image_3, "
        "image_ambiance FROM produits WHERE id = ?",
        (produit_id,),
    ).fetchone()

    if ligne is None:
        print(f"  {produit_id} : introuvable")
        return 0

    base = slug(ligne["nom"])
    changees = 0

    for rang, colonne in enumerate(COLONNES, start=1):
        source = ligne[colonne]

        if not source:
            continue

        if DEJA_FAIT in source:
            print(f"  {colonne} : deja renommee")
            continue

        nom = f"{base}-{rang}{extension(source)}"

        try:
            nouvelle = deposer(source, nom)
        except Exception as erreur:
            print(f"  {colonne} : ECHEC ({erreur})")
            continue

        connexion.execute(
            f"UPDATE produits SET {colonne} = ? WHERE id = ?",
            (nouvelle, produit_id),
        )
        print(f"  {colonne} -> {nom}")
        changees += 1

    connexion.commit()
    return changees


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    connexion = _connexion()
    total = 0

    for produit_id in identifiants(sys.argv[1:]):
        ligne = connexion.execute(
            "SELECT nom FROM produits WHERE id = ?", (produit_id,)
        ).fetchone()
        nom = ligne["nom"] if ligne else "?"
        print(f"\n[{produit_id}] {nom}")
        total += renommer(produit_id, connexion)

    connexion.close()
    print(f"\n{total} image(s) renommee(s).\n")


if __name__ == "__main__":
    main()