"""
Remplace « Colissimo sans signature » par « Mondial Relay
Domicile » dans les modèles de fiche, et ajoute le délai de
livraison juste après.

Ce script fait DEUX choses, et rien d'autre :
  1. le libellé <strong>Colissimo sans signature</strong>
     devient <strong>Mondial Relay Domicile</strong>
  2. le paragraphe de délai est inséré après la ligne
     « offert dès ...€ d'achats. » qui suit ce libellé

Les tarifs eux-mêmes ne bougent pas : ils restent portés
par {{tarif_colissimo}} et {{seuil_colissimo}}, qui
contiennent déjà les bons montants.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


LIBELLE_AVANT = "<strong>Colissimo sans signature</strong>"
LIBELLE_APRES = "<strong>Mondial Relay Domicile</strong>"

# Ligne repère après laquelle on insère le délai.
REPERE = "offert dès {{seuil_colissimo}}€ d'achats."

DELAI = (
    "\n\n                <br><br>\n\n"
    "                Le délai de livraison à domicile par "
    "Mondial Relay\n"
    "                en France métropolitaine est estimé à 3 "
    "à 5 jours\n"
    "                ouvrés à partir de la prise en charge du "
    "colis.\n"
    "                Ce service s'effectue généralement du "
    "lundi au samedi."
)


def corriger(html):
    """
    Renvoie (html_corrigé, libellés_remplacés, délais_ajoutés).
    """

    libelles = html.count(LIBELLE_AVANT)

    html = html.replace(LIBELLE_AVANT, LIBELLE_APRES)

    # On n'ajoute le délai que s'il n'y est pas déjà, pour
    # pouvoir relancer le script sans le dupliquer.
    delais = 0

    if (
        REPERE in html
        and "par Mondial Relay" not in html
    ):
        html = html.replace(REPERE, REPERE + DELAI, 1)
        delais = 1

    return html, libelles, delais


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

        html = modele["html_template"] or ""

        _, libelles, delais = corriger(html)

        if libelles or delais:
            a_faire.append({
                "id": modele["id"],
                "nom": modele["nom"],
                "libelles": libelles,
                "delais": delais,
            })

    print("\n=== MODÈLES À CORRIGER ===\n")

    if not a_faire:
        print("   Aucun. Rien à faire.\n")
        sys.exit(0)

    for ligne in a_faire:
        print(
            f"   {ligne['nom'][:48]:<50} "
            f"{ligne['libelles']} libellé(s), "
            f"{ligne['delais']} délai(s) à ajouter"
        )

    print(f"\n{len(a_faire)} modèle(s) concerné(s).\n")

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for ligne in a_faire:

        modele = db.lire_un(
            "SELECT html_template FROM modeles_fiche_produit "
            "WHERE id = ?",
            (ligne["id"],)
        )

        corrige, _, _ = corriger(modele["html_template"])

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (corrige, ligne["id"])
        )

    print(f"\n{len(a_faire)} modèle(s) corrigé(s).\n")

    # Ce qui mentionne encore Colissimo, sous une forme que
    # le script n'a pas su traiter.
    restants = db.lire(
        """
        SELECT nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template LIKE '%Colissimo%'
        ORDER BY nom
        """
    )

    if restants:

        print(
            "⚠ Ces modèles mentionnent encore « Colissimo » "
            "sous une forme inconnue — à vérifier à la main :\n"
        )

        for modele in restants:
            print(f"   {modele['nom']}")

    else:
        print("Plus aucune mention de Colissimo dans les modèles.")