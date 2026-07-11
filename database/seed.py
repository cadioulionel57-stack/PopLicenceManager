from database.database import Database


class Seeder:

    def __init__(self):

        self.db = Database()

    def executer(self):

        self._seed_tva()
        self._seed_grille_transport()
        self._corriger_chronopost()
        self._seed_grille_fba()
        self._corriger_categories_fba()
        self._seed_grille_emballage()
        self._corriger_poids_max_emballage()
        self._corriger_type_emballage()
        self._corriger_regles_amazon_fbm()
        self._seed_fnac()
        self._corriger_categories_fnac()
        self._seed_cdiscount()
        self._corriger_mecanisme_cdiscount()
        self._seed_categories_cdiscount()
        self._seed_rakuten()
        self._seed_ebay()
        self._seed_emballage_cadeau()
        self._corriger_couleurs_canaux()
        self._corriger_contribution_ebay()

    def _corriger_categories_fba(self):
        """
        Ajoute automatiquement, une seule fois, les autres
        catégories qui partagent officiellement la même
        grille tarifaire FBA que "Linge de maison et
        tapis" (confirmé par le PDF tarifaire Amazon en
        vigueur au 1er février 2026, page 7 : ces 16
        catégories utilisent toutes le même tableau).

        Ne s'exécute que si "Vêtements et accessoires"
        n'existe pas encore dans la grille FBA.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM grille_fba
            WHERE categorie_speciale = 'Vêtements et accessoires'
            LIMIT 1
            """
        )

        if existe_deja is not None:
            return

        lignes_reference = self.db.lire(
            """
            SELECT *
            FROM grille_fba
            WHERE categorie_speciale = 'Linge de maison et tapis'
            """
        )

        if not lignes_reference:
            return

        autres_categories = [
            "Poussettes et articles de sécurité bébé",
            "Accessoires pour portes, fenêtres et douches",
            "Lunettes de protection",
            "Chaussures",
            "Accessoires de meubles",
            "Épicerie et gastronomie",
            "Adhésifs et colliers de serrage pour la maison",
            "Accessoires de bagages",
            "Matelas",
            "Matériel d'emballage",
            "Vêtements et alimentation pour animaux",
            "Accessoires pour imprimantes et scanners",
            "Gants de travail et de sécurité réutilisables",
            "Vêtements et accessoires",
            "Sacs à dos et sacs à main",
        ]

        for categorie in autres_categories:

            for ligne in lignes_reference:

                self.db.executer(
                    """
                    INSERT INTO grille_fba
                    (
                        format_colis,
                        categorie_speciale,
                        longueur_max_cm,
                        largeur_max_cm,
                        hauteur_max_cm,
                        poids_seuil_g,
                        prix_base_ht,
                        prix_supplement_ht,
                        supplement_pas_g,
                        actif
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
                    )
                    """,
                    (
                        ligne["format_colis"],
                        categorie,
                        ligne["longueur_max_cm"],
                        ligne["largeur_max_cm"],
                        ligne["hauteur_max_cm"],
                        ligne["poids_seuil_g"],
                        ligne["prix_base_ht"],
                        ligne["prix_supplement_ht"],
                        ligne["supplement_pas_g"],
                    )
                )

    def _seed_grille_emballage(self):
        """
        Pré-remplit la grille d'emballage avec les 6
        emballages définis par l'utilisateur (pochettes
        et cartons), leurs dimensions, poids, coût et
        calage moyen.

        Ne s'exécute que si la grille est encore vide.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM grille_emballage
            LIMIT 1
            """
        )

        if existe_deja is not None:
            return

        # (code, nom, L, l, h, poids_g, poids_max_g, cout_ht, calage_ht)
        emballages = [
            ("P1", "Pochette d'expédition S", 25, 20, 1, 20, 500, 0.16, 0.00),
            ("P2", "Pochette d'expédition M", 35, 25, 1, 35, 2000, 0.28, 0.00),
            ("C1", "Petit carton simple cannelure", 20, 15, 10, 120, 2000, 0.52, 0.08),
            ("C2", "Carton standard simple cannelure", 35, 25, 15, 260, 5000, 0.88, 0.12),
            ("C3", "Grand carton double cannelure", 45, 35, 20, 480, 10000, 1.34, 0.18),
            ("C4", "Très grand carton double cannelure", 60, 40, 30, 760, 20000, 2.08, 0.25),
        ]

        for (
            code, nom, l_max, larg_max, h_max,
            poids, poids_max, cout_ht, calage_ht
        ) in emballages:

            self.db.executer(
                """
                INSERT INTO grille_emballage
                (
                    code,
                    nom,
                    longueur_ext_cm,
                    largeur_ext_cm,
                    hauteur_ext_cm,
                    poids_g,
                    poids_max_g,
                    cout_ht,
                    calage_ht,
                    actif
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
                )
                """,
                (
                    code, nom, l_max, larg_max, h_max,
                    poids, poids_max, cout_ht, calage_ht
                )
            )

    def _corriger_poids_max_emballage(self):
        """
        Renseigne automatiquement, une seule fois, le poids
        maximum supporté par chacun des 6 emballages déjà
        existants dans la base (ajout de la colonne
        poids_max_g après leur création initiale).

        Ne touche que les lignes où poids_max_g est encore
        vide (NULL), pour ne jamais écraser une valeur que
        tu aurais déjà modifiée manuellement depuis
        l'interface.
        """

        poids_max_par_code = {
            "P1": 500,
            "P2": 2000,
            "C1": 2000,
            "C2": 5000,
            "C3": 10000,
            "C4": 20000,
        }

        for code, poids_max in poids_max_par_code.items():

            self.db.executer(
                """
                UPDATE grille_emballage
                SET poids_max_g = ?
                WHERE code = ?
                AND poids_max_g IS NULL
                """,
                (poids_max, code)
            )

    def _seed_grille_fba(self):
        """
        Pré-remplit la grille FBA avec les tarifs officiels
        de la catégorie "Linge de maison et tapis" (grille
        Amazon en vigueur au 1er février 2026) — la seule
        catégorie vérifiée avec certitude pour l'instant.

        D'autres catégories (Jouets, Vêtements...) ont
        potentiellement leurs propres tarifs à vérifier
        séparément avant de les ajouter.

        Ne s'exécute que si la grille est encore vide.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM grille_fba
            LIMIT 1
            """
        )

        if existe_deja is not None:
            return

        categorie = "Linge de maison et tapis"

        # (format, L_max, l_max, h_max, poids_seuil_g,
        #  prix_base_ht, prix_supplement_ht, pas_g)
        lignes = [
            ("Petit colis 1", 35, 25, 7, 100, 4.97, 0.03, 100),
            ("Petit colis 2", 35, 25, 9, 100, 5.01, 0.05, 100),
            ("Petit colis 3", 35, 25, 12, 100, 5.05, 0.08, 100),
            ("Colis moyen 1", 40, 30, 6, 100, 5.45, 0.08, 100),
            ("Colis moyen 2", 40, 30, 20, 100, 5.69, 0.08, 100),
            ("Grand colis 1", 45, 34, 10, 100, 6.16, 0.08, 100),
            ("Grand colis 2", 45, 34, 26, 100, 6.25, 0.08, 100),
        ]

        for (
            format_colis, l_max, larg_max, h_max,
            poids_seuil, prix_base, prix_supp, pas_g
        ) in lignes:

            self.db.executer(
                """
                INSERT INTO grille_fba
                (
                    format_colis,
                    categorie_speciale,
                    longueur_max_cm,
                    largeur_max_cm,
                    hauteur_max_cm,
                    poids_seuil_g,
                    prix_base_ht,
                    prix_supplement_ht,
                    supplement_pas_g,
                    actif
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, 1
                )
                """,
                (
                    format_colis, categorie, l_max, larg_max, h_max,
                    poids_seuil, prix_base, prix_supp, pas_g
                )
            )

    def _corriger_chronopost(self):
        """
        Corrige automatiquement, une seule fois, les
        tarifs Chronopost mal extraits lors du tout
        premier remplissage (Chrono 13 au lieu de Chrono
        Relais, mauvaises valeurs pour Chrono 18).

        Ne touche à rien d'autre : les autres transporteurs
        et toutes tes données produits/licences/etc. restent
        intacts.
        """

        ancienne_donnee_presente = self.db.lire_un(
            """
            SELECT id
            FROM grille_transport
            WHERE offre = 'Chrono 13'
            """
        )

        if ancienne_donnee_presente is None:
            return

        chronopost = self.db.lire_un(
            """
            SELECT id
            FROM transporteurs
            WHERE nom = 'Chronopost'
            """
        )

        if chronopost is None:
            return

        chronopost_id = chronopost["id"]

        self.db.executer(
            """
            DELETE FROM grille_transport
            WHERE transporteur_id = ?
            AND offre IN ('Chrono 13', 'Chrono 18')
            """,
            (chronopost_id,)
        )

        chrono_relais = [
            (0.25, 5.94), (0.5, 5.94), (1, 5.94),
            (2, 6.92), (3, 7.52), (5, 8.90),
            (7, 10.31), (10, 12.41), (15, 15.90),
            (20, 19.39),
        ]

        for poids_max_kg, prix_ht in chrono_relais:

            self.db.executer(
                """
                INSERT INTO grille_transport
                (transporteur_id, offre, poids_max_kg, prix_ht, actif)
                VALUES (?, 'Chrono Relais', ?, ?, 1)
                """,
                (chronopost_id, poids_max_kg, prix_ht)
            )

        chrono_18 = [
            (0.25, 8.69), (0.5, 8.69), (1, 8.69), (2, 8.69),
            (3, 11.40), (5, 11.40), (7, 13.91),
            (10, 14.98), (15, 16.93), (20, 18.90), (30, 22.82),
        ]

        for poids_max_kg, prix_ht in chrono_18:

            self.db.executer(
                """
                INSERT INTO grille_transport
                (transporteur_id, offre, poids_max_kg, prix_ht, actif)
                VALUES (?, 'Chrono 18', ?, ?, 1)
                """,
                (chronopost_id, poids_max_kg, prix_ht)
            )

    def _corriger_regles_amazon_fbm(self):
        """
        Renseigne automatiquement, une seule fois, la
        contribution transport minimale (2€ HT) et le prix
        de vente minimum recommandé (29€ TTC) sur le canal
        "Amazon FBM" — règles actées avec l'utilisateur.

        Ne touche que les lignes où ces deux champs sont
        encore à leur valeur neutre (0 ou NULL), pour ne
        jamais écraser une valeur déjà modifiée manuellement
        depuis l'écran "Canaux de vente".
        """

        self.db.executer(
            """
            UPDATE canaux_vente
            SET contribution_transport_min_ht = 2.0
            WHERE nom = 'Amazon FBM'
            AND (
                contribution_transport_min_ht IS NULL
                OR contribution_transport_min_ht = 0
            )
            """
        )

        self.db.executer(
            """
            UPDATE canaux_vente
            SET prix_vente_min_ttc = 29.0
            WHERE nom = 'Amazon FBM'
            AND prix_vente_min_ttc IS NULL
            """
        )

    def _corriger_categories_fnac(self):
        """
        Ajoute automatiquement, une seule fois, deux
        catégories Fnac supplémentaires confirmées via les
        CGV officielles Fnac Marketplace : Bagagerie (14%,
        grille "Sports & Loisirs, bagagerie") et Décoration
        (15%, grille "maison & lifestyle").

        Ne s'exécute que si le canal Fnac existe déjà, et
        n'ajoute que les catégories qui n'existent pas
        encore pour ce canal (jamais de doublon).
        """

        fnac = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'Fnac'
            """
        )

        if fnac is None:
            return

        fnac_id = fnac["id"]

        nouvelles_categories = [
            ("Bagagerie", 14.0),
            ("Décoration", 15.0),
        ]

        for nom, commission in nouvelles_categories:

            existe = self.db.lire_un(
                """
                SELECT id
                FROM categories
                WHERE nom = ?
                AND canal_id = ?
                """,
                (nom, fnac_id)
            )

            if existe is None:

                self.db.executer(
                    """
                    INSERT INTO categories
                    (nom, canal_id, commission_pourcentage, actif)
                    VALUES (?, ?, ?, 1)
                    """,
                    (nom, fnac_id, commission)
                )

    def _seed_cdiscount(self):
        """
        Crée le canal Cdiscount, une seule fois :
        - commission flat 15% (aucune catégorie de ton
          catalogue n'a de taux spécifique dans la grille
          officielle Cdiscount — tout tombe dans "Toutes
          catégories") ;
        - port_inclus=1, sur le même principe que FBA : le
          coût réel du Point Relais (Mondial Relay) est
          intégré au prix produit, le client voit "livraison
          gratuite" en point relais. Les options payantes
          (Colissimo, Chrono Relais) sont gérées côté
          Cdiscount lui-même, hors calcul de marge du
          logiciel, comme acté avec l'utilisateur ;
        - seul Mondial Relay/Point Relais est autorisé côté
          calcul de prix (le moins cher, cohérent avec la
          pratique observée chez les vendeurs indépendants
          Cdiscount).

        Ne s'exécute que si "Cdiscount" n'existe pas déjà.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'Cdiscount'
            """
        )

        if existe_deja is not None:
            return

        mondial_relay_id = self._obtenir_ou_creer_transporteur(
            "Mondial Relay"
        )

        curseur = self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                port_inclus,
                grille_tarif_client_active,
                utilise_grille_fba,
                ordre,
                actif
            )
            VALUES
            (
                'Cdiscount', 'marketplace', 15, 0, 0, 0, 0, 1, 0, 0, 0, 1
            )
            """
        )

        cdiscount_id = curseur.lastrowid

        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, actif)
            VALUES (?, ?, 'Point Relais', 1)
            """,
            (cdiscount_id, mondial_relay_id)
        )

    def _seed_categories_cdiscount(self):
        """
        Crée les 3 catégories Cdiscount validées avec
        l'utilisateur, taux "produits neufs" de la grille
        officielle CGV Cdiscount :

        - "Toutes catégories (hors liste ci-dessous)" 15%,
          la catégorie par défaut pour l'essentiel du
          catalogue (jouets, figurines, textile, décoration,
          bagagerie, maroquinerie...) ;
        - "Maison" 17%, pour le linge de maison (coussins,
          parures de lit, oreillers, taies) ;
        - "Mode - Montres" 16%, pour les montres.

        Toutes les autres catégories de la grille officielle
        (bijoux, électroménager, vin, pneus, parapharmacie...)
        ont été explicitement écartées avec l'utilisateur,
        car sans rapport avec son activité — ne pas les
        rajouter sans revalidation.

        Ne s'exécute que si le canal Cdiscount existe, et
        n'ajoute que les catégories qui n'existent pas
        encore (jamais de doublon).
        """

        cdiscount = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'Cdiscount'
            """
        )

        if cdiscount is None:
            return

        cdiscount_id = cdiscount["id"]

        categories_validees = [
            ("Toutes catégories (hors liste ci-dessous)", 15.0),
            ("Maison", 17.0),
            ("Mode - Montres", 16.0),
        ]

        for nom, commission in categories_validees:

            existe = self.db.lire_un(
                """
                SELECT id
                FROM categories
                WHERE nom = ?
                AND canal_id = ?
                """,
                (nom, cdiscount_id)
            )

            if existe is None:

                self.db.executer(
                    """
                    INSERT INTO categories
                    (nom, canal_id, commission_pourcentage, actif)
                    VALUES (?, ?, ?, 1)
                    """,
                    (nom, cdiscount_id, commission)
                )

    def _corriger_mecanisme_cdiscount(self):
        """
        CORRECTIF : le canal Cdiscount avait été codé avec
        le mécanisme "port inclus" (coût réel complet du
        transport absorbé, variable selon le poids — celui
        de FBA), alors que la demande initiale était une
        contribution FIXE de 3,49€ HT par produit, peu
        importe le poids réel — exactement le même principe
        qu'Amazon FBM et Rakuten.

        Corrige : port_inclus désactivé, contribution
        transport fixe à 3,49€ HT, port affiché au client à
        0€ (gratuit). Les options payantes Colissimo (4,79€
        TTC) et Chrono Relais (10,45€ TTC) restent gérées
        directement dans les paramètres vendeur Cdiscount,
        hors calcul de marge du logiciel — comme pour
        l'option Colissimo Suivi sur Rakuten.

        Ne s'exécute que si le canal Cdiscount existe, et ne
        touche que les lignes où la contribution est encore
        à 0 (valeur jamais modifiée depuis), pour ne pas
        écraser un réglage que tu aurais déjà changé toi-même
        après cette correction.
        """

        self.db.executer(
            """
            UPDATE canaux_vente
            SET
                port_inclus = 0,
                contribution_transport_min_ht = 3.49,
                tarif_port_client_ttc = 0
            WHERE nom = 'Cdiscount'
            AND (
                contribution_transport_min_ht IS NULL
                OR contribution_transport_min_ht = 0
            )
            """
        )

        # Seuil de prix minimum recommandé (25€ TTC, observé
        # en comparant la marge Cdiscount à celle des autres
        # canaux) — même mécanisme que les 29€ d'Amazon FBM.
        self.db.executer(
            """
            UPDATE canaux_vente
            SET prix_vente_min_ttc = 25.0
            WHERE nom = 'Cdiscount'
            AND prix_vente_min_ttc IS NULL
            """
        )

    def _corriger_contribution_ebay(self):
        """
        CORRECTIF : la contribution transport eBay avait été
        actée à 3,79€ HT dans un premier temps, puis
        ajustée à 2,79€ HT (achat de l'étiquette Mondial
        Relay directement via eBay, moins cher que via
        Boxtal).

        Corrige si la valeur est encore à l'ancien montant
        (3,79) OU si elle est restée à 0/NULL (cas où le
        canal eBay avait été créé avant que cette valeur ne
        soit actée). Si tu as toi-même mis une autre valeur
        depuis, ce correctif ne la touche pas.
        """

        self.db.executer(
            """
            UPDATE canaux_vente
            SET contribution_transport_min_ht = 2.79
            WHERE nom = 'eBay'
            AND (
                contribution_transport_min_ht = 3.79
                OR contribution_transport_min_ht IS NULL
                OR contribution_transport_min_ht = 0
            )
            """
        )

    def _seed_emballage_cadeau(self):
        """
        Crée la grille des emballages cadeau, une seule
        fois : 8 codes "principaux" (le client paie toujours
        2,42€ HT, quel que soit celui choisi — seul le coût
        réel varie) et 5 codes "supplément" (jamais facturés,
        juste un coût en plus qui réduit la marge).

        Tous les coûts restent modifiables ensuite dans
        l'écran "Emballages Cadeau", au fil des évolutions de
        prix fournisseur.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM grille_emballage_cadeau
            LIMIT 1
            """
        )

        if existe_deja is not None:
            return

        TARIF_FACTURE = 2.42

        # (code, nom, cout_ht, type, tarif_facture_ht)
        codes = [
            ("EPKDO1", "Étiquette adhésive (plaisir d'offrir)", 0.01, "supplement", None),
            ("EPKDO2", "Étiquette adhésive (joyeux noël)", 0.01, "supplement", None),
            ("CKDO1", "Étiquette adhésive (joyeux anniversaire)", 0.01, "supplement", None),
            ("CKDO2", "Boîte pliable pelliculée blanc", 0.43, "principal", TARIF_FACTURE),
            ("BBKDO", "Boîte berlingot 20x33x7", 1.59, "principal", TARIF_FACTURE),
            ("POCKDO", "Boîte cadeau pliable 20x14x5", 0.72, "principal", TARIF_FACTURE),
            ("PPKDO", "Emballage papier cadeau (rouleau)", 1.50, "principal", TARIF_FACTURE),
            ("BOPKDO", "Boîte cadeau noire (20,7x3x3,7)", 1.44, "principal", TARIF_FACTURE),
            ("PBSB", "Papier soie blanc", 0.04, "supplement", None),
            ("PMSM", "Papier soie mauve", 0.05, "supplement", None),
            ("POCKDO1", "Pochette cadeau polypro", 0.51, "principal", TARIF_FACTURE),
            ("POCKDO2", "Pochette cadeau craft", 0.94, "principal", TARIF_FACTURE),
        ]

        for code, nom, cout_ht, type_emballage, tarif_facture in codes:

            self.db.executer(
                """
                INSERT INTO grille_emballage_cadeau
                (code, nom, cout_ht, type, tarif_facture_ht, actif)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (code, nom, cout_ht, type_emballage, tarif_facture)
            )

    def _corriger_couleurs_canaux(self):
        """
        Attribue une couleur distincte à chaque canal connu,
        pour les repérer d'un coup d'œil dans l'onglet
        Tarification — sans ça, tous partageraient la même
        couleur par défaut.

        Ne touche que les canaux encore à la couleur par
        défaut (#144b8b), pour ne jamais écraser une couleur
        que tu aurais choisie toi-même depuis l'écran Canaux
        de vente.
        """

        couleurs = {
            "Amazon FBA": "#ff9900",
            "Amazon FBM": "#cc7a00",
            "Cdiscount": "#e2001a",
            "Fnac": "#eaba00",
            "Rakuten": "#bf0000",
            "eBay": "#0064d2",
            "Leclerc Marketplace": "#0057a8",
            "Site+Drop": "#1e7d32",
        }

        for nom, couleur in couleurs.items():

            self.db.executer(
                """
                UPDATE canaux_vente
                SET couleur = ?
                WHERE nom = ?
                AND (couleur IS NULL OR couleur = '#144b8b')
                """,
                (couleur, nom)
            )

    def _seed_ebay(self):
        """
        Crée le canal eBay au complet, une seule fois :

        - le canal : pas de frais de paiement PayPal séparé
          (eBay Managed Payments les inclut déjà dans la
          commission), 0,35€ HT fixe par commande, 0,35% de
          frais d'exploitation réglementaires (modélisés via
          frais_paiement_pourcentage, mécaniquement identique
          — un pourcentage du TTC déduit de la marge) ;
        - contribution transport 3,79€ HT intégrée (Mondial
          Relay, seul transporteur sous contrat), port
          affiché au client à 0€ ("gratuit") ;
        - 4 catégories validées, dont 2 à paliers de prix
          (9%/2% et 12%/2% au-delà de 990€, comme les paliers
          déjà utilisés pour Amazon Vêtements).

        Colissimo domicile sans signature (4,90€ TTC) et
        Chrono Relais (7,90€ TTC) restent des options
        informatives, gérées côté paramètres vendeur eBay,
        hors calcul de marge du logiciel — même principe que
        Colissimo sur Rakuten et Cdiscount.

        Ne s'exécute que si "eBay" n'existe pas déjà.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'eBay'
            """
        )

        if existe_deja is not None:
            return

        curseur = self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                port_inclus,
                contribution_transport_min_ht,
                tarif_port_client_ttc,
                grille_tarif_client_active,
                utilise_grille_fba,
                ordre,
                actif
            )
            VALUES
            (
                'eBay', 'marketplace', 9, 0.35, 0.35, 0, 0,
                0, 2.79, 0, 0, 0, 0, 1
            )
            """
        )

        ebay_id = curseur.lastrowid

        # Catégories à taux flat
        categories_flat = [
            ("Mode (vêtements)", 12.0),
            ("Maison (déco, linge de maison)", 9.0),
        ]

        for nom, commission in categories_flat:

            self.db.executer(
                """
                INSERT INTO categories
                (nom, canal_id, commission_pourcentage, actif)
                VALUES (?, ?, ?, 1)
                """,
                (nom, ebay_id, commission)
            )

        # Catégories à paliers de prix (9%/2% et 12%/2%,
        # bascule à 990€)
        categories_paliers = [
            ("Collection (jouets, figurines)", 9.0),
            ("Sacs et bagagerie", 12.0),
        ]

        for nom, taux_principal in categories_paliers:

            curseur_cat = self.db.executer(
                """
                INSERT INTO categories
                (nom, canal_id, commission_pourcentage, actif)
                VALUES (?, ?, ?, 1)
                """,
                (nom, ebay_id, taux_principal)
            )

            categorie_id = curseur_cat.lastrowid

            self.db.executer(
                """
                INSERT INTO paliers_commission_categorie
                (categorie_id, seuil_prix_max, commission_pourcentage, ordre)
                VALUES (?, 990, ?, 0)
                """,
                (categorie_id, taux_principal)
            )

            self.db.executer(
                """
                INSERT INTO paliers_commission_categorie
                (categorie_id, seuil_prix_max, commission_pourcentage, ordre)
                VALUES (?, NULL, 2.0, 1)
                """,
                (categorie_id,)
            )

    def _seed_rakuten(self):
        """
        Crée le canal Rakuten au complet, une seule fois :

        - le canal (pack Expert : commission par catégorie,
          contribution transport 1,25€ HT intégrée à chaque
          produit, grille_tarif_client_active=1 pour la
          bascule automatique de transporteur selon le prix) ;
        - 2 catégories validées avec l'utilisateur ;
        - transport : Point Relais Mondial Relay en mode de
          base (≤200€, tarif client 3,99€ TTC), bascule
          automatique vers Chrono 18 (+200€, tarif client
          11,81€ TTC — obligation de signature Rakuten sur
          les commandes de cette valeur) ;
        - frais de gestion par palier de prix de vente
          (grille officielle Rakuten, 0,15€ à 5€).

        Le mode Colissimo Suivi (option intermédiaire
        proposée au client) n'est volontairement pas modélisé
        ici : il reste géré directement dans les paramètres
        vendeur Rakuten, hors calcul de marge du logiciel,
        comme validé avec l'utilisateur — ne pas l'ajouter
        sans revalidation, ça changerait le calcul de marge.

        L'abonnement mensuel (49€ HT, pack Expert) n'est pas
        inclus dans le coût produit : comme pour Amazon FBM,
        c'est un coût fixe mensuel, pas un coût par vente.

        Ne s'exécute que si "Rakuten" n'existe pas déjà.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'Rakuten'
            """
        )

        if existe_deja is not None:
            return

        mondial_relay_id = self._obtenir_ou_creer_transporteur(
            "Mondial Relay"
        )
        chronopost_id = self._obtenir_ou_creer_transporteur(
            "Chronopost"
        )

        curseur = self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                port_inclus,
                contribution_transport_min_ht,
                grille_tarif_client_active,
                utilise_grille_fba,
                ordre,
                actif
            )
            VALUES
            (
                'Rakuten', 'marketplace', 15, 0, 0, 0, 0, 0, 1.25, 1, 0, 0, 1
            )
            """
        )

        rakuten_id = curseur.lastrowid

        # Catégories validées avec l'utilisateur
        categories_rakuten = [
            ("Bricolage, jeux vidéo, livres, musique", 12.0),
            (
                "Papeterie, Mode, Jouets et puériculture, "
                "Décoration, Arts de la table, Linge de "
                "maison, Art et collection, Bijoux",
                15.0,
            ),
        ]

        for nom, commission in categories_rakuten:

            self.db.executer(
                """
                INSERT INTO categories
                (nom, canal_id, commission_pourcentage, actif)
                VALUES (?, ?, ?, 1)
                """,
                (nom, rakuten_id, commission)
            )

        # Éligibilité par tranche de prix
        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, prix_min_ttc, prix_max_ttc, actif)
            VALUES (?, ?, 'Point Relais', NULL, 200, 1)
            """,
            (rakuten_id, mondial_relay_id)
        )

        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, prix_min_ttc, prix_max_ttc, actif)
            VALUES (?, ?, 'Chrono 18', 200, NULL, 1)
            """,
            (rakuten_id, chronopost_id)
        )

        # Tarifs client (flat, sur tous les paliers de poids
        # existants pour ces offres dans grille_transport)
        poids_point_relais = [
            0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30
        ]
        poids_chrono_18 = [
            0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30
        ]

        for poids_max_kg in poids_point_relais:

            self.db.executer(
                """
                INSERT INTO grille_tarif_client
                (canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc, actif)
                VALUES (?, ?, 'Point Relais', ?, 3.99, 1)
                """,
                (rakuten_id, mondial_relay_id, poids_max_kg)
            )

        for poids_max_kg in poids_chrono_18:

            self.db.executer(
                """
                INSERT INTO grille_tarif_client
                (canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc, actif)
                VALUES (?, ?, 'Chrono 18', ?, 11.81, 1)
                """,
                (rakuten_id, chronopost_id, poids_max_kg)
            )

        # Frais de gestion par palier de prix (grille
        # officielle Rakuten)
        paliers_gestion = [
            (10, 0.15, 1),
            (50, 0.50, 2),
            (100, 1.00, 3),
            (200, 2.00, 4),
            (300, 3.00, 5),
            (400, 4.00, 6),
            (None, 5.00, 7),
        ]

        for seuil, montant, ordre in paliers_gestion:

            self.db.executer(
                """
                INSERT INTO paliers_frais_gestion
                (canal_id, seuil_prix_max, frais_gestion_ht, ordre)
                VALUES (?, ?, ?, ?)
                """,
                (rakuten_id, seuil, montant, ordre)
            )

    def _corriger_type_emballage(self):
        """
        Classe P1/P2 en "souple" (pochette, pas de marge de
        sécurité nécessaire) et C1-C4 en "rigide" (carton,
        marge +1cm nécessaire).

        Attention : contrairement aux autres corrections de
        ce fichier, celle-ci s'applique à chaque lancement
        du logiciel sur ces 6 codes précis — si tu modifies
        manuellement le type de P1, P2, C1, C2, C3 ou C4
        depuis l'interface, ce changement sera écrasé au
        prochain lancement. Pour tout nouvel emballage que tu
        crées toi-même (autre code), rien n'est touché ici.
        """

        souples = ["P1", "P2"]
        rigides = ["C1", "C2", "C3", "C4"]

        for code in souples:

            self.db.executer(
                """
                UPDATE grille_emballage
                SET type_emballage = 'souple'
                WHERE code = ?
                """,
                (code,)
            )

        for code in rigides:

            self.db.executer(
                """
                UPDATE grille_emballage
                SET type_emballage = 'rigide'
                WHERE code = ?
                """,
                (code,)
            )

    def _seed_fnac(self):
        """
        Crée le canal Fnac au complet, une seule fois :
        - le canal lui-même (grille_tarif_client_active=1,
          car le client choisit entre plusieurs transporteurs
          à des tarifs différents selon le poids) ;
        - les 4 catégories Fnac avec leurs commissions ;
        - le coût réel (Boxtal négocié) de Relais Colis et
          Colissimo Recommandé R1 dans grille_transport
          (Chrono 18 y est déjà, transporteur Chronopost) ;
        - le tarif facturé au client pour ces 3 offres, par
          tranche de poids, dans grille_tarif_client ;
        - l'éligibilité par tranche de prix de vente sur
          canaux_transporteurs (25€-200€ pour Relais Colis
          et Colissimo R1, +200€ pour Chrono 18 — sous 25€,
          rien n'est éligible : le produit est exclu de Fnac,
          conformément à la règle actée).

        Poids couverts : jusqu'à 5kg uniquement (poids max
        Fnac acté). Ne s'exécute que si "Fnac" n'existe pas
        déjà comme canal de vente.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM canaux_vente
            WHERE nom = 'Fnac'
            """
        )

        if existe_deja is not None:
            return

        colissimo_id = self._obtenir_ou_creer_transporteur(
            "Colissimo"
        )
        chronopost_id = self._obtenir_ou_creer_transporteur(
            "Chronopost"
        )
        relais_colis_id = self._obtenir_ou_creer_transporteur(
            "Relais Colis"
        )

        # (poids_max_kg, coût réel HT, tarif client TTC)
        grille_relais_colis = [
            (0.5, 3.33, 4.20),
            (1, 3.56, 4.50),
            (2, 5.06, 6.40),
            (3, 5.23, 6.60),
            (5, 7.40, 9.35),
        ]

        grille_colissimo_r1 = [
            (0.25, 7.73, 8.59),
            (0.5, 8.57, 10.69),
            (1, 10.15, 12.69),
            (2, 11.26, 14.29),
            (3, 12.24, 16.29),
            (5, 14.23, 20.49),
        ]

        # Chrono 18 : coût réel déjà présent dans
        # grille_transport (transporteur_id=chronopost_id,
        # offre="Chrono 18") — seul le tarif client est à
        # créer ici.
        grille_chrono_18_client = [
            (0.25, 9.90), (0.5, 9.90), (1, 9.90),
            (2, 9.90), (3, 11.90), (5, 11.90),
        ]

        for poids_max_kg, cout_ht, tarif_ttc in grille_relais_colis:

            self.db.executer(
                """
                INSERT INTO grille_transport
                (transporteur_id, offre, poids_max_kg, prix_ht, actif)
                VALUES (?, 'Relais Colis', ?, ?, 1)
                """,
                (relais_colis_id, poids_max_kg, cout_ht)
            )

        for poids_max_kg, cout_ht, tarif_ttc in grille_colissimo_r1:

            self.db.executer(
                """
                INSERT INTO grille_transport
                (transporteur_id, offre, poids_max_kg, prix_ht, actif)
                VALUES (?, 'Recommandé R1', ?, ?, 1)
                """,
                (colissimo_id, poids_max_kg, cout_ht)
            )

        # Canal Fnac
        curseur = self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                frais_paiement_pourcentage,
                frais_paiement_fixe_ht,
                taux_tsn_pourcentage,
                port_inclus,
                grille_tarif_client_active,
                utilise_grille_fba,
                ordre,
                actif
            )
            VALUES
            (
                'Fnac', 'marketplace', 12, 0, 0, 0, 0, 0, 1, 0, 0, 1
            )
            """
        )

        fnac_id = curseur.lastrowid

        # Catégories Fnac (commissions actées)
        categories_fnac = [
            ("Jeux, jouets, figurines", 12.0),
            ("Vêtements et diversification", 11.0),
            ("Papeterie", 14.0),
            ("Linge de maison", 15.0),
        ]

        for nom, commission in categories_fnac:

            self.db.executer(
                """
                INSERT INTO categories
                (nom, canal_id, commission_pourcentage, actif)
                VALUES (?, ?, ?, 1)
                """,
                (nom, fnac_id, commission)
            )

        # Éligibilité par tranche de prix (canaux_transporteurs)
        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, prix_min_ttc, prix_max_ttc, actif)
            VALUES (?, ?, 'Relais Colis', 25, 200, 1)
            """,
            (fnac_id, relais_colis_id)
        )

        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, prix_min_ttc, prix_max_ttc, actif)
            VALUES (?, ?, 'Recommandé R1', 25, 200, 1)
            """,
            (fnac_id, colissimo_id)
        )

        self.db.executer(
            """
            INSERT INTO canaux_transporteurs
            (canal_id, transporteur_id, offre, prix_min_ttc, prix_max_ttc, actif)
            VALUES (?, ?, 'Chrono 18', 200, NULL, 1)
            """,
            (fnac_id, chronopost_id)
        )

        # Tarifs client par poids (grille_tarif_client)
        for poids_max_kg, cout_ht, tarif_ttc in grille_relais_colis:

            self.db.executer(
                """
                INSERT INTO grille_tarif_client
                (canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc, actif)
                VALUES (?, ?, 'Relais Colis', ?, ?, 1)
                """,
                (fnac_id, relais_colis_id, poids_max_kg, tarif_ttc)
            )

        for poids_max_kg, cout_ht, tarif_ttc in grille_colissimo_r1:

            self.db.executer(
                """
                INSERT INTO grille_tarif_client
                (canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc, actif)
                VALUES (?, ?, 'Recommandé R1', ?, ?, 1)
                """,
                (fnac_id, colissimo_id, poids_max_kg, tarif_ttc)
            )

        for poids_max_kg, tarif_ttc in grille_chrono_18_client:

            self.db.executer(
                """
                INSERT INTO grille_tarif_client
                (canal_id, transporteur_id, offre, poids_max_kg, tarif_ttc, actif)
                VALUES (?, ?, 'Chrono 18', ?, ?, 1)
                """,
                (fnac_id, chronopost_id, poids_max_kg, tarif_ttc)
            )

    def _seed_tva(self):

        tvas = [

            ("20 %", 20.0),
            ("10 %", 10.0),
            ("5,5 %", 5.5),
            ("2,1 %", 2.1),
            ("0 %", 0.0),

        ]

        for nom, taux in tvas:

            existe = self.db.lire_un(
                """
                SELECT id
                FROM tva
                WHERE nom = ?
                """,
                (nom,)
            )

            if existe is None:

                self.db.executer(
                    """
                    INSERT INTO tva
                    (
                        nom,
                        taux,
                        actif
                    )
                    VALUES
                    (
                        ?, ?, 1
                    )
                    """,
                    (
                        nom,
                        taux
                    )
                )

    def _obtenir_ou_creer_transporteur(self, nom):

        existe = self.db.lire_un(
            """
            SELECT id
            FROM transporteurs
            WHERE nom = ?
            """,
            (nom,)
        )

        if existe is not None:
            return existe["id"]

        curseur = self.db.executer(
            """
            INSERT INTO transporteurs (nom, actif)
            VALUES (?, 1)
            """,
            (nom,)
        )

        return curseur.lastrowid

    def _seed_grille_transport(self):
        """
        Pré-remplit la grille tarifaire avec les tarifs
        Boxtal (France) pour les 4 offres utilisées par
        Pop Licence : Mondial Relay Point Relais, Colissimo
        Domicile Sans Signature, Chronopost Chrono 13 et
        Chrono 18.

        Ne s'exécute que si la grille est encore vide, pour
        ne jamais écraser une modification manuelle faite
        depuis l'interface.
        """

        existe_deja = self.db.lire_un(
            """
            SELECT id
            FROM grille_transport
            LIMIT 1
            """
        )

        if existe_deja is not None:
            return

        mondial_relay_id = self._obtenir_ou_creer_transporteur(
            "Mondial Relay"
        )
        colissimo_id = self._obtenir_ou_creer_transporteur(
            "Colissimo"
        )
        chronopost_id = self._obtenir_ou_creer_transporteur(
            "Chronopost"
        )

        # (poids_max_kg, prix_ht)
        grilles = {

            (mondial_relay_id, "Point Relais"): [
                (0.25, 3.04), (0.5, 3.14), (1, 3.51),
                (2, 4.90), (3, 5.21), (5, 9.44),
                (7, 10.36), (10, 10.36), (15, 16.16),
                (20, 16.26), (30, 18.60),
            ],

            (colissimo_id, "Domicile Sans Signature"): [
                (0.25, 6.70), (0.5, 7.54), (1, 9.13),
                (2, 10.24), (3, 11.22), (5, 13.21),
                (7, 14.79), (10, 17.70), (15, 22.14),
                (20, 26.89), (30, 36.05),
            ],

            (chronopost_id, "Chrono Relais"): [
                (0.25, 5.94), (0.5, 5.94), (1, 5.94),
                (2, 6.92), (3, 7.52), (5, 8.90),
                (7, 10.31), (10, 12.41), (15, 15.90),
                (20, 19.39),
            ],

            # Jusqu'à 2kg : offre "boîte aux lettres".
            # Au-delà : bascule sur le tarif poids
            # volumétrique (Chronopost facture au poids
            # volumétrique, pas au poids réel).
            (chronopost_id, "Chrono 18"): [
                (0.25, 8.69), (0.5, 8.69), (1, 8.69),
                (2, 8.69), (3, 11.40), (5, 11.40),
                (7, 13.91), (10, 14.98), (15, 16.93),
                (20, 18.90), (30, 22.82),
            ],

        }

        for (transporteur_id, offre), paliers in grilles.items():

            for poids_max_kg, prix_ht in paliers:

                self.db.executer(
                    """
                    INSERT INTO grille_transport
                    (
                        transporteur_id,
                        offre,
                        poids_max_kg,
                        prix_ht,
                        actif
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, 1
                    )
                    """,
                    (
                        transporteur_id,
                        offre,
                        poids_max_kg,
                        prix_ht
                    )
                )