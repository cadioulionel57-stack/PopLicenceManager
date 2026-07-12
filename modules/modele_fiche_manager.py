from database.database import Database


class ModeleFicheManager:
    """
    Gère les modèles de fiche produit (chartes HTML) par
    thème + type de produit (stock/dropshipping) — un seul
    actif à la fois par combinaison (le modèle
    "Automatique"), les autres (Noël, soldes...) restent en
    mémoire pour être réactivés plus tard sans avoir à les
    recréer.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                mfp.*,
                t.nom AS nom_theme
            FROM modeles_fiche_produit mfp

            LEFT JOIN themes_template t
                ON t.id = mfp.theme_id

            ORDER BY t.nom, mfp.type_produit, mfp.nom
            """
        )

    def pour_type(self, type_produit):
        """
        Tous les modèles disponibles pour un type de produit
        donné, avec le nom de leur thème — sert à peupler le
        menu déroulant de sélection directe sur la fiche
        produit (le mode "forcer un modèle précis").
        """

        return self.db.lire(
            """
            SELECT
                mfp.*,
                t.nom AS nom_theme
            FROM modeles_fiche_produit mfp

            LEFT JOIN themes_template t
                ON t.id = mfp.theme_id

            WHERE mfp.type_produit = ?

            ORDER BY t.nom, mfp.nom
            """,
            (type_produit,)
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )

    def obtenir_actif(self, theme_id, type_produit):
        """
        Le modèle actif ("Automatique") pour ce thème+type —
        celui utilisé par les produits qui n'ont pas de
        modèle forcé. None si aucun n'existe encore.
        """

        if theme_id is None:
            return None

        return self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE theme_id = ?
            AND type_produit = ?
            AND actif = 1
            """,
            (theme_id, type_produit)
        )

    def ajouter(self, nom, theme_id, type_produit, html_template):

        curseur = self.db.executer(
            """
            INSERT INTO modeles_fiche_produit
            (nom, theme_id, type_produit, html_template, actif)
            VALUES (?, ?, ?, ?, 0)
            """,
            (nom, theme_id, type_produit, html_template)
        )

        return curseur.lastrowid

    def modifier(
        self, identifiant, nom, theme_id, type_produit,
        html_template
    ):

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET nom = ?, theme_id = ?, type_produit = ?,
                html_template = ?
            WHERE id = ?
            """,
            (nom, theme_id, type_produit, html_template,
             identifiant)
        )

    def basculer_actif(self, identifiant):
        """
        Active ce modèle et désactive automatiquement tout
        autre modèle du même thème+type — un seul modèle
        "Automatique" à la fois. Bascule d'un coup tous les
        produits en mode "Automatique" de ce thème (ex :
        passer tout le thème "Vêtements" en mode Noël).
        """

        modele = self.obtenir(identifiant)

        if modele is None:
            return

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 0
            WHERE theme_id = ?
            AND type_produit = ?
            """,
            (modele["theme_id"], modele["type_produit"])
        )

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET actif = 1
            WHERE id = ?
            """,
            (identifiant,)
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            DELETE FROM modeles_fiche_produit
            WHERE id = ?
            """,
            (identifiant,)
        )