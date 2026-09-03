r"""
modules/pousser_finies.py
------------------------------------------------------------
Pousse vers WiziShop UNIQUEMENT les fiches qui sont :
  - actives
  - JAMAIS poussees (aucun identifiant WiziShop)
  - TERMINEES (pas d'encadre orange "A TERMINER")

    python -m modules.pousser_finies
    python -m modules.pousser_finies ID9 SAS
    python -m modules.pousser_finies WDK Groupe Partner

Sans nom de fournisseur, toutes les fiches finies et jamais
poussees sont proposees.
------------------------------------------------------------
"""

import sys

from modules.wizishop_produits import (
    PousseeProduits,
    WiziShopAPIError,
)


def liste(poussee, fournisseur=None):

    conditions = [
        "actif = 1",
        "CAST(IFNULL(id_wizishop, 0) AS INTEGER) = 0",
        "IFNULL(fiche_a_terminer, 0) = 0",
    ]

    parametres = []

    if fournisseur:

        lignes = poussee.connexion.execute(
            "SELECT id, nom FROM fournisseurs"
        ).fetchall()

        cherche = fournisseur.strip().lower()

        trouves = [
            l["id"] for l in lignes
            if (l["nom"] or "").strip().lower() == cherche
        ]

        if not trouves:

            connus = ", ".join(
                sorted((l["nom"] or "") for l in lignes)
            )

            raise ValueError(
                f"Fournisseur '{fournisseur}' introuvable.\n"
                f"Fournisseurs enregistres : {connus}"
            )

        marques = ",".join("?" for _ in trouves)

        conditions.append(f"fournisseur_id IN ({marques})")

        parametres.extend(trouves)

    requete = (
        "SELECT id, nom FROM produits WHERE "
        + " AND ".join(conditions)
        + " ORDER BY id"
    )

    return poussee.connexion.execute(
        requete, parametres
    ).fetchall()


if __name__ == "__main__":

    fournisseur = " ".join(sys.argv[1:]).strip() or None

    poussee = PousseeProduits()

    try:

        produits = liste(poussee, fournisseur)

        if not produits:
            print(
                "\nAucune fiche terminee en attente d'envoi.\n"
            )
            sys.exit(0)

        if fournisseur:
            print(f"\nFOURNISSEUR : {fournisseur}")

        print(
            f"\n{len(produits)} fiche(s) TERMINEE(S) et "
            f"jamais poussee(s) :\n"
        )

        for ligne in produits:
            print(f"   {ligne['id']:>3}  {ligne['nom'][:60]}")

        reponse = input(
            "\nEnvoyer vers WiziShop ? (tape oui) : "
        )

        if reponse.strip().lower() not in ("oui", "o"):
            print("\nAnnule.\n")
            sys.exit(0)

        print()

        conformes = 0
        autres = []
        echecs = []

        for ligne in produits:

            identifiant = ligne["id"]

            try:
                fait, id_ws, avertissements, etat = (
                    poussee.pousser(identifiant)
                )

            except Exception as erreur:
                print(
                    f"   {identifiant:>3}  ECHEC : {erreur}"
                )
                echecs.append(identifiant)
                continue

            print(
                f"   {identifiant:>3}  {str(fait):<9} "
                f"WiziShop {str(id_ws):<6} etat {etat}"
            )

            if etat == "draft":
                conformes += 1
            else:
                autres.append((identifiant, etat))

            for texte in avertissements:
                print(f"        - {texte}")

        print(
            f"\n{conformes} fiche(s) arrivees EN BROUILLON."
        )

        if autres:
            print("\nATTENTION, etat inattendu :")
            for identifiant, etat in autres:
                print(f"   {identifiant} : {etat}")

        if echecs:
            print(f"\n{len(echecs)} echec(s) : {echecs}")

        print()

    except (ValueError, WiziShopAPIError) as erreur:
        print(f"\nErreur : {erreur}\n")