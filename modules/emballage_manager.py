from database.database import Database


class EmballageManager:
    """
    Gère la grille d'emballages (pochettes, cartons...)
    utilisée pour calculer automatiquement le coût
    d'emballage d'un produit, selon la famille à laquelle
    il appartient.

    Rien n'est figé : la grille est entièrement modifiable
    depuis l'interface.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM grille_emballage
            WHERE actif = 1
            ORDER BY longueur_ext_cm * largeur_ext_cm * hauteur_ext_cm
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM grille_emballage
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        code,
        nom,
        longueur_ext_cm,
        largeur_ext_cm,
        hauteur_ext_cm,
        poids_g,
        cout_ht,
        calage_ht,
    ):

        curseur = self.db.executer(
            """
            INSERT INTO grille_emballage
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        code,
        nom,
        longueur_ext_cm,
        largeur_ext_cm,
        hauteur_ext_cm,
        poids_g,
        cout_ht,
        calage_ht,
    ):

        self.db.executer(
            """
            UPDATE grille_emballage
            SET
                code = ?,
                nom = ?,
                longueur_ext_cm = ?,
                largeur_ext_cm = ?,
                hauteur_ext_cm = ?,
                poids_g = ?,
                cout_ht = ?,
                calage_ht = ?
            WHERE id = ?
            """,
            (
                code,
                nom,
                longueur_ext_cm,
                largeur_ext_cm,
                hauteur_ext_cm,
                poids_g,
                cout_ht,
                calage_ht,
                identifiant,
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE grille_emballage
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    def cout_total(self, emballage_id):
        """
        Renvoie le coût total (emballage + calage) pour un
        emballage donné.
        """

        emballage = self.obtenir(emballage_id)

        if emballage is None:
            return 0

        return (emballage["cout_ht"] or 0) + (emballage["calage_ht"] or 0)