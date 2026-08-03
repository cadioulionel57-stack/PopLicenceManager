r"""
corriger_hauteur_hero.py
------------------------------------------------------------
Corrige la banniere de couleur qui s'etire sur toute la
hauteur de la fiche produit.

Le haut de la fiche est une grille a deux colonnes : la
banniere d'etat et le bloc emballage cadeau. Par defaut, une
grille CSS donne a toutes ses colonnes la hauteur de la plus
grande. Le bloc cadeau faisant pres de 8000 caracteres, la
banniere s'etirait pour l'egaler.

La correction ajoute UNE seule propriete, align-items:start,
qui laisse chaque colonne a sa hauteur naturelle.
------------------------------------------------------------
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


GRILLE_HERO = re.compile(
    r'(<section style="[^"]*?minmax\(280px,1fr\)[^"]*?'
    r'margin-bottom:28px;\s*)(">)',
    re.S,
)

VARIABLE = re.compile(r"\{\{[#/]?[a-zA-Z0-9_]+\}\}")


def compter_variables(html):
    return len(VARIABLE.findall(html))


def corriger(html):

    nombre = 0

    def remplacer(m):
        nonlocal nombre
        if "align-items" in m.group(1):
            return m.group(0)
        nombre += 1
        return m.group(1) + "align-items:start;\n    " + m.group(2)

    return GRILLE_HERO.sub(remplacer, html), nombre


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

    print("\n=== GRILLE DU HAUT DE FICHE ===\n")

    prevus = []
    alerte = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, nombre = corriger(html)

        if not nombre:
            continue

        if compter_variables(html) != compter_variables(nouveau_html):
            alerte.append(modele["nom"])
            continue

        print(f"   {modele['nom'][:44]:<46} {nombre} grille(s)")

        prevus.append((modele["id"], nouveau_html))

    if alerte:
        print(
            "\n/!\\ ECARTES, le nombre de variables changeait :"
            "\n   " + "\n   ".join(alerte) + "\n"
        )

    if not prevus:
        print("\nRien a corriger.\n")
        sys.exit(0)

    print(
        f"\n{len(prevus)} modele(s) a corriger.\n"
        f"\nPropriete ajoutee : align-items:start;\n"
    )

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

    restant = sum(
        1
        for ligne in apres
        for m in GRILLE_HERO.finditer(ligne["html_template"])
        if "align-items" not in m.group(1)
    )

    variables = sum(
        compter_variables(l["html_template"]) for l in apres
    )

    print(f"Variables et blocs conditionnels : {variables}\n")

    if restant:
        print(f"Il reste {restant} grille(s) non corrigee(s).\n")
    else:
        print("Toutes les grilles du haut de fiche sont corrigees.\n")