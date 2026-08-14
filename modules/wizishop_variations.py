r"""
modules/wizishop_variations.py
------------------------------------------------------------
Construit les groupes "attributes" envoyes a WiziShop a
partir des variations du logiciel (produits_variations).

PRIX : sur un produit a variations, c'est LA VARIATION qui
porte le prix affiche. Chaque taille part donc au PRIX DE
VENTE HT du produit, augmente de son supplement s'il en a
un. Constate le 08/08/2026 : des tailles a 0 font apparaitre
le produit a 0 EUR sur la boutique.

L'option emballage cadeau, elle, se comporte en supplement
et reste geree dans wizishop_produits.py.

LES POIDS DES VARIATIONS SONT DEJA EN GRAMMES.
------------------------------------------------------------
"""


def groupes_variations(connexion, produit, prix_ht):
    """
    Renvoie (groupes, avertissements).

    prix_ht est le prix de vente HORS TAXES calcule pour le
    canal Site. Il sert de prix de base a chaque option.
    """

    avertissements = []

    lignes = connexion.execute(
        "SELECT id, sku, ean, libelle, poids, quantite_stock, "
        "prix_supplement_ht "
        "FROM produits_variations "
        "WHERE produit_id = ? AND actif = 1 "
        "ORDER BY ordre, id",
        (produit["id"],)
    ).fetchall()

    if not lignes:
        return [], avertissements

    criteres = {}

    for ligne in lignes:
        criteres[ligne["id"]] = connexion.execute(
            "SELECT a.nom AS critere, va.valeur AS valeur "
            "FROM variations_valeurs vv "
            "JOIN attributs a ON a.id = vv.attribut_id "
            "JOIN valeurs_attributs va ON va.id = vv.valeur_id "
            "WHERE vv.variation_id = ?",
            (ligne["id"],)
        ).fetchall()

    noms = set()

    for rangs in criteres.values():
        for rang in rangs:
            noms.add(rang["critere"])

    if not noms:
        avertissements.append(
            "des variations existent mais aucune n'est reliee a "
            "un critere : elles ne sont pas envoyees"
        )
        return [], avertissements

    if len(noms) > 1:
        avertissements.append(
            "ce produit croise plusieurs criteres ("
            + ", ".join(sorted(noms))
            + ") : WiziShop porte le SKU et le stock au niveau "
            "d'une option et non d'une combinaison, les "
            "variations ne sont pas envoyees"
        )
        return [], avertissements

    nom_critere = noms.pop()

    try:
        prix_de_base = float(prix_ht or 0)
    except (TypeError, ValueError):
        prix_de_base = 0.0

    if prix_de_base <= 0:
        avertissements.append(
            "prix de vente introuvable : les variations "
            "partiraient a 0 EUR, elles ne sont pas envoyees"
        )
        return [], avertissements

    poids_parent = int(round(float(produit["poids"] or 0) * 1000))

    options = []

    for ligne in lignes:

        libelle = ligne["libelle"] or ""

        if not libelle:
            rangs = criteres[ligne["id"]]
            libelle = rangs[0]["valeur"] if rangs else ""

        poids = ligne["poids"]

        try:
            supplement = float(ligne["prix_supplement_ht"] or 0)
        except (TypeError, ValueError):
            supplement = 0.0

        options.append({
            "value": libelle,
            "sku": ligne["sku"] or "",
            "ean13": ligne["ean"] or "",
            "weight": int(round(float(poids))) if poids else poids_parent,
            "quantity": int(ligne["quantite_stock"] or 0),

            # PRIX COMPLET de la declinaison.
            "price_tax_excluded": round(supplement, 2),

            "reduction": 0,
            "reduction_type": "amount",
            "image": "",
            "active": True,
            "default": False,
        })

    sans_ean = [o["value"] for o in options if not o["ean13"]]

    if sans_ean:
        avertissements.append(
            "variations sans EAN : " + ", ".join(sans_ean)
        )

    sans_stock = [o["value"] for o in options if o["quantity"] <= 0]

    if sans_stock:
        avertissements.append(
            "variations a zero en stock, invendables sur le "
            "site : " + ", ".join(sans_stock)
        )

    return [{
        "name": nom_critere,
        "label": nom_critere,
        "options": options,
    }], avertissements