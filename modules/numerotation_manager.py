from database.database import Database


class NumerotationManager:

    def __init__(self):

        self.db = Database()

    def obtenir(self, code):

        return self.db.lire_un(
            """
            SELECT *
            FROM numerotations
            WHERE code = ?
            """,
            (code,)
        )

    def initialiser(self):

        numerotations = [

            ("SKU_STOCK", "S"),
            ("SKU_DROP", "D"),
            ("SKU_BUNDLE", "B"),
            ("SKU_PRECO", "P"),

            ("CMD", "CMD"),
            ("ACH", "ACH"),
            ("SAV", "SAV"),
            ("FAC", "FAC")

        ]

        for code, prefixe in numerotations:

            existe = self.obtenir(code)

            if existe is None:

                self.db.executer(
                    """
                    INSERT INTO numerotations
                    (
                        code,
                        prefixe,
                        dernier_numero
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        0
                    )
                    """,
                    (
                        code,
                        prefixe
                    )
                )

    def apercu(self, code):

        numero = self.obtenir(code)

        if numero is None:
            raise Exception(f"Numérotation inconnue : {code}")

        prochain = numero["dernier_numero"] + 1

        return f"{numero['prefixe']}{prochain:0{numero['longueur']}d}"

    def generer(self, code):

        numero = self.obtenir(code)

        if numero is None:
            raise Exception(f"Numérotation inconnue : {code}")

        nouveau = numero["dernier_numero"] + 1

        self.db.executer(
            """
            UPDATE numerotations
            SET dernier_numero = ?
            WHERE code = ?
            """,
            (
                nouveau,
                code
            )
        )

        return f"{numero['prefixe']}{nouveau:0{numero['longueur']}d}"