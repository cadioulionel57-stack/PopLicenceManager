from database.database import Database


class ModeleFicheManager:
    """
    Gère les modèles de fiche produit (chartes HTML) par
    thème + type de produit (stock/dropshipping/les_deux) —
    un seul actif à la fois par thème+type effectif (le
    modèle "Automatique"), les autres (Noël, soldes...)
    restent en mémoire pour être réactivés plus tard sans
    avoir à les recréer.
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
        donné — inclut ceux propres à ce type ET ceux marqués
        "les_deux". Sert à peupler le menu déroulant de
        sélection directe sur la fiche produit (le mode
        "forcer un modèle précis").
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
            OR mfp.type_produit = 'les_deux'

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
        modèle forcé. Un modèle propre à ce type précis
        (stock ou dropshipping) est toujours prioritaire sur
        un modèle "les_deux" actif en même temps — ça permet
        à un modèle "les_deux" (Noël) de continuer à couvrir
        le Direct Fournisseur même si on réactive entre-temps
        un modèle "stock" normal, sans qu'ils s'excluent
        mutuellement. None si aucun des deux n'existe.
        """

        if theme_id is None:
            return None

        specifique = self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE theme_id = ?
            AND type_produit = ?
            AND actif = 1
            """,
            (theme_id, type_produit)
        )

        if specifique is not None:
            return specifique

        return self.db.lire_un(
            """
            SELECT *
            FROM modeles_fiche_produit
            WHERE theme_id = ?
            AND type_produit = 'les_deux'
            AND actif = 1
            """,
            (theme_id,)
        )

    def ajouter(
        self, nom, theme_id, type_produit, html_template,
        types_articles_concernes=""
    ):

        curseur = self.db.executer(
            """
            INSERT INTO modeles_fiche_produit
            (nom, theme_id, type_produit, html_template,
             types_articles_concernes, actif)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (nom, theme_id, type_produit, html_template,
             types_articles_concernes)
        )

        return curseur.lastrowid

    def modifier(
        self, identifiant, nom, theme_id, type_produit,
        html_template, types_articles_concernes=""
    ):

        self.db.executer(
            """
            UPDATE modeles_fiche_produit
            SET nom = ?, theme_id = ?, type_produit = ?,
                html_template = ?, types_articles_concernes = ?
            WHERE id = ?
            """,
            (nom, theme_id, type_produit, html_template,
             types_articles_concernes, identifiant)
        )

    def basculer_actif(self, identifiant):
        """
        Active ce modèle. La désactivation des autres suit
        une règle volontairement asymétrique :

        - Activer un modèle "les_deux" (Noël, soldes...)
          désactive TOUS les autres modèles du thème (stock,
          dropshipping, les_deux) — il prend le contrôle
          complet du thème, pour les deux types.
        - Activer un modèle "stock" ou "dropshipping" ne
          désactive que les autres modèles de ce même type
          précis — un modèle "les_deux" déjà actif reste
          actif pour l'autre type (ex : réactiver un modèle
          stock normal ne coupe pas la couverture Direct
          Fournisseur d'un Noël toujours en place).

        C'est obtenir_actif() qui donne ensuite la priorité
        au modèle le plus spécifique (stock/dropshipping)
        sur un "les_deux" actif en même temps.
        """

        modele = self.obtenir(identifiant)

        if modele is None:
            return

        if modele["type_produit"] == "les_deux":

            self.db.executer(
                """
                UPDATE modeles_fiche_produit
                SET actif = 0
                WHERE theme_id = ?
                """,
                (modele["theme_id"],)
            )

        else:

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