from database.database import Database


class ListManager:

    def __init__(self):

        self.db = Database()

    def tous(self, table):

        return self.db.lire(
            f"SELECT * FROM {table} WHERE actif=1 ORDER BY nom"
        )

    def obtenir(self, table, identifiant):

        return self.db.lire_un(
            f"SELECT * FROM {table} WHERE id=?",
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
                nom=?,
                description=?,
                actif=?
            WHERE id=?
            """,
            (
                nom,
                description,
                1 if actif else 0,
                identifiant
            )
        )

    def supprimer(self, table, identifiant):

        self.db.executer(
            f"""
            UPDATE {table}
            SET actif=0
            WHERE id=?
            """,
            (identifiant,)
        )