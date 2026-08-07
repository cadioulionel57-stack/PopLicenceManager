r"""
remonter_description.py  (18e version)
------------------------------------------------------------
Deux corrections.

  1. LE TITRE DE LA BANNIERE UNIVERS reste noir chez
     WiziShop. La couleur etait posee sur la balise du titre
     avec une priorite maximale, et leur editeur la retire au
     passage.

     On la met donc SUR LE TEXTE LUI-MEME, dans une balise
     qui lui appartient. Une regle de theme qui vise les
     titres ne peut plus l'atteindre.

  2. LA BANNIERE PRECOMMANDE remonte TOUT EN HAUT, juste
     au-dessus de la description.

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

TITRE = re.compile(r"(<h[1-6][^>]*>)(.*?)(</h[1-6]>)", re.S)


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


def blanchir_titres(texte):
    """
    Entoure le texte de chaque titre d'une balise qui porte
    la couleur blanche. Renvoie (texte, nombre traite).
    """

    nombre = 0

    def remplacer(m):

        nonlocal nombre

        ouverture, contenu, fermeture = m.group(1), m.group(2), m.group(3)

        if "color:#ffffff" in contenu:
            return m.group(0)

        nombre += 1

        return (
            ouverture
            + '<span style="color:#ffffff">'
            + contenu.strip()
            + "</span>"
            + fermeture
        )

    return TITRE.sub(remplacer, texte), nombre


def corriger(nom_modele, html):
    """
    Renvoie (html, titres_traites, banniere_remontee).
    """

    entete, morceaux = sections(html)

    if not morceaux:
        return html, 0, False

    total = 0
    resultat = []

    for titre, texte in morceaux:

        if "UNIVERS PRODUIT" in titre:
            texte, nombre = blanchir_titres(texte)
            total += nombre

        resultat.append((titre, texte))

    remontee = False

    if "PRECOMMANDE" in nom_modele.upper():

        index = next(
            (i for i, (t, _) in enumerate(resultat) if "BADGE" in t),
            None
        )

        if index is not None and index != 0:
            resultat.insert(0, resultat.pop(index))
            remontee = True

    if not (total or remontee):
        return html, 0, False

    return (
        entete + "".join(t for _, t in resultat),
        total,
        remontee,
    )


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

    print("\n=== TITRES BLANCS ET BANNIERE PRECOMMANDE ===\n")

    prevus = []

    for modele in modeles:

        nouveau_html, total, remontee = corriger(
            modele["nom"], modele["html_template"]
        )

        if not (total or remontee):
            continue

        detail = []

        if total:
            detail.append(f"{total} titre(s) en blanc")

        if remontee:
            detail.append("banniere precommande remontee en tete")

        print(f"   {modele['nom'][:38]:<40} {', '.join(detail)}")

        prevus.append((modele["id"], nouveau_html))

    if not prevus:
        print("\nRien a corriger.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a corriger.\n")

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

    casses = sum(
        1 for l in apres
        if l["html_template"].count("<div")
        != l["html_template"].count("</div>")
    )

    print(f"Modeles au cadre mal ferme : {casses}\n")