r"""
remonter_description.py  (8e version)
------------------------------------------------------------
Transforme la BANNIERE UNIVERS en vraie image.

Jusqu'ici la photo etait posee en fond decoratif (CSS).
Pour Google elle n'existait pas : pas d'indexation, pas de
texte alternatif, aucun poids dans la page.

Le script la remplace par une vraie balise image, avec :

  - un texte alternatif qui reprend le nom du produit et sa
    licence, fabrique par le logiciel ;
  - le voile de couleur conserve par-dessus, en calque ;
  - le texte de la banniere au-dessus du tout.

Si le produit n'a pas d'image d'ambiance, la banniere garde
simplement son fond colore : pas d'image cassee.

Relancable sans risque.

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

# Le fond de la banniere : un degrade suivi de l'image.
FOND = re.compile(
    r"background:\s*(linear-gradient\(.*?\)),\s*"
    r"url\('\{\{image_fond_univers\}\}'\)[^;]*;",
    re.S,
)


IMAGE = (
    "\n\n  {{#si_image_univers}}\n"
    "  <img src=\"{{image_fond_univers}}\"\n"
    "       alt=\"{{alt_univers}}\"\n"
    "       loading=\"lazy\"\n"
    "       decoding=\"async\"\n"
    "       style=\"\n"
    "       position:absolute;\n"
    "       top:0; left:0;\n"
    "       width:100%; height:100%;\n"
    "       object-fit:cover;\n"
    "       z-index:0;\n"
    "       \">\n"
    "  <div style=\"\n"
    "  position:absolute;\n"
    "  top:0; left:0;\n"
    "  width:100%; height:100%;\n"
    "  background:VOILE;\n"
    "  z-index:1;\n"
    "  \"></div>\n"
    "  {{/si_image_univers}}\n"
    "  <div style=\"position:relative; z-index:2;\">\n"
)


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


def transformer(texte):
    """
    Renvoie (texte, True) si la banniere a ete transformee.
    """

    if "{{alt_univers}}" in texte:
        return texte, False

    trouve = FOND.search(texte)

    if not trouve:
        return texte, False

    voile = re.sub(r"\s+", " ", trouve.group(1)).strip()

    # 1. Le fond du cadre ne garde que le degrade, sans
    #    l'image : elle devient une vraie balise.
    texte = (
        texte[:trouve.start()]
        + f"background:{voile};\nposition:relative;\noverflow:hidden;"
        + texte[trouve.end():]
    )

    # 2. On insere l'image, le voile en calque, et on ouvre
    #    le cadre qui portera le texte au-dessus.
    ouverture = texte.find(">", texte.find("<div style="))

    if ouverture == -1:
        return texte, False

    bloc = IMAGE.replace("VOILE", voile)

    texte = texte[:ouverture + 1] + bloc + texte[ouverture + 1:]

    # 3. On referme ce cadre juste avant la fin du bloc.
    fin = texte.rfind("</div>")

    if fin == -1:
        return texte, False

    texte = texte[:fin] + "</div>\n  " + texte[fin:]

    return texte, True


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

    print("\n=== BANNIERE UNIVERS EN VRAIE IMAGE ===\n")

    prevus = []

    for modele in modeles:

        entete, morceaux = sections(modele["html_template"])

        if not morceaux:
            continue

        fait = False
        resultat = []

        for titre, texte in morceaux:

            if "UNIVERS PRODUIT" in titre:
                texte, change = transformer(texte)
                fait = fait or change

            resultat.append((titre, texte))

        if not fait:
            continue

        print(f"   {modele['nom'][:46]}")

        prevus.append(
            (modele["id"], entete + "".join(t for _, t in resultat))
        )

    if not prevus:
        print("\nRien a transformer.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a transformer.\n")

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

    print(f"\n{len(prevus)} modele(s) transforme(s).\n")