r"""
remonter_description.py  (5e version)
------------------------------------------------------------
Deux corrections sur les modeles de fiche :

  1. L'IMAGE DE BANNIERE UNIVERS. 21 modeles contiennent
     encore un texte a remplacer laisse par leur auteur,
     du type URL_IMAGE_BANNIERE_DF_PELUCHES_ICI, au lieu de
     la variable {{image_fond_univers}}. L'adresse saisie
     dans le logiciel n'etait donc jamais lue. Le script
     branche la variable a la place.

  2. LA BANNIERE BLEUE Direct Fournisseur est supprimee des
     modeles, comme la verte l'a ete pour les produits en
     stock. Elle est identique sur toutes les fiches et ne
     dit rien du produit.

Relancable sans risque : ce qui est deja fait est ignore.

Usage :
    python remonter_description.py
------------------------------------------------------------
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


MARQUEUR = re.compile(r"<!--\s*=+\s*(.{0,80}?)\s*=+\s*-->", re.S)

PLACEHOLDER = re.compile(r"URL_IMAGE[A-Z0-9_]*")

VARIABLE = re.compile(r"\{\{[#/]?[a-zA-Z0-9_]+\}\}")


def compter_variables(html):
    return len(VARIABLE.findall(html))


def sections(html):

    reperes = list(MARQUEUR.finditer(html))

    if not reperes:
        return "", []

    entete = html[: reperes[0].start()]

    morceaux = []

    for i, m in enumerate(reperes):

        fin = (
            reperes[i + 1].start()
            if i + 1 < len(reperes)
            else len(html)
        )

        titre = re.sub(r"\s+", " ", m.group(1)).strip().upper()

        morceaux.append((titre, html[m.start(): fin]))

    return entete, morceaux


def corriger(html):
    """
    Renvoie (html, images_branchees, banniere_retiree).
    """

    images = len(PLACEHOLDER.findall(html))

    if images:
        html = PLACEHOLDER.sub("{{image_fond_univers}}", html)

    banniere = False

    entete, morceaux = sections(html)

    if morceaux:

        restants = [
            (titre, texte)
            for titre, texte in morceaux
            if not (
                "BANNIÈRE DIRECT FOURNISSEUR" in titre
                or "BANNIERE DIRECT FOURNISSEUR" in titre
            )
        ]

        if len(restants) != len(morceaux):
            banniere = True
            html = entete + "".join(t for _, t in restants)

    return html, images, banniere


if __name__ == "__main__":

    db = Database()

    modeles = db.lire(
        """
        SELECT id, nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        ORDER BY nom
        """
    )

    print("\n=== IMAGE UNIVERS ET BANNIERE BLEUE ===\n")

    prevus = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, images, banniere = corriger(html)

        if not images and not banniere:
            continue

        detail = []

        if images:
            detail.append(f"{images} image(s) branchee(s)")

        if banniere:
            detail.append("banniere bleue retiree")

        print(f"   {modele['nom'][:40]:<42} {', '.join(detail)}")

        prevus.append((modele["id"], nouveau_html))

    if not prevus:
        print("\nRien a corriger.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) concerne(s).\n")

    reponse = input("Appliquer ? (tape oui puis Entree) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnule. Rien n'a ete modifie.\n")
        sys.exit(0)

    for modele_id, nouveau_html in prevus:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (nouveau_html, modele_id)
        )

    print(f"\n{len(prevus)} modele(s) corrige(s).\n")

    apres = db.lire(
        "SELECT html_template FROM modeles_fiche_produit "
        "WHERE html_template IS NOT NULL"
    )

    restants = sum(
        len(PLACEHOLDER.findall(l["html_template"])) for l in apres
    )

    print(f"Textes a remplacer restants : {restants}\n")