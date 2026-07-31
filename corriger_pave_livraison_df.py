"""
Corrige UNE SEULE PHRASE dans le pavé jaune « Optimisez
votre livraison » : celle qui annonce un tarif Direct
Fournisseur.

Le port fournisseur étant désormais inclus dans le prix de
vente, la livraison est offerte sans minimum d'achat.

Ce script ne touche à RIEN d'autre : ni les tarifs des
transporteurs, ni le reste du pavé, ni les autres sections
du modèle.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


AVANT = (
    "sous 5 à 7 jours ouvrés, pour {{tarif_livraison_df}}€ TTC "
    "(offert dès {{seuil_livraison_gratuite_df}}€ d'achats)."
)

APRES = (
    "sous 5 à 7 jours ouvrés. <strong>Livraison offerte, "
    "sans minimum d'achat.</strong>"
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

    a_faire = [
        m for m in modeles
        if AVANT in (m["html_template"] or "")
    ]

    print("\n=== PHRASE À CORRIGER ===\n")
    print(f"   avant : ...{AVANT}")
    print(f"   après : ...{APRES}\n")

    print("=== MODÈLES CONCERNÉS ===\n")

    if not a_faire:
        print("   Aucun. Rien à faire.\n")
        sys.exit(0)

    for modele in a_faire:
        print(f"   {modele['nom']}")

    print(f"\n{len(a_faire)} modèle(s) concerné(s).\n")

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for modele in a_faire:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (modele["html_template"].replace(AVANT, APRES),
             modele["id"])
        )

    print(f"\n{len(a_faire)} modèle(s) corrigé(s).\n")

    # Ce qui mentionne encore un tarif DF, sous une forme que
    # le script n'a pas su traiter.
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
            "Fournisseur ailleurs — à vérifier à la main :\n"
        )

        for modele in restants:
            print(f"   {modele['nom']}")

    else:
        print("Plus aucune mention de tarif Direct Fournisseur.")