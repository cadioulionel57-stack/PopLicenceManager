from database.schema import SCHEMA


# ==========================================================
# Une ligne par référence vendable
# ==========================================================

SCHEMA["produits_variations"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Le produit parent (le t-shirt), dont la variation
    # hérite de tout ce qui n'est pas redéfini ici.
    ("produit_id", "INTEGER"),

    # Codes propres à cette référence. L'EAN est unique :
    # deux tailles ne peuvent pas partager un code-barres.
    ("sku", "TEXT UNIQUE"),
    ("ean", "TEXT UNIQUE"),

    # Libellé lisible, reconstruit à partir des critères
    # ("Noir / M"). Stocké pour l'affichage et l'export,
    # pour ne pas avoir à le recalculer à chaque ligne.
    ("libelle", "TEXT"),

    # Écart de prix par rapport au produit parent. Une XL
    # peut coûter 2 € de plus qu'une S. Zéro le plus souvent.
    ("prix_supplement_ht", "REAL DEFAULT 0"),

    # Le prix d'achat peut lui aussi différer d'une taille à
    # l'autre. Vide = on reprend celui du produit parent.
    ("prix_achat_ht", "REAL"),

    # Une XL pèse plus lourd qu'une S, et le transport suit.
    # Vide = on reprend le poids du produit parent.
    ("poids", "REAL"),

    # Quantité mise en vente sur les canaux, comme
    # produits.quantite_stock mais au niveau de la taille.
    # Le stock réel, lui, se lit dans mouvements_stock.
    ("quantite_stock", "INTEGER DEFAULT 0"),

    # Identifiant renvoyé par WiziShop à la création de la
    # variation. Vide tant que le produit n'est pas exporté.
    ("id_wizishop", "TEXT"),

    # Ordre d'affichage : S avant M avant L, et non l'ordre
    # alphabétique qui donnerait L, M, S, XL.
    ("ordre", "INTEGER DEFAULT 0"),

    ("actif", "INTEGER DEFAULT 1"),
]


# ==========================================================
# Le croisement des critères
#
# Une ligne par critère de la variation :
#   variation 12 -> Couleur = Noir
#   variation 12 -> Taille  = M
#
# C'est ce qui permet un critère, deux ou trois sans rien
# changer à la mécanique.
# ==========================================================

SCHEMA["variations_valeurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("variation_id", "INTEGER"),

    # Le critère (Couleur, Taille, Pointure, Tour de tête)
    ("attribut_id", "INTEGER"),

    # Sa valeur (Noir, M, 42, 58 cm)
    ("valeur_id", "INTEGER"),
]


# ==========================================================
# Colonnes ajoutées à des tables existantes
#
# On complète les listes déjà définies dans schema.py au
# lieu de les redéfinir : les redéfinir effacerait toutes
# leurs colonnes actuelles.
# ==========================================================

def _ajouter_colonne(table, nom, type_colonne):
    """
    Ajoute une colonne à une table existante du schéma, sans
    rien écraser, et sans la dupliquer si elle y est déjà.
    """

    colonnes = SCHEMA.get(table)

    if colonnes is None:
        return

    if any(existante == nom for existante, _ in colonnes):
        return

    colonnes.append((nom, type_colonne))


# Un mouvement de stock concerne désormais soit le produit
# entier (un mug), soit une variation précise (le t-shirt
# noir en M). Vide = le produit entier, comme avant.
_ajouter_colonne("mouvements_stock", "variation_id", "INTEGER")

# Une ligne de commande doit dire quelle taille a été
# vendue, sinon on ne peut pas décrémenter le bon stock.
_ajouter_colonne("lignes_commandes", "variation_id", "INTEGER")

# Idem à la réception d'un achat fournisseur.
_ajouter_colonne("achats_fournisseurs_lignes", "variation_id", "INTEGER")