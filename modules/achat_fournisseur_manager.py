from database.database import Database


class AchatFournisseurManager:
    """
    Gère les commandes passées à tes fournisseurs (achats de
    stock) — distinct des commandes clients.
    """

    def __init__(self):

        self.db = Database()

    def tous(self):

        return self.db.lire(
            """
            SELECT
                a.*,
                f.nom AS nom_fournisseur
            FROM achats_fournisseurs a

            LEFT JOIN fournisseurs f
                ON f.id = a.fournisseur_id

            WHERE a.actif = 1

            ORDER BY a.date_achat DESC
            """
        )

    def obtenir(self, identifiant):

        return self.db.lire_un(
            """
            SELECT *
            FROM achats_fournisseurs
            WHERE id = ?
            """,
            (identifiant,)
        )

    def ajouter(
        self,
        numero,
        fournisseur_id,
        date_achat,
        date_reception=None,
        statut="Commandé",
        montant_ht=0,
        frais_port_ht=0,
        commentaire=""
    ):

        curseur = self.db.executer(
            """
            INSERT INTO achats_fournisseurs
            (
                numero, fournisseur_id, date_achat, date_reception,
                statut, montant_ht, frais_port_ht, commentaire, actif
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, 1
            )
            """,
            (
                numero, fournisseur_id, date_achat, date_reception,
                statut, montant_ht, frais_port_ht, commentaire
            )
        )

        return curseur.lastrowid

    def modifier(
        self,
        identifiant,
        numero,
        fournisseur_id,
        date_achat,
        date_reception=None,
        statut="Commandé",
        montant_ht=0,
        frais_port_ht=0,
        commentaire=""
    ):

        self.db.executer(
            """
            UPDATE achats_fournisseurs
            SET
                numero = ?, fournisseur_id = ?, date_achat = ?,
                date_reception = ?, statut = ?, montant_ht = ?,
                frais_port_ht = ?, commentaire = ?
            WHERE id = ?
            """,
            (
                numero, fournisseur_id, date_achat, date_reception,
                statut, montant_ht, frais_port_ht, commentaire,
                identifiant
            )
        )

    def supprimer(self, identifiant):

        self.db.executer(
            """
            UPDATE achats_fournisseurs
            SET actif = 0
            WHERE id = ?
            """,
            (identifiant,)
        )

    ########################################################
    # Lignes (produits commandés)
    ########################################################

    def lignes(self, achat_id):

        return self.db.lire(
            """
            SELECT *
            FROM achats_fournisseurs_lignes
            WHERE achat_id = ?
            AND actif = 1
            ORDER BY id
            """,
            (achat_id,)
        )

    def definir_lignes(self, achat_id, lignes):
        """
        Remplace toutes les lignes d'un achat — même
        principe que pour les commandes clients.
        """

        self.db.executer(
            """
            UPDATE achats_fournisseurs_lignes
            SET actif = 0
            WHERE achat_id = ?
            """,
            (achat_id,)
        )

        for ligne in lignes:

            self.db.executer(
                """
                INSERT INTO achats_fournisseurs_lignes
                (
                    achat_id, produit_id, nom_produit,
                    quantite, prix_unitaire_ht, actif
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, 1
                )
                """,
                (
                    achat_id,
                    ligne.get("produit_id"),
                    ligne.get("nom_produit"),
                    ligne.get("quantite", 1),
                    ligne.get("prix_unitaire_ht"),
                )
            )