r"""
remonter_description.py  (4e version)
------------------------------------------------------------
Traite les 17 modeles DIRECT FOURNISSEUR, qui n'avaient rien
recu jusqu'ici : chez eux la description ne s'appelle pas
DESCRIPTION mais INTRO SEO, et mes scripts precedents
passaient a cote.

Deux operations, sur cette seule section :

  1. INTRO SEO remonte TOUT EN HAUT de la fiche.

  2. Un paragraphe de donnees est ajoute juste apres la
     premiere phrase : matiere, coloris, dimensions, poids.
     Chaque mention ne s'affiche que si le champ est rempli.

Rien d'autre n'est touche. Relancable sans risque : un
modele deja traite est ignore.

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

SECTION = "INTRO SEO"


PARAGRAPHE = (
    "\n\n        <p style=\"\n"
    "        margin:14px 0 0 0;\n"
    "        font-size:14px;\n"
    "        line-height:1.9;\n"
    "        color:#4b5563;\n"
    "        \">\n"
    "            {{#si_matiere}}Matière : {{matiere}}. {{/si_matiere}}"
    "{{#si_couleur}}Coloris : {{couleur}}. {{/si_couleur}}"
    "{{#si_dimensions}}Dimensions : {{dimensions}}. {{/si_dimensions}}"
    "{{#si_poids}}Poids : {{poids_lisible}}.{{/si_poids}}\n"
    "        </p>\n"
)


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
    Renvoie (html, True) si le modele a ete traite.
    """

    if "{{dimensions}}" in html:
        return html, False   # deja fait

    entete, morceaux = sections(html)

    if not morceaux:
        return html, False

    index = next(
        (i for i, (t, _) in enumerate(morceaux) if SECTION in t),
        None
    )

    if index is None:
        return html, False

    titre, texte = morceaux.pop(index)

    # Le paragraphe de donnees se glisse apres la premiere
    # phrase de l'intro.

    position = texte.find("</p>")

    if position != -1:
        coupe = position + len("</p>")
        texte = texte[:coupe] + PARAGRAPHE + texte[coupe:]

    morceaux.insert(0, (titre, texte))

    return entete + "".join(t for _, t in morceaux), True


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

    print("\n=== MODELES DIRECT FOURNISSEUR ===\n")

    prevus = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, fait = corriger(html)

        if not fait:
            continue

        _, morceaux = sections(nouveau_html)
        ordre = " > ".join(t[:14] for t, _ in morceaux[:4])

        print(f"   {modele['nom'][:36]:<38} {ordre}...")

        prevus.append((modele["id"], nouveau_html))

    if not prevus:
        print("\nRien a traiter.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a traiter.\n")

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

    print(f"\n{len(prevus)} modele(s) traite(s).\n")