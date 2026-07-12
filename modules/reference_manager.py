from database.database import Database


class ReferenceManager:

    def __init__(self):

        self.db = Database()

    def tous(self, table, filtre_colonne=None, filtre_valeur=None):
        """
        Liste les lignes actives d'une table de référence.

        Sans filtre_colonne : toutes les lignes actives.

        Avec filtre_colonne et filtre_valeur=None :
        les lignes où cette colonne est vide (IS NULL).
        Utile par exemple pour les catégories internes
        Pop Licence (canal_id NULL).

        Avec filtre_colonne et filtre_valeur renseigné :
        les lignes où cette colonne vaut cette valeur.
        Utile par exemple pour les catégories d'un canal
        de vente précis (canal_id = X).
        """

        if filtre_colonne is None:

            return self.db.lire(
                f"""
                SELECT *
                FROM {table}
                WHERE actif = 1
                ORDER BY nom
                """
            )

        if filtre_valeur is None:

            return self.db.lire(
                f"""
                SELECT *
                FROM {table}
                WHERE actif = 1
                AND {filtre_colonne} IS NULL
                ORDER BY nom
                """
            )

        return self.db.lire(
            f"""
            SELECT *
            FROM {table}
            WHERE actif = 1
            AND {filtre_colonne} = ?
            ORDER BY nom
            """,
            (filtre_valeur,)
        )

    def obtenir(self, table, identifiant):

        return self.db.lire_un(
            f"""
            SELECT *
            FROM {table}
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        table,
        nom,
        description="",
        actif=True
    ):

        self.db.executer(
            f"""
            INSERT INTO {table}
            (
                nom,
                description,
                actif
            )
            VALUES
            (
                ?,
                ?,
                ?
            )
            """,
            (
                nom,
                description,
                1 if actif else 0
            )
        )

    def modifier(
        self,
        table,
        identifiant,
        nom,
        description,
        actif
    ):

        self.db.executer(
            f"""
            UPDATE {table}
            SET
                nom = ?,
                description = ?,
                actif = ?
            WHERE id = ?
            """,
            (
                nom,
                description,
                1 if actif else 0,
                identifiant
            )
        )

    def definir_champ(self, table, identifiant, colonne, valeur):
        """
        Modifie un seul champ précis d'une ligne, dans une
        table qui a des colonnes en plus du socle commun
        (nom/description/actif) — par exemple id_wizishop
        sur les Marques, sans avoir à dupliquer ajouter()/
        modifier() pour chaque champ spécifique à une seule
        table.
        """

        self.db.executer(
            f"""
            UPDATE {table}
            SET {colonne} = ?
            WHERE id = ?
            """,
            (valeur, identifiant)
        )

    def supprimer(
        self,
        table,
        identifiant
    ):

        self.db.executer(
            f"""
            UPDATE {table}
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )