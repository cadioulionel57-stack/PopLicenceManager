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

        # Champs textile façon Amazon (liste à puces sur la
        # fiche HTML) — génériques et libres, à laisser vides
        # si non pertinents pour le type d'article (ex : un
        # pantalon n'a pas de "manche").
        ("composition_matiere", "TEXT"),
        ("instructions_entretien", "TEXT"),
        ("coupe_type", "TEXT"),
        ("type_manche", "TEXT"),

        ("tva", "REAL"),

        ("ean_colis", "TEXT"),

        # Éligibilité à la prestation d'emballage cadeau —
        # uniquement pertinent pour les produits de type
        # "stock" (proposée seulement sur le site). Le client
        # choisit ou non de la payer au moment de l'achat ;
        # cette case dit juste si l'option lui est proposée.
        ("eligible_papier_cadeau", "INTEGER DEFAULT 0"),

        # Statut de disponibilité, distinct du champ "actif"
        # (qui sert à archiver/supprimer). 'actif' = normal,
        # 'rupture' = temporairement indisponible, 'fin_de_vie'
        # = ne sera plus jamais réapprovisionné. Affiché en
        # couleur dans la liste des produits.
        ("statut_stock", "TEXT DEFAULT 'actif'"),

        # Quantité réellement en stock — distincte du statut
        # ci-dessus (qui dit si tu vends encore ce produit,
        # pas combien tu en as). Nécessaire pour l'export
        # WiziShop ("Nombre de produits en stock"), et pour
        # que ce nombre reste juste si un produit est un
        # jour réimporté depuis WiziShop puis réexporté.
        ("quantite_stock", "INTEGER DEFAULT 0"),

        # Coché automatiquement quand la fiche est créée en
        # vitesse depuis "Achats Stocks" (nom + prix d'achat
        # seulement) — signale qu'il manque des infos avant
        # export (dimensions, marge, catégories par canal...).
        # Décoché manuellement une fois la fiche complétée.
        ("fiche_a_terminer", "INTEGER DEFAULT 0"),

        # Onglet SEO — remplis automatiquement à la création
        # du produit (voir modules/seo_generator.py), toujours
        # modifiables ensuite. Pensés pour être exportés tels
        # quels vers WiziShop/Base.com, sans retouche.
        ("titre_seo", "TEXT"),
        ("meta_description", "TEXT"),
        ("mots_cles", "TEXT"),
        ("url_slug", "TEXT"),

        ("description_courte", "TEXT"),
        ("description_longue", "TEXT"),

        ("image_principale", "TEXT"),
        ("image_2", "TEXT"),
        ("image_3", "TEXT"),

        # Image de fond utilisée dans la section "Univers
        # produit" des chartes HTML — volontairement séparée
        # des Photos 1/2/3 (celles-ci vont à WiziShop, celle-
        # là est une image d'ambiance propre à la charte
        # graphique, à changer facilement sans toucher aux
        # vraies photos produit).
        ("image_ambiance", "TEXT"),

        # Catégorie du site (pointe vers la sous-catégorie,
        # WiziShop exigeant les deux niveaux — la catégorie
        # principale se retrouve via categorie_parente_id).
        # Uniquement pertinent pour les produits destinés au
        # site (Site+Drop).
        ("categorie_site_id", "INTEGER"),

        # Thème de template (Vêtements, Figurines...) —
        # détermine quel modèle "Automatique" s'applique à ce
        # produit. Distinct de la catégorie WiziShop
        # ci-dessus.
        ("theme_template_id", "INTEGER"),

        # Force un modèle précis pour CE produit, en dehors
        # du fonctionnement automatique par thème — laisser
        # vide pour suivre le modèle actif du thème.
        ("modele_fiche_id", "INTEGER"),

        # Identifiant attribué par WiziShop une fois le
        # produit importé (le #N) — vide tant qu'il n'a
        # jamais été exporté/importé, permet ensuite de
        # mettre à jour la bonne fiche plutôt que d'en
        # recréer une nouvelle.
        ("id_wizishop", "TEXT"),

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

    # 'souple' (pochette P1/P2 : pas de marge de sécurité
    # nécessaire, le produit peut être enveloppé au plus
    # près) ou 'rigide' (carton C1-C4 : marge de +1cm
    # appliquée, pour permettre fermeture/calage). Utilisé
    # par la sélection automatique d'emballage sur la fiche
    # produit.
    ("type_emballage", "TEXT DEFAULT 'rigide'"),

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

    # Identifiant WiziShop de cette marque (le #N visible
    # dans Produits > Marques sur WiziShop) — obligatoire
    # pour l'export CSV du catalogue.
    ("id_wizishop", "TEXT"),

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["themes_template"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("description", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["modeles_fiche_produit"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    # Thème large (Vêtements, Figurines...) — regroupe les
    # templates pour s'y retrouver et permettre un bascule
    # global (ex : passer tout le thème "Vêtements" en mode
    # Noël d'un coup), distinct des catégories WiziShop
    # précises.
    ("theme_id", "INTEGER"),

    # 'stock' ou 'dropshipping'.
    ("type_produit", "TEXT"),

    # Le code HTML complet de la charte, avec des variables
    # entre doubles accolades (ex: {{nom_produit}}) que le
    # logiciel remplace à l'export.
    ("html_template", "TEXT"),

    # Un seul modèle actif à la fois par thème+type — celui
    # utilisé automatiquement pour les produits en mode
    # "Automatique". Les autres (Noël, soldes...) restent en
    # mémoire, prêts à être réactivés d'un clic.
    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["categories_site"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    # Identifiant WiziShop de cette catégorie (le #N visible
    # dans Produits > Catégories sur WiziShop).
    ("id_wizishop", "TEXT"),

    # NULL = catégorie principale. Sinon, référence l'id
    # d'une autre ligne de cette même table : c'est une
    # sous-catégorie rattachée à cette catégorie principale.
    ("categorie_parente_id", "INTEGER"),

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


SCHEMA["paliers_frais_gestion"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("canal_id", "INTEGER"),

    # Prix de vente TTC jusqu'auquel ce montant s'applique.
    # NULL = dernier palier, sans limite haute.
    # Ex : Rakuten = 0,15€ jusqu'à 10€, 0,50€ jusqu'à 50€...
    ("seuil_prix_max", "REAL"),

    # Montant fixe HT (pas un pourcentage, contrairement aux
    # paliers de commission).
    ("frais_gestion_ht", "REAL"),

    ("ordre", "INTEGER")

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


SCHEMA["grille_emballage_cadeau"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("code", "TEXT UNIQUE"),

    ("nom", "TEXT"),

    ("cout_ht", "REAL DEFAULT 0"),

    # 'principal' : le choix d'emballage visible/facturé au
    # client (toujours au même tarif, quel que soit le code
    # choisi — le coût réel varie, pas le prix facturé).
    # 'supplement' : un ajout optionnel (papier de soie,
    # étiquette...) jamais facturé séparément au client,
    # juste un coût en plus qui réduit la marge sur la
    # prestation.
    ("type", "TEXT DEFAULT 'principal'"),

    # Uniquement renseigné pour les codes de type
    # 'principal' — le montant HT facturé au client,
    # actuellement 2,42€ pour tous, mais modifiable
    # individuellement si un jour tu differencies les tarifs.
    ("tarif_facture_ht", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]

SCHEMA["fournisseurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT UNIQUE"),

    ("contact", "TEXT"),

    ("telephone", "TEXT"),

    ("email", "TEXT"),

    ("site", "TEXT"),

    # Montant minimum de commande exigé par ce fournisseur
    # (HT), en dessous duquel il n'accepte pas la commande.
    ("seuil_minimum_commande", "REAL"),

    # Montant de commande (HT) à partir duquel les frais de
    # port sont offerts par ce fournisseur.
    ("franco_port", "REAL"),

    # Frais de port facturés par ce fournisseur si la
    # commande est en dessous du seuil de franco ci-dessus.
    ("frais_port", "REAL"),

    # Conditions de règlement en texte libre (ex : "30 jours
    # fin de mois", "comptant à la commande", "50% acompte").
    ("conditions_reglement", "TEXT"),

    # Délai de livraison en texte libre (ex : "15-20 jours",
    # "3 semaines", variable selon les produits chez
    # certains fournisseurs, d'où le texte libre plutôt
    # qu'un nombre de jours figé).
    ("delai_livraison", "TEXT"),

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

    # Couleur d'identification visuelle du canal (code hexa,
    # ex : "#1e7d32") — reprise dans l'onglet Tarification
    # des fiches produit pour repérer chaque canal d'un coup
    # d'œil.
    ("couleur", "TEXT DEFAULT '#144b8b'"),

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
SCHEMA["contributions_fonds_croissance"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("commande_id", "INTEGER UNIQUE"),

    # Montant figé au moment où la commande a été cochée
    # payée — ne change jamais après coup, même si le taux
    # de contribution est modifié plus tard dans les
    # réglages. Une commande décochée retire sa ligne ici.
    ("montant_contribue", "REAL"),

    ("taux_applique", "REAL"),

    ("date_contribution", "TEXT")

]


SCHEMA["commandes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Numéro tel que fourni par WiziShop/Base.com/la
    # marketplace — unique pour éviter les doublons si tu
    # importes la même commande deux fois plus tard.
    ("numero", "TEXT UNIQUE"),

    ("canal_id", "INTEGER"),

    ("client_id", "INTEGER"),

    ("date_commande", "TEXT"),

    ("date_expedition", "TEXT"),

    ("transporteur_id", "INTEGER"),

    ("statut", "TEXT DEFAULT 'En cours'"),

    # Argent réellement reçu ou non — distinct du statut de
    # livraison. Une vente marketplace peut être "Livrée"
    # sans que l'argent soit encore arrivé sur le compte
    # (reversement différé). Sert de base au calcul de la
    # trésorerie réelle disponible.
    ("paye", "INTEGER DEFAULT 0"),

    # Date à laquelle l'argent est réellement arrivé — pas
    # forcément le jour où tu coches la case, si tu coches
    # après-coup.
    ("date_paiement", "TEXT"),

    ("montant_ht", "REAL"),

    ("montant_ttc", "REAL"),

    # Frais de port payés PAR LE CLIENT (ce qu'il a réglé à
    # l'achat) — jamais confondu avec le coût réel ci-dessous.
    ("frais_port_client_ttc", "REAL"),

    # Frais de port réellement payés PAR TOI au transporteur
    # (le vrai coût, indispensable pour calculer ta marge
    # réelle sur cette commande).
    ("frais_port_reel_ht", "REAL"),

    # Prestation emballage cadeau — un seul choix par
    # commande. papier_cadeau_emballage_id = le code
    # "principal" choisi (toujours facturé au tarif fixe de
    # la grille, quel que soit le code) ; supplement_id = un
    # ajout optionnel (papier de soie...), jamais facturé,
    # juste un coût en plus.
    ("papier_cadeau_actif", "INTEGER DEFAULT 0"),
    ("papier_cadeau_emballage_id", "INTEGER"),
    ("papier_cadeau_supplement_id", "INTEGER"),

    ("tracking", "TEXT"),

    ("commentaire", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["lignes_commandes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("commande_id", "INTEGER"),

    # Peut être NULL si le produit n'existe plus dans ton
    # catalogue au moment de l'import (nom_produit ci-dessous
    # reste alors la seule trace).
    ("produit_id", "INTEGER"),

    # Copie du nom au moment de la commande — ne dépend
    # jamais du produit actuel, qui peut être renommé ou
    # supprimé depuis.
    ("nom_produit", "TEXT"),

    ("quantite", "INTEGER DEFAULT 1"),

    ("prix_unitaire_ht", "REAL"),

    ("prix_unitaire_ttc", "REAL"),

    # Coût d'achat unitaire (HT) au moment de la commande —
    # figé ici, jamais recalculé depuis la fiche produit,
    # pour que la marge de cette vente reste exacte même si
    # ton prix d'achat change plus tard.
    ("cout_achat_unitaire_ht", "REAL"),

    ("remise_ht", "REAL"),

    ("tva", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["commandes_retours"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Lié à une ligne précise, pas à toute la commande : on
    # peut retourner un seul article parmi plusieurs achetés
    # dans la même commande.
    ("ligne_commande_id", "INTEGER"),

    ("date_retour", "TEXT"),

    ("motif", "TEXT"),

    ("statut", "TEXT DEFAULT 'Demandé'"),

    ("montant_rembourse_ttc", "REAL"),

    # Frais de réexpédition si un produit de remplacement
    # est renvoyé au client (distinct du coût du retour
    # ci-dessous, qui couvre le retour initial).
    ("frais_reexpedition_ht", "REAL"),

    # Coût du retour lui-même (étiquette retour, remise en
    # stock, produit invendable...).
    ("cout_retour_ht", "REAL"),

    ("notes", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["achats_fournisseurs"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("numero", "TEXT UNIQUE"),

    ("fournisseur_id", "INTEGER"),

    ("date_achat", "TEXT"),

    ("date_reception", "TEXT"),

    ("statut", "TEXT DEFAULT 'Commandé'"),

    ("montant_ht", "REAL DEFAULT 0"),

    ("frais_port_ht", "REAL DEFAULT 0"),

    ("commentaire", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["achats_fournisseurs_lignes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("achat_id", "INTEGER"),

    # Peut être NULL si le produit n'existe pas encore dans
    # ton catalogue au moment de la commande fournisseur.
    ("produit_id", "INTEGER"),

    ("nom_produit", "TEXT"),

    ("quantite", "INTEGER DEFAULT 1"),

    ("prix_unitaire_ht", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

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
SCHEMA["budget_publicitaire_canaux"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("ligne_id", "INTEGER"),

    ("canal_id", "INTEGER"),

    # Permet de lier un canal à une ligne de budget (ex :
    # Amazon FBA + FBM tous les deux liés à "Amazon Ads")
    # sans forcément les compter tous les deux tout de suite
    # — décoche celui pas encore utilisé, coche-le le jour
    # où tu t'en sers vraiment.
    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["periodes_commerciales"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    ("date_debut", "TEXT"),
    ("date_fin", "TEXT"),

    # Budget EN PLUS de ce qui est déjà dépensé sur les
    # lignes habituelles pendant cette période (ex : un
    # coup de pouce pour Noël, en plus du budget normal de
    # Google Shopping ce mois-là).
    ("budget_supplementaire_ht", "REAL DEFAULT 0"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["budget_publicitaire_lignes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    # Enveloppe totale HT prévue pour toute la période
    # (ex : 5040€ pour Google Shopping sur les 15 mois du
    # 1er exercice).
    ("enveloppe_totale_ht", "REAL"),

    ("date_debut", "TEXT"),
    ("date_fin", "TEXT"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["depenses_publicitaires"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("ligne_id", "INTEGER"),

    # Mois de la dépense réelle, format 'YYYY-MM' — saisi
    # librement, aucune répartition automatique imposée :
    # certains mois consomment plus (périodes commerciales
    # fortes), d'autres moins.
    ("mois", "TEXT"),

    ("montant_reel_ht", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["soldes_journaliers"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("date", "TEXT UNIQUE"),

    ("solde_ttc", "REAL"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["charges_recurrentes"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("nom", "TEXT"),

    # loyer / electricite / eau / abonnement / pret /
    # credit_tva / autre
    ("categorie", "TEXT DEFAULT 'autre'"),

    # 'mensuelle' (due chaque mois) ou 'annuelle' (due une
    # seule fois par an, le même mois que mois_debut).
    ("frequence", "TEXT DEFAULT 'mensuelle'"),

    # Certaines charges portent de la TVA récupérable
    # (loyer, électricité, abonnements...), d'autres non
    # (remboursement de prêt — capital et intérêts —, ou le
    # crédit relais TVA lui-même). Coché par défaut, à
    # décocher pour les charges concernées.
    ("tva_applicable", "INTEGER DEFAULT 1"),

    ("montant_mensuel", "REAL"),

    # Mois de première échéance, format 'YYYY-MM'.
    ("mois_debut", "TEXT"),

    # Nombre d'échéances au total. NULL = récurrent sans
    # fin (loyer, abonnements...). Un nombre précis pour un
    # prêt ou un crédit à durée déterminée (ex : 81 pour la
    # phase de remboursement du prêt, 6 pour le crédit TVA).
    ("nombre_occurrences", "INTEGER"),

    ("actif", "INTEGER DEFAULT 1")

]


SCHEMA["paiements_charges"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    ("charge_id", "INTEGER"),

    # Mois concerné par ce paiement, format 'YYYY-MM'.
    ("mois", "TEXT"),

    ("paye", "INTEGER DEFAULT 0"),

    ("date_paiement", "TEXT")

]


SCHEMA["renouvellement_stock"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Singleton : ajustement manuel libre (positif pour
    # ajouter une somme, négatif pour en retirer) — vient
    # s'ajouter au cumul automatique du coût d'achat de
    # chaque produit vendu (calculé en direct depuis les
    # commandes, jamais stocké ici).
    ("ajustement_manuel", "REAL DEFAULT 0")

]


SCHEMA["fonds_croissance"] = [

    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),

    # Singleton : une seule ligne, le montant cumulé actuel
    # de la cagnotte (30% du solde de départ + 5% du
    # bénéfice de chaque mois, versé une fois par mois).
    ("montant_actuel", "REAL DEFAULT 0"),

    # Dernier mois pour lequel la contribution mensuelle de
    # 5% du bénéfice a déjà été versée — évite de la
    # verser deux fois si le logiciel est relancé plusieurs
    # fois dans le même mois.
    ("dernier_mois_alimente", "TEXT"),

    # Distingue "jamais initialisé avec les 30% du solde de
    # départ" de "à 0€ mais déjà initialisé" — un simple
    # test sur montant_actuel==0 se trompait si la
    # cotisation mensuelle de 5% arrivait avant la toute
    # première saisie de solde.
    ("initialise", "INTEGER DEFAULT 0")

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