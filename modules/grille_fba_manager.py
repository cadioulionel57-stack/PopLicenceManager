from database.database import Database


class GrilleFbaManager:
    """
    Gère la grille tarifaire des frais de traitement FBA
    (Expédié par Amazon), basée sur le format de colis
    (déterminé par les dimensions du produit) et le poids.

    Contrairement à Boxtal (un tarif par tranche de poids),
    Amazon détermine d'abord le plus petit format de colis
    qui contient le produit, PUIS applique un tarif de base
    + un supplément par tranche de poids au-delà d'un seuil
    inclus dans ce format.

    Rien n'est figé : la grille est entièrement modifiable
    depuis l'interface, pour suivre les évolutions
    tarifaires d'Amazon (généralement 1 à 2 fois par an).
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM grille_fba
            WHERE actif = 1
            ORDER BY
                categorie_speciale IS NULL,
                categorie_speciale,
                longueur_max_cm * largeur_max_cm * hauteur_max_cm
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM grille_fba
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        format_colis,
        longueur_max_cm,
        largeur_max_cm,
        hauteur_max_cm,
        poids_seuil_g,
        prix_base_ht,
        prix_supplement_ht,
        supplement_pas_g,
        categorie_speciale=None,
    ):

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
                format_colis,
                categorie_speciale,
                longueur_max_cm,
                largeur_max_cm,
                hauteur_max_cm,
                poids_seuil_g,
                prix_base_ht,
                prix_supplement_ht,
                supplement_pas_g,
            )
        )

    def modifier(
        self,
        identifiant,
        format_colis,
        longueur_max_cm,
        largeur_max_cm,
        hauteur_max_cm,
        poids_seuil_g,
        prix_base_ht,
        prix_supplement_ht,
        supplement_pas_g,
        categorie_speciale=None,
    ):

        self.db.executer(
            """
            UPDATE grille_fba
            SET
                format_colis = ?,
                categorie_speciale = ?,
                longueur_max_cm = ?,
                largeur_max_cm = ?,
                hauteur_max_cm = ?,
                poids_seuil_g = ?,
                prix_base_ht = ?,
                prix_supplement_ht = ?,
                supplement_pas_g = ?
            WHERE id = ?
            """,
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
                identifiant,
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_fba
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def tarif(
        self,
        longueur_cm,
        largeur_cm,
        hauteur_cm,
        poids_g,
        categorie_speciale=None,
    ):
        """
        Détermine automatiquement le plus petit format de
        colis qui contient le produit (en triant ses 3
        dimensions pour ne pas dépendre de l'ordre saisi),
        puis calcule le prix pour son poids.

        Cherche d'abord dans la catégorie spéciale du
        produit si elle existe et a ses propres tarifs,
        sinon utilise la grille standard (categorie_speciale
        NULL).

        Renvoie {format_colis, prix_ht} ou None si aucun
        format ne convient (produit trop grand/lourd).
        """

        dimensions_produit = sorted(
            [longueur_cm or 0, largeur_cm or 0, hauteur_cm or 0],
            reverse=True
        )

        lignes = self._grille_applicable(categorie_speciale)

        for ligne in lignes:

            dimensions_format = sorted([
                ligne["longueur_max_cm"],
                ligne["largeur_max_cm"],
                ligne["hauteur_max_cm"],
            ], reverse=True)

            tient_dans_le_format = all(
                dimensions_produit[i] <= dimensions_format[i]
                for i in range(3)
            )

            if not tient_dans_le_format:
                continue

            if ligne["poids_seuil_g"] and poids_g > 0:

                if poids_g <= ligne["poids_seuil_g"]:
                    prix = ligne["prix_base_ht"]
                else:
                    import math

                    tranches = math.ceil(
                        (poids_g - ligne["poids_seuil_g"])
                        / ligne["supplement_pas_g"]
                    )
                    prix = (
                        ligne["prix_base_ht"]
                        + tranches * ligne["prix_supplement_ht"]
                    )
            else:
                prix = ligne["prix_base_ht"]

            return {
                "format_colis": ligne["format_colis"],
                "prix_ht": round(prix, 2),
            }

        return None

    def _grille_applicable(self, categorie_speciale):
        """
        Renvoie les lignes de la catégorie spéciale du
        produit si elle a des tarifs dédiés, sinon la
        grille standard.
        """

        if categorie_speciale:

            lignes_speciales = self.db.lire(
                """
                SELECT *
                FROM grille_fba
                WHERE actif = 1
                AND categorie_speciale = ?
                ORDER BY longueur_max_cm * largeur_max_cm * hauteur_max_cm
                """,
                (categorie_speciale,)
            )

            if lignes_speciales:
                return lignes_speciales

        return self.db.lire(
            """
            SELECT *
            FROM grille_fba
            WHERE actif = 1
            AND categorie_speciale IS NULL
            ORDER BY longueur_max_cm * largeur_max_cm * hauteur_max_cm
            """
        )