from database.database import Database


class CanalManager:
    """
    Gère les canaux de vente (WiziShop, Amazon FBM,
    Cdiscount, eBay, Leclerc, Rakuten, Fnac...).

    Rien n'est figé ici : un canal peut être ajouté,
    modifié ou désactivé librement depuis l'interface,
    avec ses propres règles (commission, frais fixe,
    port inclus ou non dans le prix affiché).
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT *
            FROM canaux_vente
            WHERE actif = 1
            ORDER BY ordre, nom
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM canaux_vente
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        nom,
        type_canal,
        commission_pourcentage=0,
        frais_fixe_ht=0,
        port_inclus=False,
        ordre=0
    ):

        self.db.executer(
            """
            INSERT INTO canaux_vente
            (
                nom,
                type,
                commission_pourcentage,
                frais_fixe_ht,
                port_inclus,
                ordre,
                actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                nom,
                type_canal,
                commission_pourcentage,
                frais_fixe_ht,
                1 if port_inclus else 0,
                ordre
            )
        )

    def modifier(
        self,
        identifiant,
        nom,
        type_canal,
        commission_pourcentage,
        frais_fixe_ht,
        port_inclus,
        ordre
    ):

        self.db.executer(
            """
            UPDATE canaux_vente
            SET
                nom = ?,
                type = ?,
                commission_pourcentage = ?,
                frais_fixe_ht = ?,
                port_inclus = ?,
                ordre = ?
            WHERE id = ?
            """,
            (
                nom,
                type_canal,
                commission_pourcentage,
                frais_fixe_ht,
                1 if port_inclus else 0,
                ordre,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE canaux_vente
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )