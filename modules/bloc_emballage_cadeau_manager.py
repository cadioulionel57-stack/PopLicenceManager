from database.database import Database


class BlocEmballageCadeauManager:
    """
    Gère le bloc HTML réutilisable "Produit éligible à
    l'emballage cadeau" — un seul exemplaire, modifiable une
    fois pour toutes, inséré automatiquement dans toutes les
    fiches Stock où le produit est coché éligible.
    """

    def __init__(self):

        self.db = Database()

    def obtenir(self):

        ligne = self.db.lire_un(
            """
            SELECT * FROM bloc_emballage_cadeau LIMIT 1
            """
        )

        if ligne is None:
            return ""

        return ligne["html_template"] or ""

    def definir(self, html_template):

        ligne = self.db.lire_un(
            """
            SELECT id FROM bloc_emballage_cadeau LIMIT 1
            """
        )

        if ligne is None:

            self.db.executer(
                """
                INSERT INTO bloc_emballage_cadeau (html_template)
                VALUES (?)
                """,
                (html_template,)
            )

        else:

            self.db.executer(
                """
                UPDATE bloc_emballage_cadeau
                SET html_template = ?
                WHERE id = ?
                """,
                (html_template, ligne["id"])
            )