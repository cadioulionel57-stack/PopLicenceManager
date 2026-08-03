"""
Retire la mention « Direct Fournisseur » de TOUS les modèles
de fiche produit et la remplace par « Livraison sous 5 à 7
jours ouvrés ».

Sept formulations sont traitées, et sept seulement. Le script
ne touche à rien d'autre : ni les couleurs, ni les bandeaux,
ni les tarifs, ni les autres textes.

Les modèles qui ne contiennent aucune de ces formulations ne
sont ni lus ni modifiés.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.database import Database


NOUVEAU = "Livraison sous 5 à 7 jours ouvrés"


# Chaque entrée : (texte recherché, texte de remplacement)
# L'ordre compte : les formulations longues d'abord, pour
# qu'une formulation courte ne vienne pas les amputer.
REMPLACEMENTS = [

    # 6 - modèle TARIF FRAIS DE PORT
    (
        'Les produits <strong>"Direct Fournisseur"</strong> '
        '(bandeau bleu en haut de la fiche produit) sont '
        'expédiés sous 24h et livrés en remise contre '
        'signature, sous 5 à 7 jours ouvrés.',

        f'Les produits <strong>"{NOUVEAU}"</strong> '
        '(bandeau bleu en haut de la fiche produit) sont '
        'expédiés sous 24h et livrés à domicile en remise '
        'contre signature.',
    ),

    # 2 - pavé jaune, présent dans presque tous les modèles
    (
        'Les produits <strong>"Direct Fournisseur"</strong> '
        'sont expédiés sous 24h et livrés en remise contre '
        'signature, sous 5 à 7 jours ouvrés.',

        f'Les produits <strong>"{NOUVEAU}"</strong> sont '
        'expédiés sous 24h et livrés à domicile en remise '
        'contre signature.',
    ),

    # 3 - modèle TARIF FRAIS DE PORT
    (
        'Les produits <strong>Direct Fournisseur</strong> '
        'sont expédiés séparément des produits en stock.',

        f'Les produits en <strong>{NOUVEAU}</strong> sont '
        'expédiés séparément des produits en stock.',
    ),

    # 5 - modèle TARIF FRAIS DE PORT
    (
        '"En Stock", "En Précommande" et "Direct Fournisseur"',
        f'"En Stock", "En Précommande" et "{NOUVEAU}"',
    ),

    # 1 - pavé jaune, présent dans presque tous les modèles
    (
        '"En Stock" et "Direct Fournisseur"',
        f'"En Stock" et "{NOUVEAU}"',
    ),

    # 4 - modèle TARIF FRAIS DE PORT
    (
        'la livraison Direct Fournisseur étant offerte',
        'cette livraison étant offerte',
    ),

    # 7 - modèle TARIF FRAIS DE PORT, titre en majuscules
    (
        'LOGISTIQUE "DIRECT FOURNISSEUR"',
        'LOGISTIQUE "LIVRAISON SOUS 5 À 7 JOURS OUVRÉS"',
    ),
]

# Les mentions écrites en majuscules dans les COMMENTAIRES
# HTML (<!-- BANNIÈRE DIRECT FOURNISSEUR -->) ne sont pas
# touchées : elles ne s'affichent pas chez le client et
# servent de repère quand on relit un modèle.
COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)


def mentions_visibles(html):
    """
    Compte les mentions hors commentaires HTML, sans tenir
    compte de la casse.
    """

    sans_commentaires = COMMENTAIRE.sub("", html)

    return len(
        re.findall(r"direct\s+fournisseur",
                   sans_commentaires, re.I)
    )


def modeles_concernes(db):
    """
    Tous les modèles qui contiennent encore la mention,
    quel que soit leur type de produit.
    """

    return db.lire(
        """
        SELECT id, nom, html_template
        FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
          AND html_template LIKE '%Direct Fournisseur%'
        ORDER BY nom
        """
    )


def corriger(html):
    """
    Applique les remplacements et renvoie le texte corrigé
    ainsi que le nombre de substitutions faites.
    """

    total = 0

    for avant, apres in REMPLACEMENTS:

        nombre = html.count(avant)

        if nombre:
            html = html.replace(avant, apres)
            total += nombre

    return html, total


if __name__ == "__main__":

    db = Database()

    modeles = modeles_concernes(db)

    if not modeles:
        print("\nAucune mention à corriger. Rien à faire.\n")
        sys.exit(0)

    print("\n=== MODÈLES CONTENANT LA MENTION ===\n")

    prevus = []
    restants = []

    for modele in modeles:

        html = modele["html_template"]

        nouveau_html, traites = corriger(html)

        non_traites = mentions_visibles(nouveau_html)

        print(
            f"   {modele['nom'][:44]:<46} "
            f"{traites} à corriger"
            + (f"   /!\\ {non_traites} non reconnue(s)"
               if non_traites else "")
        )

        if traites:
            prevus.append((modele["id"], nouveau_html))

        if non_traites:
            restants.append(modele["nom"])

    total = sum(1 for _ in prevus)

    print(
        f"\n{total} modèle(s) seront modifiés.\n"
        f"\nRemplacement appliqué :\n"
        f'   "Direct Fournisseur"  ->  "{NOUVEAU}"\n'
    )

    if restants:
        print(
            "Formulations non reconnues, à regarder à la "
            "main après coup :\n   "
            + "\n   ".join(restants)
            + "\n"
        )

    reponse = input("Appliquer ? (tape oui puis Entrée) : ")

    if reponse.strip().lower() not in ("oui", "o"):
        print("\nAnnulé. Rien n'a été modifié.\n")
        sys.exit(0)

    for modele_id, nouveau_html in prevus:

        db.executer(
            "UPDATE modeles_fiche_produit "
            "SET html_template = ? WHERE id = ?",
            (nouveau_html, modele_id)
        )

    print(f"\n{total} modèle(s) corrigé(s).\n")

    # Contrôle final : on relit la base pour voir ce qui
    # contient encore une mention visible par le client.

    apres = db.lire(
        """
        SELECT nom, html_template FROM modeles_fiche_produit
        WHERE html_template IS NOT NULL
        ORDER BY nom
        """
    )

    sales = [
        ligne["nom"] for ligne in apres
        if mentions_visibles(ligne["html_template"])
    ]

    if not sales:
        print(
            "Plus aucune mention visible par le client.\n"
            "Les mentions restantes sont dans des "
            "commentaires HTML, invisibles sur la fiche.\n"
        )
    else:
        print("Mention encore visible dans :\n")
        for nom in sales:
            print(f"   {nom}")
        print()