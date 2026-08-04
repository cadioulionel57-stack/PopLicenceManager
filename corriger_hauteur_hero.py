r"""
corriger_hauteur_hero.py  (4e version)
------------------------------------------------------------
Pose la PHRASE D'ACCROCHE en tete de chaque modele de fiche.

Cette phrase complete la description courte du produit, apres
le poids et le format :

    Sac a dos enfant Bluey sous licence officielle : 240 g,
    format 30 x 15,5 x 10 cm, TAILLE POUR LES JOURNEES
    D'ECOLE, DES PETITS COMME DES PLUS GRANDS.

Elle est propre a la FAMILLE de produit, jamais au produit
lui-meme : on l'ecrit donc une fois par modele, et tous les
produits qui l'utilisent en beneficient.

Un modele qui en possede deja une n'est PAS touche : la
phrase ecrite a la main l'emporte toujours.

Usage :
    python corriger_hauteur_hero.py
------------------------------------------------------------
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


# L'ordre compte : le premier mot-cle trouve dans le nom du
# modele gagne. Les familles precises passent donc AVANT le
# Noel generique.

ACCROCHES = [
    ("playmobil", "de quoi inventer des heures d'histoires"),
    ("lego", "brique après brique, l'univers prend forme"),
    ("jeux et jouets", "de quoi occuper les après-midi de pluie"),
    ("cartes a collectionner",
     "à collectionner, échanger et compléter"),
    ("cartables", "taillé pour les journées d'école, "
                  "des petits comme des plus grands"),
    ("chaussures", "pour garder les pieds au chaud toute l'année"),
    ("textile", "à porter tous les jours sans s'en lasser"),
    ("vetements", "à porter tous les jours sans s'en lasser"),
    ("peluches", "douce, câline, et prête à ne plus quitter les bras"),
    ("funko", "la figurine que les collectionneurs s'arrachent"),
    ("figurines", "à poser sur une étagère et à admirer longtemps"),
    ("mugs", "pour commencer la journée du bon pied"),
    ("linge de maison",
     "pour des nuits dans l'univers préféré des enfants"),
    ("decoration", "de quoi transformer une chambre "
                   "en véritable univers"),
    ("papeterie", "de quoi rendre les devoirs un peu plus gais"),
    ("univers bebe",
     "pensé pour les tout-petits, doux et facile à entretenir"),
    ("mobilier enfant", "pour aménager une chambre à son image"),
    ("electronique", "l'univers préféré des enfants jusque dans "
                     "les objets du quotidien"),
    ("noel", "à glisser sous le sapin"),
]


def accroche_pour(nom_modele):

    sans_accents = (
        nom_modele.lower()
        .replace("é", "e").replace("è", "e").replace("ê", "e")
        .replace("à", "a").replace("ô", "o").replace("û", "u")
    )

    for mot_cle, phrase in ACCROCHES:
        if mot_cle in sans_accents:
            return phrase

    return None


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

    print("\n=== PHRASES D'ACCROCHE ===\n")

    prevus = []
    sans = []

    for modele in modeles:

        html = modele["html_template"]

        if "ACCROCHE" in html:
            continue

        phrase = accroche_pour(modele["nom"])

        if phrase is None:
            sans.append(modele["nom"])
            continue

        nouveau_html = f"<!-- ACCROCHE: {phrase} -->\n\n" + html

        print(f"   {modele['nom'][:38]:<40} {phrase}")

        prevus.append((modele["id"], nouveau_html))

    if sans:
        print(
            "\n/!\\ AUCUNE PHRASE TROUVEE pour :\n   "
            + "\n   ".join(sans) + "\n"
        )

    if not prevus:
        print("\nRien a poser.\n")
        sys.exit(0)

    print(f"\n{len(prevus)} modele(s) a completer.\n")

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

    print(f"\n{len(prevus)} modele(s) complete(s).\n")