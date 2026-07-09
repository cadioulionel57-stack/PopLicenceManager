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