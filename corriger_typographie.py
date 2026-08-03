"""
Remplace les caractères que WiziShop n'accepte pas dans un
bloc Code HTML par leur équivalent sûr.

WiziShop échappe tout caractère hors Latin-1 : collé tel
quel, un euro s'affiche « \u20ac » au lieu de « € ».

Cinq caractères sont traités, et cinq seulement :

    €  ->  &#8364;      (entité HTML de l'euro)
    •  ->  &#8226;      (entité HTML de la puce)
    —  ->  -            (tiret long)
    –  ->  -            (tiret moyen)
    œ  ->  oe           (ligature)

Les lettres accentuées (é è à ê ç ù) sont dans Latin-1 et
ne sont PAS touchées : elles s'affichent correctement et
doivent rester lisibles pour pouvoir éditer les textes.

Les emojis ne sont pas traités ici, ils font l'objet d'un
script séparé.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


REMPLACEMENTS = [
    ("€", "&#8364;"),
    ("•", "&#8226;"),
    ("—", "-"),
    ("–", "-"),
    ("œ", "oe"),
    ("Œ", "OE"),
]

VARIABLE = re.compile(r"\{\{[#/]?[a-zA-Z0-9_]+\}\}")


def compter_variables(html):
    """
    Nombre de variables et de marqueurs conditionnels.
    Sert de garde-fou : ce nombre ne doit jamais changer.
    """

    return len(VARIABLE.findall(html))


def corriger(html):

    total = 0

    for avant, apres in REMPLACEMENTS:

        nombre = html.count(avant)

        if nombre:
            html = html.replace(avant, apres)
            total += nombre

    return html, total


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

    print("\n=== CARACTÈRES À REMPLACER ===\n")

    prevus = []
    total_general = 0
    alerte = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, nombre = corriger(html)

        if not nombre:
            continue

        # Garde-fou : les variables doivent être intactes.

        avant_var = compter_variables(html)
        apres_var = compter_variables(nouveau_html)

        if avant_var != apres_var:
            alerte.append(modele["nom"])
            continue

        detail = " ".join(
            f"{c}x{html.count(c)}"
            for c, _ in REMPLACEMENTS
            if html.count(c)
        )

        print(
            f"   {modele['nom'][:40]:<42} "
            f"{nombre:>4}   {detail}"
        )

        prevus.append((modele["id"], nouveau_html))
        total_general += nombre

    if alerte:
        print(
            "\n/!\\ ÉCARTÉS, le nombre de variables changeait :"
            "\n   " + "\n   ".join(alerte) + "\n"
        )

    if not prevus:
        print("\nRien à corriger.\n")
        sys.exit(0)

    print(
        f"\n{len(prevus)} modèle(s) concerné(s), "
        f"{total_general} caractère(s) à remplacer.\n"
    )

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for modele_id, nouveau_html in prevus:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (nouveau_html, modele_id)
        )

    print(f"\n{len(prevus)} modèle(s) corrigé(s).\n")

    # Contrôle final sur la base relue.

    apres = db.lire(
        """
        SELECT nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        """
    )

    restant = sum(
        ligne["html_template"].count(c)
        for ligne in apres
        for c, _ in REMPLACEMENTS
    )

    if restant:
        print(f"Il reste {restant} caractère(s) non traité(s).\n")
    else:
        print(
            "Plus aucun euro, puce, tiret long ou ligature "
            "à problème dans les modèles.\n"
        )