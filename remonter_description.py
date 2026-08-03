r"""
remonter_description.py
------------------------------------------------------------
Remonte le bloc DESCRIPTION juste apres la banniere du haut.

Aujourd'hui le visiteur doit faire defiler la banniere,
l'univers produit, les points cles et le bloc confort avant
de lire ce qu'est le produit. La description arrive en
cinquieme position. Le script la deplace en deuxieme.

Rien n'est ajoute ni supprime : les memes sections, dans un
autre ordre.

Seuls les modeles qui possedent A LA FOIS un HERO et une
DESCRIPTION sont traites. Les modeles Direct Fournisseur et
Precommande, batis autrement, ne sont pas touches.

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

VARIABLE = re.compile(r"\{\{[#/]?[a-zA-Z0-9_]+\}\}")


def compter_variables(html):
    return len(VARIABLE.findall(html))


def sections(html):
    """
    Decoupe le modele en (titre, texte) selon les
    commentaires de section.
    """

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

    entete, morceaux = sections(html)

    if not morceaux:
        return html, False

    titres = [t for t, _ in morceaux]

    index_hero = next(
        (i for i, t in enumerate(titres) if t.startswith("HERO")),
        None
    )

    index_desc = next(
        (i for i, t in enumerate(titres) if t.startswith("DESCRIPTION")),
        None
    )

    if index_hero is None or index_desc is None:
        return html, False

    if index_desc == index_hero + 1:
        return html, False

    description = morceaux.pop(index_desc)

    if index_desc < index_hero:
        index_hero -= 1

    morceaux.insert(index_hero + 1, description)

    return entete + "".join(texte for _, texte in morceaux), True


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

    print("\n=== REMONTEE DU BLOC DESCRIPTION ===\n")

    prevus = []
    ecartes = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, fait = corriger(html)

        if not fait:
            continue

        # Garde-fous : meme longueur, memes variables. Le
        # script ne fait que reordonner, rien ne doit se
        # perdre en route.

        if len(nouveau_html) != len(html):
            ecartes.append((modele["nom"], "longueur modifiee"))
            continue

        if compter_variables(nouveau_html) != compter_variables(html):
            ecartes.append((modele["nom"], "variables modifiees"))
            continue

        _, morceaux = sections(nouveau_html)
        ordre = " > ".join(t[:18] for t, _ in morceaux)

        print(f"   {modele['nom'][:38]:<40} {ordre}")

        prevus.append((modele["id"], nouveau_html))

    if ecartes:
        print("\n/!\\ ECARTES par securite :")
        for nom, raison in ecartes:
            print(f"   {nom} : {raison}")
        print()

    if not prevus:
        print("\nRien a deplacer.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a reordonner.\n")

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
        """
        SELECT html_template FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        """
    )

    variables = sum(
        compter_variables(l["html_template"]) for l in apres
    )

    print(f"Variables et blocs conditionnels : {variables}\n")