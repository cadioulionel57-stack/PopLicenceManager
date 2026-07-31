"""
Remplace UNIQUEMENT le bandeau bleu de tarif en haut des
fiches Direct Fournisseur.

Le port fournisseur étant désormais inclus dans le prix de
vente, la livraison est offerte sans minimum d'achat.

Ce script ne touche à RIEN d'autre :
  - une seule ligne remplacée par modèle
  - uniquement les modèles rattachés au type
    « dropshipping » (Direct Fournisseur)
  - les modèles Stock, Précommande et Bundle ne sont
    jamais lus ni modifiés
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


AVANT = (
    "🚚 Livraison : {{tarif_livraison_df}}€ TTC • OFFERTE DÈS "
    "{{seuil_livraison_gratuite_df}}€ D'ACHATS"
)

APRES = "🚚 LIVRAISON OFFERTE • SANS MINIMUM D'ACHAT"


def modeles_direct_fournisseur(db):
    """
    Uniquement les modèles qui couvrent le type
    « dropshipping ». Aucun autre n'est retourné.
    """

    return db.lire(
        """
        SELECT DISTINCT m.id, m.nom, m.html_template
        FROM modeles_fiche_produit m
        INNER JOIN modeles_fiche_types t
            ON t.modele_id = m.id
           AND t.type_produit = 'dropshipping'
        WHERE m.html_template IS NOT NULL
        ORDER BY m.nom
        """
    )


if __name__ == "__main__":

    db = Database()

    modeles = modeles_direct_fournisseur(db)

    concernes = [
        m for m in modeles
        if AVANT in (m["html_template"] or "")
    ]

    print("\n=== MODÈLES DIRECT FOURNISSEUR ===\n")

    for modele in modeles:

        nombre = (modele["html_template"] or "").count(AVANT)

        etat = (
            f"{nombre} bandeau à corriger"
            if nombre else "bandeau déjà corrigé ou absent"
        )

        print(f"   {modele['nom'][:48]:<50} {etat}")

    if not concernes:
        print("\nAucun bandeau à corriger. Rien à faire.\n")
        sys.exit(0)

    print(
        f"\n{len(concernes)} modèle(s) à corriger.\n"
        f"\nLigne remplacée :\n"
        f"   avant : {AVANT}\n"
        f"   après : {APRES}\n"
    )

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for modele in concernes:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (modele["html_template"].replace(AVANT, APRES),
             modele["id"])
        )

    print(f"\n{len(concernes)} modèle(s) corrigé(s).\n")