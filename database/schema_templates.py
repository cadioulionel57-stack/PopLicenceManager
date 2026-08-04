from database.schema import SCHEMA


SCHEMA["regles_template_periode"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Nom parlant, pour s'y retrouver dans la liste :
    # « Noël sur le textile », « Soldes d'hiver »...
    ("nom", "TEXT"),

    # Quand la règle s'applique. La période porte déjà ses
    # dates de début et de fin.
    ("periode_id", "INTEGER"),

    # Le modèle de fiche à appliquer pendant ce temps.
    ("modele_fiche_id", "INTEGER"),

    # Sur quels produits. Vide = TOUTES les catégories.
    # Renseigné = uniquement cette catégorie du site.
    ("categorie_site_id", "INTEGER"),

    # Le type de produit visé : "stock", "dropshipping",
    # "precommande" ou "bundle". Vide = tous les types.
    #
    # Indispensable parce qu'un modèle de fiche est lui-même
    # rattaché à un type : un « Template DF Noël Jouets » ne
    # doit toucher que les produits Direct Fournisseur de la
    # catégorie Jouets, pas ceux qui sont en stock.
    ("type_produit", "TEXT"),

    # Quand deux règles se chevauchent, la plus haute
    # priorité l'emporte. À égalité, c'est la règle la plus
    # précise qui gagne : celle qui vise à la fois une
    # catégorie ET un type passe devant celle qui ne vise
    # qu'une catégorie, elle-même devant une règle générale.
    ("priorite", "INTEGER DEFAULT 0"),

    ("actif", "INTEGER DEFAULT 1"),
]


# ==========================================================
# Bloc livraison réutilisable
#
# Le pavé « Optimisez votre livraison » était recopié à
# l'identique dans chaque modèle de fiche. Le moindre
# changement de tarif obligeait à rouvrir tous les modèles
# un par un.
#
# Même principe que le bloc emballage cadeau : un seul
# exemplaire, modifiable une fois, inséré partout via
# {{bloc_livraison}}.
# ==========================================================

SCHEMA["bloc_livraison"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("html_template", "TEXT"),
]


# ==========================================================
# Accroche commerciale par modèle de fiche
#
# La description courte d'un produit — le premier texte que
# lit le client, juste sous le nom — se compose de deux
# parties :
#
#   la partie factuelle, tirée des champs du produit
#   (poids, dimensions, matière, coloris), automatique ;
#
#   et une phrase qui vend, propre à la famille de produit
#   (« taillé pour les journées d'école des plus petits »),
#   qu'aucun générateur ne peut inventer.
#
# Cette phrase est donc écrite une seule fois par modèle de
# fiche, et reprise sur tous les produits qui l'utilisent.
#
# La colonne est ajoutée automatiquement à la base existante
# au prochain lancement du logiciel : aucune manipulation,
# aucune donnée perdue.
# ==========================================================

SCHEMA["modeles_fiche_produit"].append(
    ("accroche", "TEXT")
)