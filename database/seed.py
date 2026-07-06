from database.database import Database


class Seeder:

    def __init__(self):

        self.db = Database()

    def executer(self):

        self._seed_tva()

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