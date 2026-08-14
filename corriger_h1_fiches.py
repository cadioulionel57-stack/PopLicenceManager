r"""
corriger_h1_fiches.py
------------------------------------------------------------
Un seul H1 par page. WiziShop affiche deja le nom du produit
en H1 : un modele de fiche qui en remet un cree un doublon.

Ce script ne touche QUE les H1 contenant {{nom_produit}}.
Les pages autonomes (CGV, guide des tailles) gardent le leur.
------------------------------------------------------------
"""

import re
import sqlite3

BASE = "C:/PopLicenceManager/database/poplicence.db"

connexion = sqlite3.connect(BASE)
connexion.row_factory = sqlite3.Row

lignes = connexion.execute(
    "SELECT id, nom, html_template FROM modeles_fiche_produit "
    "WHERE html_template LIKE ?", ("%<h1%",)
).fetchall()

MOTIF = re.compile(r"<h1(\s[^>]*)?>(.*?)</h1>", re.S | re.I)

a_corriger = []

for ligne in lignes:

    html = ligne["html_template"]

    def remplace(trouve):
        if "{{nom_produit}}" in trouve.group(2):
            return f"<h2{trouve.group(1) or ''}>{trouve.group(2)}</h2>"
        return trouve.group(0)

    nouveau = MOTIF.sub(remplace, html)

    if nouveau != html:
        a_corriger.append((ligne["id"], ligne["nom"], nouveau))

if not a_corriger:
    print("\nAucun modele a corriger.\n")
    raise SystemExit

print("\n=== MODELES A CORRIGER ===\n")

for identifiant, nom, _ in a_corriger:
    print(f"   {identifiant:>3}  {nom}")

print(f"\n{len(a_corriger)} modeles. Les autres gardent leur H1.\n")

reponse = input("Appliquer la correction ? (tape oui) : ")

if reponse.strip().lower() not in ("oui", "o"):
    print("\nAnnule, rien n'a ete modifie.\n")
    raise SystemExit

for identifiant, _, nouveau in a_corriger:
    connexion.execute(
        "UPDATE modeles_fiche_produit SET html_template = ? "
        "WHERE id = ?", (nouveau, identifiant)
    )

connexion.commit()
connexion.close()

print("\nCorrection appliquee.\n")