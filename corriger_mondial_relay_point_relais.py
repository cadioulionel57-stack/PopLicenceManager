"""
Précise « Mondial Relay » en « Mondial Relay Point Relais »
dans la FAQ livraison des modèles de fiche.

Sans cette précision, deux lignes se suivent — « Mondial
Relay » puis « Mondial Relay Domicile » — sans qu'on
comprenne que la première désigne la livraison en point
relais.

Le libellé « Mondial Relay Domicile » n'est jamais touché :
le motif exige que le mot suivant soit « </strong> ».
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


# On ne vise QUE <strong>Mondial Relay</strong> — jamais
# <strong>Mondial Relay Domicile</strong>, dont le libellé
# ne se termine pas là.
MOTIF = re.compile(r"<strong>Mondial Relay</strong>")

APRES = "<strong>Mondial Relay Point Relais</strong>"


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

    a_faire = []

    for modele in modeles:

        nombre = len(MOTIF.findall(modele["html_template"] or ""))

        if nombre:
            a_faire.append({
                "id": modele["id"],
                "nom": modele["nom"],
                "html": modele["html_template"],
                "nombre": nombre,
            })

    print("\n=== LIBELLÉ À PRÉCISER ===\n")
    print("   avant : Mondial Relay")
    print("   après : Mondial Relay Point Relais\n")
    print("   (« Mondial Relay Domicile » n'est pas touché)\n")

    print("=== MODÈLES CONCERNÉS ===\n")

    if not a_faire:
        print("   Aucun. Rien à faire.\n")
        sys.exit(0)

    for ligne in a_faire:
        print(f"   {ligne['nom'][:48]:<50} {ligne['nombre']}")

    print(f"\n{len(a_faire)} modèle(s) concerné(s).\n")

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for ligne in a_faire:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (MOTIF.sub(APRES, ligne["html"]), ligne["id"])
        )

    print(f"\n{len(a_faire)} modèle(s) corrigé(s).\n")