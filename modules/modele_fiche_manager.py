from database.database import Database


class ModeleFicheManager:
    """
    Gère les modèles de fiche produit (chartes HTML) par
    thème, chacun couvrant un ou plusieurs types de produit
    (stock, dropshipping, bundle, précommande) — un seul
    actif à la fois par thème pour chaque type qu'il couvre
    (le modèle "Automatique"), les autres (Noël, soldes...)
    restent en mémoire pour être réactivés plus tard sans
    avoir à les recréer.
    """

    TOUS_LES_TYPES = ["stock", "dropshipping", "bundle", "precommande"]

    def __init__(self):

        self.db = Database()

    def tous(self):

        modeles = self.db.lire(
            """
            SELECT
                mfp.*,
                t.nom AS nom_theme
            FROM modeles_fiche_produit mfp

            LEFT JOIN themes_template t
                ON t.id = mfp.theme_id

            ORDER BY t.nom, mfp.nom
            """
        )

        resultat = []

        for modele in modeles:

            ligne = dict(modele)
            ligne["types"] = self.types_du_modele(modele["id"])
            resultat.append(ligne)

        return resultat

    def types_du_modele(self, modele_id):
        """
        Liste des types de produit couverts par ce modèle
        (ex : ['stock', 'dropshipping']).
        """

        lignes = self.db.lire(
            """
            SELECT type_produit
            FROM modeles_fiche_types
            WHERE modele_id = ?
            """,
            (modele_id,)
        )

        return [l["type_produit"] for l in lignes]

    def definir_types(self, modele_id, types_liste):
        """
        Remplace entièrement les types couverts par ce
        modèle.
        """

        self.db.executer(
            """
            DELETE FROM modeles_fiche_types
            WHERE modele_id = ?
            """,
            (modele_id,)
        )

        for type_produit in types_liste:

            self.db.executer(
                """
                INSERT INTO modeles_fiche_types
                (modele_id, type_produit)
                VALUES (?, ?)
                """,
                (modele_id, type_produit)
            )

    def actifs_pour_type(self, type_produit):
        """
        Uniquement les modèles actuellement "Actif" qui
        couvrent ce type de produit — sert à peupler le menu
        déroulant unique de la fiche produit (tu choisis
        directement parmi les actifs, pas de champ "Thème"
        séparé à gérer).
        """

        return self.db.lire(
            """
            SELECT DISTINCT
                mfp.*,
                t.nom AS nom_theme
            FROM modeles_fiche_produit mfp

            INNER JOIN modeles_fiche_types mft
                ON mft.modele_id = mfp.id
                AND mft.type_produit = ?

            LEFT JOIN themes_template t
                ON t.id = mfp.theme_id

            WHERE mfp.actif = 1

            ORDER BY t.nom, mfp.nom
            """,
            (type_produit,)
        )

    def pour_type(self, type_produit):
        """
        Tous les modèles couvrant ce type de produit — sert
        à peupler le menu déroulant de sélection directe sur
        la fiche produit (le mode "forcer un modèle précis").
        """

        modeles = self.db.lire(
            """
            SELECT DISTINCT
                mfp.*,
                t.nom AS nom_theme
            FROM modeles_fiche_produit mfp

            INNER JOIN modeles_fiche_types mft
                ON mft.modele_id = mfp.id
                AND mft.type_produit = ?

            LEFT JOIN themes_template t
                ON t.id = mfp.theme_id

            ORDER BY t.nom, mfp.nom
            """,
            (type_produit,)
        )

        return modeles

    def obtenir(self, identifiant):

        modele = self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )

        if modele is None:
            return None

        ligne = dict(modele)
        ligne["types"] = self.types_du_modele(identifiant)

        return ligne

    def obtenir_actif(self, theme_id, type_produit):
        """
        Le modèle actif ("Automatique") pour ce thème, parmi
        ceux qui couvrent ce type de produit précis. None si
        aucun n'existe.
        """

        if theme_id is None:
            return None

        return self.db.lire_un(
            """
            SELECT mfp.*
            FROM modeles_fiche_produit mfp

            INNER JOIN modeles_fiche_types mft
                ON mft.modele_id = mfp.id
                AND mft.type_produit = ?

            WHERE mfp.theme_id = ?
            AND mfp.actif = 1
            """,
            (type_produit, theme_id)
        )

    def ajouter(
        self, nom, theme_id, types_liste, html_template,
        types_articles_concernes=""
    ):

        curseur = self.db.executer(
            """
            INSERT INTO modeles_fiche_produit
            (nom, theme_id, html_template,
             types_articles_concernes, actif)
            VALUES (?, ?, ?, ?, 0)
            """,
            (nom, theme_id, html_template, types_articles_concernes)
        )

        modele_id = curseur.lastrowid

        self.definir_types(modele_id, types_liste)

        return modele_id

    def modifier(
        self, identifiant, nom, theme_id, types_liste,
        html_template, types_articles_concernes=""
    ):

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET nom = ?, theme_id = ?, html_template = ?,
                types_articles_concernes = ?
            WHERE id = ?
            """,
            (nom, theme_id, html_template, types_articles_concernes,
             identifiant)
        )

        self.definir_types(identifiant, types_liste)

    def basculer_actif(self, identifiant):
        """
        Active ce modèle — et seulement celui-ci. Ne désactive
        plus les autres modèles du même thème : plusieurs
        modèles peuvent désormais être actifs en même temps
        pour un même thème+type, pour apparaître tous ensemble
        dans la liste déroulante "Modèle de fiche" côté fiche
        produit (choix manuel, produit par produit).

        Avant, cocher un modèle décochait automatiquement les
        autres du même thème (pensé pour une bascule
        saisonnière automatique appliquée à tous les produits
        d'un coup) — ce comportement ne correspond plus à
        l'usage réel : décision actée de repasser en sélection
        manuelle libre.
        """

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 1
            WHERE id = ?
            """,
            (identifiant,)
        )

    def desactiver(self, identifiant):
        """
        Désactive ce modèle directement, sans qu'un autre
        n'ait besoin de prendre sa place — un thème+type
        peut donc temporairement n'avoir aucun modèle actif.
        """

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            DELETE FROM modeles_fiche_types
            WHERE modele_id = ?
            """,
            (identifiant,)
        )

        self.db.executer(
            """
            DELETE FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )