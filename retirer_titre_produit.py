r"""
retirer_titre_produit.py
------------------------------------------------------------
WiziShop affiche deja le nom du produit en titre au-dessus
de la fiche. Tout titre du modele qui le repete est un
doublon : on le RETIRE.

Exception : les titres de BANNIERE, reconnaissables au
span blanc pose le 05/08/2026. Eux restent.
------------------------------------------------------------
"""

import re
import sqlite3

BASE = "C:/PopLicenceManager/database/poplicence.db"

connexion = sqlite3.connect(BASE)
connexion.row_factory = sqlite3.Row

MOTIF = re.compile(
    r"[ \t]*<(h[1-6])[^>]*>((?:(?!</h).)*?\{\{nom_produit\}\}"
    r"(?:(?!</h).)*)</h[1-6]>[ \t]*\n?",
    re.S | re.I,
)

def sans_balises(texte):
    return re.sub("<[^>]+>", "", texte).replace("\n", " ").strip()

lignes = connexion.execute(
    "SELECT id, nom, html_template FROM modeles_fiche_produit"
).fetchall()

retires = []
gardes = []
modifications = []

for ligne in lignes:

    html = ligne["html_template"]

    if not MOTIF.search(html):
        continue

    def traite(trouve):
        bloc = trouve.group(0)
        if "#ffffff" in bloc.lower() or "#fff" in bloc.lower():
            gardes.append((ligne["id"], sans_balises(trouve.group(2))[:50]))
            return bloc
        retires.append((ligne["id"], sans_balises(trouve.group(2))[:50]))
        return ""

    nouveau = MOTIF.sub(traite, html)

    if nouveau != html:
        modifications.append((ligne["id"], nouveau))

print("\n=== TITRES QUI SERONT RETIRES ===\n")
for identifiant, texte in retires:
    print(f"   {identifiant:>3}  {texte}")

print("\n=== TITRES DE BANNIERE CONSERVES ===\n")
for identifiant, texte in gardes:
    print(f"   {identifiant:>3}  {texte}")

print(
    f"\n{len(retires)} titres retires, {len(gardes)} conserves, "
    f"sur {len(modifications)} modeles.\n"
)

if not modifications:
    raise SystemExit

reponse = input("Appliquer ? (tape oui) : ")

if reponse.strip().lower() not in ("oui", "o"):
    print("\nAnnule, rien n'a ete modifie.\n")
    raise SystemExit

for identifiant, nouveau in modifications:
    connexion.execute(
        "UPDATE modeles_fiche_produit SET html_template = ? "
        "WHERE id = ?", (nouveau, identifiant)
    )

connexion.commit()
connexion.close()

print("\nFait.\n")