SCHEMA = {

    "produits": [

        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

        ("ean", "TEXT UNIQUE"),
        ("sku", "TEXT UNIQUE"),

        ("nom", "TEXT"),

       ("licence_id", "INTEGER"),

       ("univers_id", "INTEGER"),

       ("categorie_poplicence_id", "INTEGER"),

       ("categorie_amazon_id", "INTEGER"),

       ("marque_id", "INTEGER"),

       ("fournisseur_id", "INTEGER"),
        ("reference_fournisseur", "TEXT"),

        ("prix_fournisseur_ht", "REAL"),
        ("taux_tva_achat", "REAL"),

("prix_achat_gestion", "REAL"),

("cout_revient", "REAL"),



        ("longueur", "REAL"),
        ("largeur", "REAL"),
        ("hauteur", "REAL"),
        ("poids", "REAL"),

        ("tva", "REAL"),

        ("ean_colis", "TEXT"),

        ("description_courte", "TEXT"),
        ("description_longue", "TEXT"),

        ("image_principale", "TEXT"),

        ("actif", "INTEGER DEFAULT 1")

    ]

}
SCHEMA["marketplaces"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("type", "TEXT"),

    ("actif", "INTEGER DEFAULT 1"),

    ("ordre", "INTEGER")

]


SCHEMA["produits_marketplaces"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("marketplace_id", "INTEGER"),

    ("publie", "INTEGER DEFAULT 0"),

    ("prix_ht", "REAL"),

    ("prix_ttc", "REAL"),

    ("reference_marketplace", "TEXT")

]
SCHEMA["licences"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT"),

    ("couleur", "TEXT"),

    ("logo", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["univers"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["marques"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["categories"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("type", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["fournisseurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("contact", "TEXT"),

    ("telephone", "TEXT"),

    ("email", "TEXT"),

    ("site", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]
SCHEMA["transporteurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["emballages"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("cout_ht", "REAL"),

    ("poids", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["tva"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    ("taux", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]
SCHEMA["parametres"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("cle", "TEXT UNIQUE"),

    ("valeur", "TEXT"),

    ("description", "TEXT")

]
SCHEMA["canaux_vente"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("type", "TEXT"),

    ("marketplace_id", "INTEGER"),

    ("actif", "INTEGER DEFAULT 1"),

    ("ordre", "INTEGER")

]


SCHEMA["produits_canaux"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    ("publie", "INTEGER DEFAULT 0"),

    ("reference_externe", "TEXT"),

    ("statut", "TEXT")

]
SCHEMA["images_produits"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("ordre", "INTEGER"),

    ("fichier", "TEXT"),

    ("type", "TEXT"),

    ("principal", "INTEGER DEFAULT 0")

]


SCHEMA["documents_produits"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("nom", "TEXT"),

    ("fichier", "TEXT"),

    ("type", "TEXT")

]
SCHEMA["attributs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("type", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["valeurs_attributs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("attribut_id", "INTEGER"),

    ("valeur", "TEXT"),

    ("ordre", "INTEGER"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["produits_attributs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("attribut_id", "INTEGER"),

    ("valeur_id", "INTEGER"),

    ("valeur_libre", "TEXT")

]
SCHEMA["stocks"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("entrepot_id", "INTEGER"),

    ("quantite", "INTEGER"),

    ("stock_alerte", "INTEGER"),

    ("stock_securite", "INTEGER"),

    ("emplacement", "TEXT")

]


SCHEMA["entrepots"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("type", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["mouvements_stock"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("entrepot_id", "INTEGER"),

    ("date", "TEXT"),

    ("type", "TEXT"),

    ("quantite", "INTEGER"),

    ("origine", "TEXT"),

    ("reference", "TEXT"),

    ("commentaire", "TEXT")

]
SCHEMA["commandes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("numero", "TEXT UNIQUE"),

    ("canal_id", "INTEGER"),

    ("client_id", "INTEGER"),

    ("date_commande", "TEXT"),

    ("date_expedition", "TEXT"),

    ("transporteur_id", "INTEGER"),

    ("statut", "TEXT"),

    ("montant_ht", "REAL"),

    ("montant_ttc", "REAL"),

    ("frais_port_ht", "REAL"),

    ("frais_port_ttc", "REAL"),

    ("tracking", "TEXT"),

    ("commentaire", "TEXT")

]


SCHEMA["lignes_commandes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("commande_id", "INTEGER"),

    ("produit_id", "INTEGER"),

    ("quantite", "INTEGER"),

    ("prix_unitaire_ht", "REAL"),

    ("prix_unitaire_ttc", "REAL"),

    ("remise_ht", "REAL"),

    ("tva", "REAL")

]


SCHEMA["clients"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    ("prenom", "TEXT"),

    ("societe", "TEXT"),

    ("email", "TEXT"),

    ("telephone", "TEXT"),

    ("adresse", "TEXT"),

    ("code_postal", "TEXT"),

    ("ville", "TEXT"),

    ("pays", "TEXT")

]
SCHEMA["ventes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("commande_id", "INTEGER"),

    ("produit_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    ("date_vente", "TEXT"),

    ("quantite", "INTEGER"),

    ("chiffre_affaires_ht", "REAL"),

    ("chiffre_affaires_ttc", "REAL"),

    ("commission_ht", "REAL"),

    ("commission_ttc", "REAL"),

    ("cout_revient", "REAL"),

    ("benefice_ht", "REAL"),

    ("benefice_ttc", "REAL")

]


SCHEMA["paiements"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("commande_id", "INTEGER"),

    ("date_paiement", "TEXT"),

    ("mode_paiement", "TEXT"),

    ("montant", "REAL"),

    ("reference", "TEXT")

]


SCHEMA["tresorerie"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date", "TEXT"),

    ("type", "TEXT"),

    ("categorie", "TEXT"),

    ("libelle", "TEXT"),

    ("montant", "REAL"),

    ("solde", "REAL"),

    ("reference", "TEXT")

]
SCHEMA["sav"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("numero", "TEXT UNIQUE"),

    ("commande_id", "INTEGER"),

    ("client_id", "INTEGER"),

    ("produit_id", "INTEGER"),

    ("date_ouverture", "TEXT"),

    ("date_cloture", "TEXT"),

    ("motif", "TEXT"),

    ("statut", "TEXT"),

    ("solution", "TEXT"),

    ("montant", "REAL"),

    ("commentaire", "TEXT")

]


SCHEMA["achats"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("numero", "TEXT UNIQUE"),

    ("fournisseur_id", "INTEGER"),

    ("date_commande", "TEXT"),

    ("date_reception", "TEXT"),

    ("statut", "TEXT"),

    ("montant_ht", "REAL"),

    ("montant_ttc", "REAL"),

    ("commentaire", "TEXT")

]


SCHEMA["lignes_achats"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("achat_id", "INTEGER"),

    ("produit_id", "INTEGER"),

    ("quantite", "INTEGER"),

    ("prix_unitaire_ht", "REAL"),

    ("tva", "REAL")

]
SCHEMA["imports"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date_import", "TEXT"),

    ("canal_id", "INTEGER"),

    ("type_import", "TEXT"),

    ("fichier", "TEXT"),

    ("lignes_importees", "INTEGER"),

    ("lignes_erreur", "INTEGER"),

    ("utilisateur", "TEXT")

]


SCHEMA["exports"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date_export", "TEXT"),

    ("canal_id", "INTEGER"),

    ("type_export", "TEXT"),

    ("fichier", "TEXT"),

    ("lignes_exportees", "INTEGER"),

    ("utilisateur", "TEXT")

]


SCHEMA["journaux"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date", "TEXT"),

    ("niveau", "TEXT"),

    ("module", "TEXT"),

    ("action", "TEXT"),

    ("details", "TEXT")

]
SCHEMA["utilisateurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    ("prenom", "TEXT"),

    ("email", "TEXT UNIQUE"),

    ("mot_de_passe", "TEXT"),

    ("role", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["roles"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT")

]


SCHEMA["permissions"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("module", "TEXT"),

    ("action", "TEXT"),

    ("description", "TEXT")

]


SCHEMA["roles_permissions"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("role_id", "INTEGER"),

    ("permission_id", "INTEGER")

]
SCHEMA["taches"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("titre", "TEXT"),

    ("description", "TEXT"),

    ("utilisateur_id", "INTEGER"),

    ("priorite", "TEXT"),

    ("statut", "TEXT"),

    ("date_creation", "TEXT"),

    ("date_echeance", "TEXT"),

    ("date_fin", "TEXT")

]


SCHEMA["notifications"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("utilisateur_id", "INTEGER"),

    ("date", "TEXT"),

    ("titre", "TEXT"),

    ("message", "TEXT"),

    ("lu", "INTEGER DEFAULT 0")

]


SCHEMA["sauvegardes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date", "TEXT"),

    ("nom_fichier", "TEXT"),

    ("taille", "INTEGER"),

    ("type", "TEXT"),

    ("commentaire", "TEXT")

]