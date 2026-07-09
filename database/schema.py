SCHEMA = {

    "produits": [

        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

        ("ean", "TEXT UNIQUE"),
        ("sku", "TEXT UNIQUE"),

        ("type_produit", "TEXT"),

        ("nom", "TEXT"),

       ("licence_id", "INTEGER"),

       ("univers_id", "INTEGER"),

       ("categorie_poplicence_id", "INTEGER"),

       ("famille_produit_id", "INTEGER"),

       ("marque_id", "INTEGER"),

       ("fournisseur_id", "INTEGER"),
        ("reference_fournisseur", "TEXT"),

        ("prix_fournisseur_ht", "REAL"),
        ("taux_tva_achat", "REAL"),

("prix_achat_gestion", "REAL"),

("cout_revient", "REAL"),

("marge_visee_pourcentage", "REAL"),


        ("longueur", "REAL"),
        ("largeur", "REAL"),
        ("hauteur", "REAL"),
        ("poids", "REAL"),

        # Dimensions du carton d'expédition, une fois le
        # produit plié/emballé — différentes des
        # dimensions ci-dessus pour les articles pliables
        # (textile...). Si vides, on utilise les dimensions
        # du produit (cas des objets rigides).
        ("longueur_expedition", "REAL"),
        ("largeur_expedition", "REAL"),
        ("hauteur_expedition", "REAL"),

        # Emballage sélectionné pour ce produit, parmi ceux
        # compatibles avec ses dimensions et son poids.
        # Pré-rempli automatiquement quand un seul emballage
        # convient, à choisir manuellement dans une liste
        # quand plusieurs conviennent. Toujours modifiable.
        ("emballage_id", "INTEGER"),

        ("matiere", "TEXT"),
        ("couleur", "TEXT"),
        ("age_minimum", "INTEGER"),
        ("pays_fabrication", "TEXT"),

        ("tva", "REAL"),

        ("ean_colis", "TEXT"),

        ("description_courte", "TEXT"),
        ("description_longue", "TEXT"),

        ("image_principale", "TEXT"),

        ("actif", "INTEGER DEFAULT 1")

    ]

}
SCHEMA["familles_produit"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    # Coût d'emballage manuel, utilisé UNIQUEMENT si
    # aucun emballage_id n'est renseigné ci-dessous
    # (rétrocompatibilité). Sinon, le coût vient
    # automatiquement de l'emballage lié.
    ("cout_emballage_ht", "REAL DEFAULT 0"),

    # Emballage de la grille utilisé par défaut pour
    # cette famille (ex : P1 pour Textile & Mode léger,
    # C1 pour Mugs/bijoux/figurines...). Si renseigné,
    # le coût d'emballage est calculé automatiquement.
    ("emballage_id", "INTEGER"),

    # Taux de retour de cette famille, exprimé en
    # pourcentage (ex : 0.18 pour 18 %). Utilisé pour
    # provisionner la perte produit + emballage sur
    # les retours dans le calcul du coût de revient.
    ("taux_retour", "REAL DEFAULT 0"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["grille_emballage"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Code court (ex : P1, P2, C1, C2, C3, C4)
    ("code", "TEXT UNIQUE"),

    ("nom", "TEXT"),

    ("longueur_ext_cm", "REAL"),
    ("largeur_ext_cm", "REAL"),
    ("hauteur_ext_cm", "REAL"),

    ("poids_g", "REAL"),

    # Poids maximum du produit que cet emballage peut
    # supporter (ex : une pochette souple ne doit pas
    # recevoir un produit trop lourd même s'il rentre
    # en dimensions). Utilisé pour la sélection
    # automatique d'emballage sur la fiche produit.
    ("poids_max_g", "REAL"),

    # Coût de l'emballage lui-même (pochette/carton)
    ("cout_ht", "REAL DEFAULT 0"),

    # Coût du calage (papier bulle, kraft, chips de
    # calage...), le carton seul ne suffit pas.
    ("calage_ht", "REAL DEFAULT 0"),

    ("actif", "INTEGER DEFAULT 1")

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

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]

SCHEMA["collections"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]
SCHEMA["personnages"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]

SCHEMA["marques"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["categories"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    # NULL = catégorie interne Pop Licence.
    # Sinon, référence un canal de vente précis
    # (Amazon, Cdiscount, WiziShop...) : chaque
    # canal a son propre arbre de catégories.
    ("canal_id", "INTEGER"),

    # Commission spécifique à cette catégorie, sur ce
    # canal (ex : Amazon "Jouets" = 15 %). Si NULL,
    # on utilise la commission par défaut du canal
    # (ex : WiziShop = 1 % pour toutes les catégories).
    # Ignoré si des paliers existent dans
    # paliers_commission_categorie pour cette catégorie.
    ("commission_pourcentage", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["paliers_commission_categorie"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("categorie_id", "INTEGER"),

    # Prix de vente jusqu'auquel ce taux s'applique.
    # NULL = dernier palier, sans limite haute.
    # Ex : Amazon Vêtements = 3 paliers :
    #   jusqu'à 15€ -> 5%
    #   jusqu'à 20€ -> 10%
    #   sans limite -> 17%
    ("seuil_prix_max", "REAL"),

    ("commission_pourcentage", "REAL"),

    ("ordre", "INTEGER")

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


SCHEMA["grille_transport"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("transporteur_id", "INTEGER"),

    # Ex : "Point Relais", "Domicile Sans Signature",
    # "Chrono 13", "Chrono 18"... un même transporteur
    # (Chronopost par ex.) peut avoir plusieurs offres.
    ("offre", "TEXT"),

    # Prix HT applicable jusqu'à ce poids (en kg) inclus.
    # Ex : 3.04€ jusqu'à 0.25kg, 3.14€ jusqu'à 0.5kg...
    ("poids_max_kg", "REAL"),

    ("prix_ht", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["grille_fba"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Nom du format de colis (ex : "Petit colis 1",
    # "Colis moyen 2", "Grand colis 1"...). Purement
    # informatif, sert à l'affichage.
    ("format_colis", "TEXT"),

    # Catégorie spéciale du produit (ex : "Linge de maison
    # et tapis"), qui a ses propres tarifs chez Amazon.
    # NULL = tarif standard, valable pour toutes les
    # catégories non spécifiques.
    ("categorie_speciale", "TEXT"),

    # Dimensions maximales de la boîte pour ce format
    # (en cm). Le format le plus petit qui contient le
    # produit est choisi automatiquement.
    ("longueur_max_cm", "REAL"),
    ("largeur_max_cm", "REAL"),
    ("hauteur_max_cm", "REAL"),

    # Poids inclus dans le prix de base (en grammes).
    ("poids_seuil_g", "REAL"),

    ("prix_base_ht", "REAL"),

    # Prix ajouté par tranche de poids supplémentaire
    # au-delà du seuil (ex : +0,08€ par 100g).
    ("prix_supplement_ht", "REAL"),
    ("supplement_pas_g", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["canaux_transporteurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("canal_id", "INTEGER"),

    ("transporteur_id", "INTEGER"),

    ("offre", "TEXT"),

    # Tranche de prix de vente TTC pour laquelle ce
    # transporteur/offre est éligible sur ce canal (ex :
    # Fnac Relais Colis = 25€ à 200€ seulement). NULL sur
    # les deux = aucune restriction de prix (comportement
    # existant, inchangé, pour les canaux qui n'ont pas ce
    # genre de règle).
    ("prix_min_ttc", "REAL"),
    ("prix_max_ttc", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["grille_tarif_client"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("canal_id", "INTEGER"),

    ("transporteur_id", "INTEGER"),

    # Doit correspondre exactement à l'"offre" utilisée
    # dans grille_transport (coût réel) pour ce même
    # transporteur, afin de calculer l'écart.
    ("offre", "TEXT"),

    # Prix facturé au client (TTC), applicable jusqu'à ce
    # poids (en kg) inclus — même principe que
    # grille_transport, mais côté prix client au lieu de
    # coût réel.
    ("poids_max_kg", "REAL"),

    ("tarif_ttc", "REAL"),

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

    # "site" (WiziShop) ou "marketplace" (Base.com, Amazon, Cdiscount...)
    ("type", "TEXT"),

    ("commission_pourcentage", "REAL DEFAULT 0"),

    # Frais fixes par vente sur ce canal (ex : Base.com +
    # étiquette). Coûts directs uniquement — les charges
    # de structure (logiciels, assurance d'entreprise...)
    # ne sont volontairement pas incluses ici.
    ("frais_fixe_ht", "REAL DEFAULT 0"),

    # Frais de paiement par défaut sur ce canal, en % du
    # prix de vente HT (ex : PayPal 2,9%, CB 1%, 0% si la
    # marketplace encaisse elle-même).
    ("frais_paiement_pourcentage", "REAL DEFAULT 0"),

    # Frais de paiement fixe par vente (ex : PayPal 0,35€
    # HT par transaction).
    ("frais_paiement_fixe_ht", "REAL DEFAULT 0"),

    # Taxe sur les services numériques (ex : Amazon 3,5%
    # de la commission). 0 pour les canaux non concernés.
    ("taux_tsn_pourcentage", "REAL DEFAULT 0"),

    # 1 = les frais de port sont inclus dans le prix affiché
    # (ex : marketplaces "livraison gratuite" type FBA, où
    # le vrai coût de transport est entièrement caché dans
    # le prix produit)
    # 0 = le client voit un frais de port séparé du prix
    # produit (Site, ou marketplace FBM)
    ("port_inclus", "INTEGER DEFAULT 0"),

    # Cas particulier du FBM : le client paie un frais de
    # port SÉPARÉ du prix produit, mais ce montant est fixé
    # par toi (pas forcément égal au vrai coût transporteur).
    # Si renseigné, seul l'ÉCART entre le vrai coût et ce
    # tarif est ajouté au coût du produit — pas le coût
    # entier. Laisser vide si non applicable (Site : le
    # client paie exactement le vrai coût, rien à absorber ;
    # FBA : le port est déjà 100% dans "port_inclus").
    ("tarif_port_client_ttc", "REAL"),

    # Seuil de commande (TTC) au-delà duquel le port est
    # gratuit pour le client. Informatif pour l'instant :
    # le calcul du prix produit part du principe prudent
    # que ce seuil n'est pas atteint (donc le port facturé
    # s'applique), pour ne jamais sous-évaluer un prix.
    ("seuil_gratuite_ttc", "REAL"),

    # Contribution transport minimale (HT), ajoutée
    # systématiquement au coût du produit sur ce canal,
    # avant calcul de la marge — en plus de l'écart déjà
    # absorbé via tarif_port_client_ttc. Sert à garantir
    # qu'une part du transport réel est toujours couverte,
    # même sur les produits légers/bon marché où l'écart
    # seul serait insuffisant. 0 = non applicable.
    ("contribution_transport_min_ht", "REAL DEFAULT 0"),

    # Prix de vente TTC en dessous duquel ce canal est
    # déconseillé pour ce produit (zone grise structurelle :
    # port + commission trop lourds face au prix). Purement
    # indicatif (n'empêche pas l'enregistrement), affiché
    # comme alerte dans l'onglet Tarification. NULL = pas
    # de seuil défini pour ce canal.
    ("prix_vente_min_ttc", "REAL"),

    # 1 = ce canal utilise la grille_tarif_client (tarif de
    # port facturé au client variable selon le transporteur
    # ET le poids — cas Fnac, où le client choisit entre
    # plusieurs modes à des tarifs différents). Si actif,
    # tarif_port_client_ttc (valeur unique) est ignoré : le
    # moteur résout le transporteur éligible automatiquement
    # (poids + tranche de prix), avec jusqu'à 3 passes
    # itératives comme pour les paliers de commission.
    ("grille_tarif_client_active", "INTEGER DEFAULT 0"),

    # 1 = ce canal calcule son "transport" via la grille
    # FBA (format de colis selon dimensions + poids) au
    # lieu de la grille transporteurs classique (Boxtal).
    ("utilise_grille_fba", "INTEGER DEFAULT 0"),

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
SCHEMA["produits_prix_marche"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    # Prix TTC observé chez la concurrence sur ce canal,
    # saisi manuellement, pour comparer au prix minimum
    # rentable calculé automatiquement.
    ("prix_ttc", "REAL")

]
SCHEMA["produits_marges"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    # Marge visée spécifique à ce canal pour ce produit.
    # Si absente, la marge par défaut du produit
    # (marge_visee_pourcentage) s'applique.
    ("marge_pourcentage", "REAL")

]
SCHEMA["produits_categories_canaux"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("produit_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    ("categorie_id", "INTEGER")

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
SCHEMA["numerotations"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("code", "TEXT UNIQUE"),

    ("prefixe", "TEXT"),

    ("dernier_numero", "INTEGER DEFAULT 0"),

    ("longueur", "INTEGER DEFAULT 6"),

    ("actif", "INTEGER DEFAULT 1")

]