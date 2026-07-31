"""
Corrige le badge de rassurance des fiches Direct
Fournisseur :

    🚚 Livraison offerte dès {{seuil_livraison_gratuite_df}}€

devient

    🚚 Livraison offerte

C'est la dernière mention de seuil dans ces modèles.
Rien d'autre n'est touché.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


# L'espace avant le « € » varie selon les modèles : on
# l'accepte tel quel.
MOTIF = re.compile(
    r"🚚 Livraison offerte dès\s*"
    r"\{\{seuil_livraison_gratuite_df\}\}\s*€"
)

APRES = "🚚 Livraison offerte"


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
            })

    print("\n=== BADGE À CORRIGER ===\n")
    print("   avant : 🚚 Livraison offerte dès ...€")
    print(f"   après : {APRES}\n")

    print("=== MODÈLES CONCERNÉS ===\n")

    if not a_faire:
        print("   Aucun. Rien à faire.\n")
        sys.exit(0)

    for ligne in a_faire:
        print(f"   {ligne['nom']}")

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

    restants = db.lire(
        """
        SELECT nom
        FROM modeles_fiche_produit
        WHERE html_template LIKE '%tarif_livraison_df%'
           OR html_template LIKE '%seuil_livraison_gratuite_df%'
        ORDER BY nom
        """
    )

    if restants:

        print(
            "⚠ Ces modèles mentionnent encore un tarif Direct "
            "Fournisseur ailleurs :\n"
        )

        for modele in restants:
            print(f"   {modele['nom']}")

    else:
        print("Plus aucune mention de tarif Direct Fournisseur.")