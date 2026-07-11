from database.database import Database


class EmballageCadeauManager:
    """
    Gère la grille des emballages cadeau : les codes
    "principaux" (facturés au client, tarif fixe quel que
    soit le code choisi) et les codes "supplément" (jamais
    facturés, juste un coût en plus).
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM grille_emballage_cadeau
            WHERE actif = 1
            ORDER BY type, nom
            """
        )

    def principaux(self):
        """
        Les codes facturés au client (choix visible sur la
        commande).
        """

        return self.db.lire(
            """
            SELECT *
            FROM grille_emballage_cadeau
            WHERE actif = 1
            AND type = 'principal'
            ORDER BY nom
            """
        )

    def supplements(self):
        """
        Les codes jamais facturés, juste un coût en plus
        (papier de soie, étiquettes...).
        """

        return self.db.lire(
            """
            SELECT *
            FROM grille_emballage_cadeau
            WHERE actif = 1
            AND type = 'supplement'
            ORDER BY nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM grille_emballage_cadeau
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(self, code, nom, cout_ht, type_emballage, tarif_facture_ht=None):

        curseur = self.db.executer(
            """
            INSERT INTO grille_emballage_cadeau
            (code, nom, cout_ht, type, tarif_facture_ht, actif)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (code, nom, cout_ht, type_emballage, tarif_facture_ht)
        )

        return curseur.lastrowid

    def modifier(
        self, identifiant, code, nom, cout_ht, type_emballage,
        tarif_facture_ht=None
    ):

        self.db.executer(
            """
            UPDATE grille_emballage_cadeau
            SET
                code = ?,
                nom = ?,
                cout_ht = ?,
                type = ?,
                tarif_facture_ht = ?
            WHERE id = ?
            """,
            (
                code, nom, cout_ht, type_emballage,
                tarif_facture_ht, identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_emballage_cadeau
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )