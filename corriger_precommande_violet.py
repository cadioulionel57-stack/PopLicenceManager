"""
Passe le modèle « Template SITE PRECOMMANDE » du bleu au
violet prune.

Le bleu de ce modèle est exactement celui du Direct
Fournisseur : un client ne distingue pas les deux. Le violet
n'est utilisé nulle part ailleurs sur la boutique, la fiche
précommande devient donc immédiatement reconnaissable.

CE SCRIPT NE TOUCHE QU'UN SEUL MODÈLE. Les mêmes codes
couleur existent dans d'autres modèles, où ils sont
légitimes : ils ne sont ni lus ni modifiés.

Ce qui change :

    bandeau du haut      bleu dégradé  ->  prune dégradé
    date de sortie       bleu          ->  violet
    trait vertical       bleu          ->  violet
    encadré information  bleu clair    ->  violet clair
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


MODELE = "Template SITE PRECOMMANDE"

# L'ordre compte : le dégradé complet d'abord, sinon les
# remplacements de couleurs simples l'auraient déjà entamé.
REMPLACEMENTS = [
    ("linear-gradient(135deg,#1d4ed8,#1e3a8a)",
     "linear-gradient(135deg,#581C87,#9333EA)"),

    ("#1d4ed8", "#7E22CE"),   # date de sortie, trait vertical
    ("#1e3a8a", "#581C87"),   # textes de l'encadré
    ("#eff6ff", "#faf5ff"),   # fond de l'encadré
    ("#93c5fd", "#d8b4fe"),   # bordure de l'encadré
    ("rgba(29,78,216", "rgba(126,34,206"),   # ombres portées
]


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

    modele = db.lire_un(
        "SELECT id, nom, html_template "
        "FROM modeles_fiche_produit WHERE nom = ?",
        (MODELE,)
    )

    if not modele:
        print(f"\nModèle « {MODELE} » introuvable.\n")
        sys.exit(0)

    html = modele["html_template"]

    nouveau_html, total = corriger(html)

    if not total:
        print("\nCe modèle est déjà en violet. Rien à faire.\n")
        sys.exit(0)

    print(f"\n=== {modele['nom']} ===\n")

    # On simule dans l'ordre pour afficher le nombre réel
    # de remplacements de chaque ligne.
    provisoire = html

    for avant, apres in REMPLACEMENTS:
        nombre = provisoire.count(avant)
        if nombre:
            print(f"   {avant:<42} -> {apres:<42} x{nombre}")
            provisoire = provisoire.replace(avant, apres)

    print(f"\n{total} remplacement(s) sur ce seul modèle.\n")

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    db.executer(
        "UPDATE modeles_fiche_produit "
        "SET html_template = ? WHERE id = ?",
        (nouveau_html, modele["id"])
    )

    verif = db.lire_un(
        "SELECT html_template FROM modeles_fiche_produit "
        "WHERE id = ?",
        (modele["id"],)
    )

    reste = sum(
        verif["html_template"].count(a)
        for a, _ in REMPLACEMENTS
    )

    print("\nModèle corrigé.\n")

    if reste:
        print(f"Il reste {reste} couleur(s) bleue(s).\n")
    else:
        print("Plus aucun bleu sur la fiche précommande.\n")