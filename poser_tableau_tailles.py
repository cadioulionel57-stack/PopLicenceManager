r"""
poser_tableau_tailles.py
------------------------------------------------------------
Pose le tableau des tailles dans les modeles de fiche, juste
apres le texte propre au produit.

Le bloc est conditionnel : il ne s'affiche que si le produit
a des variations de taille reconnues. Un mug ne montrera
donc rien.
------------------------------------------------------------
"""

import sqlite3

BASE = "C:/PopLicenceManager/database/poplicence.db"

ANCRE = "{{/si_description_specifique}}"

BALISE = (
    "\n\n{{#si_tableau_tailles}}\n"
    "{{tableau_tailles}}\n"
    "{{/si_tableau_tailles}}\n"
)

connexion = sqlite3.connect(BASE)
connexion.row_factory = sqlite3.Row

lignes = connexion.execute(
    "SELECT id, nom, html_template FROM modeles_fiche_produit"
).fetchall()

a_poser = []
deja = []
sans_ancre = []

for ligne in lignes:

    html = ligne["html_template"] or ""

    if "{{tableau_tailles}}" in html:
        deja.append((ligne["id"], ligne["nom"]))
        continue

    if ANCRE not in html:
        sans_ancre.append((ligne["id"], ligne["nom"]))
        continue

    # Apres la DERNIERE occurrence, pour se placer a la fin
    # du texte produit et non au milieu.
    position = html.rfind(ANCRE) + len(ANCRE)

    nouveau = html[:position] + BALISE + html[position:]

    a_poser.append((ligne["id"], ligne["nom"], nouveau))

print("\n=== MODELES QUI RECEVRONT LE TABLEAU ===\n")
for identifiant, nom, _ in a_poser:
    print(f"   {identifiant:>3}  {nom}")

if deja:
    print("\n=== DEJA POSE, IGNORES ===\n")
    for identifiant, nom in deja:
        print(f"   {identifiant:>3}  {nom}")

if sans_ancre:
    print("\n=== SANS ANCRE, NON TRAITES ===\n")
    for identifiant, nom in sans_ancre:
        print(f"   {identifiant:>3}  {nom}")

print(f"\n{len(a_poser)} modeles a modifier.\n")

if not a_poser:
    raise SystemExit

reponse = input("Appliquer ? (tape oui) : ")

if reponse.strip().lower() not in ("oui", "o"):
    print("\nAnnule, rien n'a ete modifie.\n")
    raise SystemExit

for identifiant, _, nouveau in a_poser:
    connexion.execute(
        "UPDATE modeles_fiche_produit SET html_template = ? "
        "WHERE id = ?", (nouveau, identifiant)
    )

connexion.commit()
connexion.close()

print("\nFait.\n")