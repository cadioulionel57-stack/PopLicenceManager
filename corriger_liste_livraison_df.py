"""
Corrige la liste « Livraison partenaire sécurisée » des
fiches Direct Fournisseur.

Les deux lignes qui annoncent un tarif et un seuil :

    <li>Tarif livraison : {{tarif_livraison_df}}€ TTC</li>
    <li>Livraison OFFERTE dès {{seuil_livraison_gratuite_df}}€ d'achats</li>

sont remplacées par une seule :

    <li><strong>Livraison offerte, sans minimum d'achat</strong></li>

Rien d'autre n'est touché : ni les autres puces de la liste,
ni le reste du modèle.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


# Les deux <li> peuvent être séparés par n'importe quelle
# indentation selon le modèle : on l'accepte telle quelle.
MOTIF = re.compile(
    r"<li>\s*Tarif livraison\s*:\s*\{\{tarif_livraison_df\}\}€ TTC\s*</li>"
    r"\s*"
    r"<li>\s*Livraison OFFERTE dès\s*"
    r"\{\{seuil_livraison_gratuite_df\}\}€ d'achats\s*</li>"
)

APRES = (
    "<li><strong>Livraison offerte, sans minimum "
    "d'achat</strong></li>"
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

    print("\n=== LIGNES À REMPLACER ===\n")
    print("   <li>Tarif livraison : ...€ TTC</li>")
    print("   <li>Livraison OFFERTE dès ...€ d'achats</li>\n")
    print("   deviennent\n")
    print(f"   {APRES}\n")

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