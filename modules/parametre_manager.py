from database.database import Database


class ParametreManager:
    """
    Gère les réglages globaux du logiciel, stockés en
    base (table "parametres"), plutôt que codés en dur.

    Exemple : le seuil maximum de transport toléré avant
    qu'un produit soit signalé non recommandé sur un canal.
    """

    def __init__(self):

        self.db = Database()

    def obtenir(self, cle, valeur_defaut=None):

        ligne = self.db.lire_un(
            """
            SELECT valeur
            FROM parametres
            WHERE cle = ?
            """,
            (cle,)
        )

        if ligne is None:
            return valeur_defaut

        return ligne["valeur"]

    def obtenir_nombre(self, cle, valeur_defaut=None):

        valeur = self.obtenir(cle)

        if valeur is None:
            return valeur_defaut

        try:
            return float(valeur)
        except ValueError:
            return valeur_defaut

    def definir(self, cle, valeur, description=""):

        existe = self.db.lire_un(
            """
            SELECT id
            FROM parametres
            WHERE cle = ?
            """,
            (cle,)
        )

        if existe is not None:

            self.db.executer(
                """
                UPDATE parametres
                SET valeur = ?
                WHERE cle = ?
                """,
                (str(valeur), cle)
            )

        else:

            self.db.executer(
                """
                INSERT INTO parametres
                (cle, valeur, description)
                VALUES (?, ?, ?)
                """,
                (cle, str(valeur), description)
            )